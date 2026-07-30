#!/usr/bin/env python3
"""Correlate SAST, CycloneDX, vulnerability, KEV, and VEX evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from security_kev_gate import EvidenceError, load_json, validate_catalog
import datetime as dt


def component_index(sbom: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(sbom, dict) or sbom.get("bomFormat") != "CycloneDX":
        raise EvidenceError("SBOM is not CycloneDX")
    components = sbom.get("components")
    if not isinstance(components, list):
        raise EvidenceError("SBOM components must be an array")
    index: dict[str, dict[str, Any]] = {}
    for component in components:
        if not isinstance(component, dict):
            raise EvidenceError("SBOM component must be an object")
        ref = str(component.get("bom-ref", ""))
        if not ref or ref in index:
            raise EvidenceError("SBOM component refs must be non-empty and unique")
        index[ref] = {
            "bom_ref": ref,
            "name": str(component.get("name", "")),
            "version": str(component.get("version", "")),
            "purl": str(component.get("purl", "")),
        }
    return index


def vex_index(vex: Any) -> dict[tuple[str, str], dict[str, str]]:
    if not isinstance(vex, dict) or vex.get("schema") != "asynqmon-vex/v1":
        raise EvidenceError("unsupported or missing VEX schema")
    result: dict[tuple[str, str], dict[str, str]] = {}
    for item in vex.get("statements", []):
        if not isinstance(item, dict):
            raise EvidenceError("VEX statement must be an object")
        key = (str(item.get("advisory_id", "")), str(item.get("package", "")))
        if not all(key) or item.get("status") != "not_affected":
            raise EvidenceError("unsupported VEX statement")
        result[key] = {str(k): str(v) for k, v in item.items()}
    return result


def correlate(
    sbom_path: Path,
    sast_path: Path,
    kev_path: Path,
    kev_receipt_path: Path,
    vex_path: Path,
    now: dt.datetime,
) -> tuple[dict[str, Any], bool]:
    sbom = load_json(sbom_path)
    components = component_index(sbom)
    sast = load_json(sast_path)
    if not isinstance(sast, dict) or not isinstance(sast.get("results"), list):
        raise EvidenceError("Semgrep evidence is malformed")
    if sast.get("errors"):
        raise EvidenceError("Semgrep reported scan errors")
    _, kev_ids, kev_sha = validate_catalog(kev_path, kev_receipt_path, 7, now)
    dispositions = vex_index(load_json(vex_path))

    correlated: list[dict[str, Any]] = []
    unresolved: list[dict[str, str]] = []
    for vulnerability in sbom.get("vulnerabilities", []):
        if not isinstance(vulnerability, dict):
            raise EvidenceError("SBOM vulnerability must be an object")
        advisory_id = str(vulnerability.get("id", ""))
        affects = vulnerability.get("affects")
        if not advisory_id or not isinstance(affects, list) or not affects:
            raise EvidenceError("SBOM vulnerability requires id and affects")
        for affect in affects:
            ref = str(affect.get("ref", "")) if isinstance(affect, dict) else ""
            component = components.get(ref)
            if component is None:
                unresolved.append({"id": advisory_id, "bom_ref": ref})
                continue
            key = (advisory_id, component["name"])
            vex = dispositions.get(key)
            kev = advisory_id in kev_ids
            severity = max(
                (str(r.get("severity", "unknown")).upper()
                 for r in vulnerability.get("ratings", []) if isinstance(r, dict)),
                default="UNKNOWN",
            )
            correlated.append(
                {
                    "id": advisory_id,
                    "component": component,
                    "severity": severity,
                    "kev": kev,
                    "disposition": vex or {"status": "affected"},
                    "recommendation": str(vulnerability.get("recommendation", "")),
                    "blocking": kev or (
                        severity in {"HIGH", "CRITICAL"} and vex is None
                    ),
                }
            )

    sast_findings = [
        {
            "rule_id": str(item.get("check_id", "")),
            "path": str(item.get("path", "")),
            "severity": str(item.get("extra", {}).get("severity", "UNKNOWN")),
        }
        for item in sast["results"]
        if isinstance(item, dict)
    ]
    blocked = bool(unresolved or sast_findings or any(v["blocking"] for v in correlated))
    output = {
        "schema": "asynqmon-sast-sbom-cve-kev-correlation/v1",
        "result": "fail" if blocked else "pass",
        "summary": {
            "sbom_components": len(components),
            "sbom_vulnerabilities": len(sbom.get("vulnerabilities", [])),
            "correlated_component_vulnerabilities": len(correlated),
            "unresolved_component_references": len(unresolved),
            "sast_findings": len(sast_findings),
            "kev_matches": sum(item["kev"] for item in correlated),
            "blocking_findings": len(sast_findings)
            + len(unresolved)
            + sum(item["blocking"] for item in correlated),
        },
        "catalog": {"kev_sha256": kev_sha},
        "component_vulnerabilities": correlated,
        "unresolved_component_references": unresolved,
        "sast_findings": sast_findings,
    }
    return output, blocked


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sbom", required=True, type=Path)
    parser.add_argument("--sast", required=True, type=Path)
    parser.add_argument("--kev-catalog", required=True, type=Path)
    parser.add_argument("--kev-receipt", required=True, type=Path)
    parser.add_argument("--vex", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        result, blocked = correlate(
            args.sbom, args.sast, args.kev_catalog, args.kev_receipt, args.vex,
            dt.datetime.now(dt.timezone.utc),
        )
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    except (EvidenceError, OSError) as exc:
        print(f"security evidence correlation: unavailable: {exc}", file=sys.stderr)
        return 2
    print("security evidence correlation: "
          f"{result['result']} {result['summary']}")
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
