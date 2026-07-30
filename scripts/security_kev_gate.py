#!/usr/bin/env python3
"""Correlate Trivy CVE findings with an exact, pinned CISA KEV snapshot."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

CVE_RE = re.compile(r"^CVE-\d{4}-\d{4,}$")
RECEIPT_SCHEMA = "asynqmon-security-catalog-receipt/v1"


class EvidenceError(ValueError):
    """Raised when security evidence is unavailable or malformed."""


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvidenceError(f"cannot read valid JSON from {path}: {exc}") from exc


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise EvidenceError(f"cannot hash {path}: {exc}") from exc
    return digest.hexdigest()


def parse_timestamp(value: str) -> dt.datetime:
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise EvidenceError(f"invalid receipt retrieved_at: {value}") from exc
    if parsed.tzinfo is None:
        raise EvidenceError("receipt retrieved_at must include a timezone")
    return parsed


def validate_catalog(
    catalog_path: Path, receipt_path: Path, max_age_days: int, now: dt.datetime
) -> tuple[dict[str, Any], set[str], str]:
    catalog = load_json(catalog_path)
    receipt = load_json(receipt_path)
    if not isinstance(catalog, dict) or not isinstance(receipt, dict):
        raise EvidenceError("catalog and receipt must be JSON objects")
    if receipt.get("schema") != RECEIPT_SCHEMA:
        raise EvidenceError("unsupported or missing KEV receipt schema")
    actual_sha = sha256(catalog_path)
    if receipt.get("sha256") != actual_sha:
        raise EvidenceError("KEV catalog SHA-256 does not match its receipt")
    retrieved_at = parse_timestamp(str(receipt.get("retrieved_at", "")))
    age = now.astimezone(dt.timezone.utc) - retrieved_at.astimezone(dt.timezone.utc)
    if age < dt.timedelta(0) or age > dt.timedelta(days=max_age_days):
        raise EvidenceError(
            f"KEV snapshot age {age} is outside the allowed {max_age_days} days"
        )
    vulnerabilities = catalog.get("vulnerabilities")
    if not isinstance(vulnerabilities, list) or catalog.get("count") != len(
        vulnerabilities
    ):
        raise EvidenceError("KEV catalog count does not match vulnerabilities")
    ids: set[str] = set()
    for item in vulnerabilities:
        if not isinstance(item, dict) or not CVE_RE.fullmatch(
            str(item.get("cveID", ""))
        ):
            raise EvidenceError("KEV catalog contains an invalid CVE record")
        cve_id = str(item["cveID"])
        if cve_id in ids:
            raise EvidenceError(f"KEV catalog contains duplicate {cve_id}")
        ids.add(cve_id)
    return catalog, ids, actual_sha


def trivy_findings(report: Any) -> list[dict[str, str]]:
    if not isinstance(report, dict) or not isinstance(report.get("Results"), list):
        raise EvidenceError("Trivy report is missing Results")
    findings: list[dict[str, str]] = []
    for result in report["Results"]:
        if not isinstance(result, dict):
            raise EvidenceError("Trivy Results must contain objects")
        target = str(result.get("Target", ""))
        vulnerabilities = result.get("Vulnerabilities") or []
        if not isinstance(vulnerabilities, list):
            raise EvidenceError("Trivy Vulnerabilities must be an array or null")
        for finding in vulnerabilities:
            if not isinstance(finding, dict):
                raise EvidenceError("Trivy vulnerability entry must be an object")
            advisory_id = str(finding.get("VulnerabilityID", ""))
            if not advisory_id:
                raise EvidenceError("Trivy vulnerability is missing VulnerabilityID")
            findings.append(
                {
                    "id": advisory_id,
                    "target": target,
                    "package": str(finding.get("PkgName", "")),
                    "installed_version": str(finding.get("InstalledVersion", "")),
                    "fixed_version": str(finding.get("FixedVersion", "")),
                    "severity": str(finding.get("Severity", "UNKNOWN")).upper(),
                }
            )
    return sorted(
        findings,
        key=lambda item: (
            item["id"],
            item["target"],
            item["package"],
            item["installed_version"],
        ),
    )


def correlate(
    report_path: Path,
    catalog_path: Path,
    receipt_path: Path,
    vex_path: Path | None,
    max_age_days: int,
    now: dt.datetime,
) -> tuple[dict[str, Any], bool]:
    catalog, kev_ids, catalog_sha = validate_catalog(
        catalog_path, receipt_path, max_age_days, now
    )
    findings = trivy_findings(load_json(report_path))
    exceptions: dict[tuple[str, str], dict[str, str]] = {}
    if vex_path is not None:
        vex = load_json(vex_path)
        if not isinstance(vex, dict) or vex.get("schema") != "asynqmon-vex/v1":
            raise EvidenceError("unsupported or missing VEX schema")
        statements = vex.get("statements")
        if not isinstance(statements, list):
            raise EvidenceError("VEX statements must be an array")
        for statement in statements:
            if not isinstance(statement, dict):
                raise EvidenceError("VEX statements must contain objects")
            advisory_id = str(statement.get("advisory_id", ""))
            package = str(statement.get("package", ""))
            status = str(statement.get("status", ""))
            justification = str(statement.get("justification", "")).strip()
            detail = str(statement.get("detail", "")).strip()
            if (
                not advisory_id
                or not package
                or status != "not_affected"
                or not justification
                or not detail
            ):
                raise EvidenceError("VEX statement is incomplete or has unsupported status")
            key = (advisory_id, package)
            if key in exceptions:
                raise EvidenceError(f"duplicate VEX statement for {advisory_id}/{package}")
            exceptions[key] = {
                "advisory_id": advisory_id,
                "package": package,
                "status": status,
                "justification": justification,
                "detail": detail,
            }
    cve_findings = [item for item in findings if CVE_RE.fullmatch(item["id"])]
    non_cve_findings = [item for item in findings if not CVE_RE.fullmatch(item["id"])]
    kev_matches = [item for item in cve_findings if item["id"] in kev_ids]
    waived_findings = [
        {**item, "vex": exceptions[(item["id"], item["package"])]}
        for item in findings
        if (item["id"], item["package"]) in exceptions
        and item["id"] not in kev_ids
    ]
    blocking_severities = [
        item for item in findings if item["severity"] in {"HIGH", "CRITICAL"}
        and (item["id"], item["package"]) not in exceptions
    ]
    output = {
        "schema": "asynqmon-cve-kev-correlation/v1",
        "result": "fail" if kev_matches or blocking_severities else "pass",
        "policy": {
            "block_severities": ["CRITICAL", "HIGH"],
            "block_any_kev_match": True,
            "max_kev_catalog_age_days": max_age_days,
        },
        "catalog": {
            "source": "CISA Known Exploited Vulnerabilities",
            "version": catalog.get("catalogVersion"),
            "date_released": catalog.get("dateReleased"),
            "count": catalog.get("count"),
            "sha256": catalog_sha,
            "completeness": "not-asserted-by-source-schema",
        },
        "summary": {
            "advisory_findings": len(findings),
            "cve_findings": len(cve_findings),
            "ignored_non_cve_findings": len(non_cve_findings),
            "vex_not_affected_findings": len(waived_findings),
            "blocking_severity_findings": len(blocking_severities),
            "kev_matches": len(kev_matches),
        },
        "blocking_severity_findings": blocking_severities,
        "vex_not_affected_findings": waived_findings,
        "kev_matches": kev_matches,
        "ignored_non_cve_ids": sorted({item["id"] for item in non_cve_findings}),
    }
    return output, bool(kev_matches or blocking_severities)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trivy-report", required=True, type=Path)
    parser.add_argument("--kev-catalog", required=True, type=Path)
    parser.add_argument("--kev-receipt", required=True, type=Path)
    parser.add_argument("--vex", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-catalog-age-days", type=int, default=7)
    args = parser.parse_args()
    if args.max_catalog_age_days < 1:
        print("security KEV gate: max catalog age must be positive", file=sys.stderr)
        return 2
    try:
        result, blocked = correlate(
            args.trivy_report,
            args.kev_catalog,
            args.kev_receipt,
            args.vex,
            args.max_catalog_age_days,
            dt.datetime.now(dt.timezone.utc),
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    except (EvidenceError, OSError) as exc:
        print(f"security KEV gate: evidence unavailable: {exc}", file=sys.stderr)
        return 2
    summary = result["summary"]
    print(
        "security KEV gate: "
        f"{result['result']} "
        f"(advisories={summary['advisory_findings']}, "
        f"high_or_critical={summary['blocking_severity_findings']}, "
        f"kev={summary['kev_matches']})"
    )
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
