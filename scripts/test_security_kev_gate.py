from __future__ import annotations

import datetime as dt
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from security_kev_gate import EvidenceError, correlate


class KevGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.now = dt.datetime(2026, 7, 30, tzinfo=dt.timezone.utc)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_evidence(
        self, vulnerability_id: str, severity: str = "MEDIUM"
    ) -> tuple[Path, Path, Path]:
        report = self.root / "trivy.json"
        report.write_text(
            json.dumps(
                {
                    "Results": [
                        {
                            "Target": "ui/yarn.lock",
                            "Vulnerabilities": [
                                {
                                    "VulnerabilityID": vulnerability_id,
                                    "PkgName": "example",
                                    "InstalledVersion": "1.0.0",
                                    "FixedVersion": "1.0.1",
                                    "Severity": severity,
                                }
                            ],
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        catalog = self.root / "kev.json"
        catalog.write_text(
            json.dumps(
                {
                    "catalogVersion": "2026.07.30",
                    "dateReleased": "2026-07-30T00:00:00Z",
                    "count": 1,
                    "vulnerabilities": [
                        {
                            "cveID": "CVE-2026-12345",
                            "vendorProject": "vendor",
                            "product": "product",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        receipt = self.root / "receipt.json"
        receipt.write_text(
            json.dumps(
                {
                    "schema": "asynqmon-security-catalog-receipt/v1",
                    "retrieved_at": "2026-07-30T00:00:00Z",
                    "sha256": hashlib.sha256(catalog.read_bytes()).hexdigest(),
                }
            ),
            encoding="utf-8",
        )
        return report, catalog, receipt

    def test_blocks_exact_kev_match(self) -> None:
        evidence = self.write_evidence("CVE-2026-12345")
        result, blocked = correlate(*evidence, None, 7, self.now)
        self.assertTrue(blocked)
        self.assertEqual(1, result["summary"]["kev_matches"])

    def test_blocks_high_non_cve_advisory_and_discloses_boundary(self) -> None:
        evidence = self.write_evidence("GHSA-aaaa-bbbb-cccc", "HIGH")
        result, blocked = correlate(*evidence, None, 7, self.now)
        self.assertTrue(blocked)
        self.assertEqual(1, result["summary"]["ignored_non_cve_findings"])
        self.assertEqual(["GHSA-aaaa-bbbb-cccc"], result["ignored_non_cve_ids"])

    def test_rejects_tampered_catalog(self) -> None:
        report, catalog, receipt = self.write_evidence("CVE-2026-99999")
        catalog.write_text("{}\n", encoding="utf-8")
        with self.assertRaises(EvidenceError):
            correlate(report, catalog, receipt, None, 7, self.now)

    def test_rejects_stale_catalog(self) -> None:
        evidence = self.write_evidence("CVE-2026-99999")
        with self.assertRaises(EvidenceError):
            correlate(
                *evidence,
                None,
                7,
                self.now + dt.timedelta(days=8),
            )

    def test_accepts_narrow_not_affected_vex_statement(self) -> None:
        report, catalog, receipt = self.write_evidence(
            "GHSA-aaaa-bbbb-cccc", "HIGH"
        )
        vex = self.root / "vex.json"
        vex.write_text(
            json.dumps(
                {
                    "schema": "asynqmon-vex/v1",
                    "statements": [
                        {
                            "advisory_id": "GHSA-aaaa-bbbb-cccc",
                            "package": "example",
                            "status": "not_affected",
                            "justification": "vulnerable_code_not_in_execute_path",
                            "detail": "The affected feature is not used.",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        result, blocked = correlate(
            report, catalog, receipt, vex, 7, self.now
        )
        self.assertFalse(blocked)
        self.assertEqual(1, result["summary"]["vex_not_affected_findings"])

    def test_kev_match_cannot_be_waived(self) -> None:
        report, catalog, receipt = self.write_evidence(
            "CVE-2026-12345", "HIGH"
        )
        vex = self.root / "vex.json"
        vex.write_text(
            json.dumps(
                {
                    "schema": "asynqmon-vex/v1",
                    "statements": [
                        {
                            "advisory_id": "CVE-2026-12345",
                            "package": "example",
                            "status": "not_affected",
                            "justification": "vulnerable_code_not_in_execute_path",
                            "detail": "Attempted KEV waiver.",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        result, blocked = correlate(
            report, catalog, receipt, vex, 7, self.now
        )
        self.assertTrue(blocked)
        self.assertEqual(1, result["summary"]["kev_matches"])


if __name__ == "__main__":
    unittest.main()
