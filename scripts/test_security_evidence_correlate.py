from __future__ import annotations

import datetime as dt
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from security_evidence_correlate import EvidenceError, correlate


class EvidenceCorrelationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.now = dt.datetime(2026, 7, 30, tzinfo=dt.timezone.utc)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write(self, name: str, data: object) -> Path:
        path = self.root / name
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def evidence(self, affect_ref: str = "pkg:npm/example@1.0.0"):
        sbom = self.write(
            "sbom.json",
            {
                "bomFormat": "CycloneDX",
                "components": [
                    {
                        "bom-ref": "pkg:npm/example@1.0.0",
                        "name": "example",
                        "version": "1.0.0",
                        "purl": "pkg:npm/example@1.0.0",
                    }
                ],
                "vulnerabilities": [
                    {
                        "id": "CVE-2026-12345",
                        "ratings": [{"severity": "high"}],
                        "affects": [{"ref": affect_ref}],
                    }
                ],
            },
        )
        sast = self.write("sast.json", {"results": [], "errors": []})
        kev_data = {
            "catalogVersion": "2026.07.30",
            "dateReleased": "2026-07-30T00:00:00Z",
            "count": 1,
            "vulnerabilities": [{"cveID": "CVE-2026-12345"}],
        }
        kev = self.write("kev.json", kev_data)
        receipt = self.write(
            "receipt.json",
            {
                "schema": "asynqmon-security-catalog-receipt/v1",
                "retrieved_at": "2026-07-30T00:00:00Z",
                "sha256": hashlib.sha256(kev.read_bytes()).hexdigest(),
            },
        )
        vex = self.write("vex.json", {"schema": "asynqmon-vex/v1", "statements": []})
        return sbom, sast, kev, receipt, vex

    def test_correlates_component_and_blocks_kev(self) -> None:
        result, blocked = correlate(*self.evidence(), self.now)
        self.assertTrue(blocked)
        self.assertEqual(1, result["summary"]["kev_matches"])
        self.assertEqual("example", result["component_vulnerabilities"][0]["component"]["name"])

    def test_blocks_unresolved_sbom_reference(self) -> None:
        result, blocked = correlate(*self.evidence("missing-ref"), self.now)
        self.assertTrue(blocked)
        self.assertEqual(1, result["summary"]["unresolved_component_references"])


if __name__ == "__main__":
    unittest.main()
