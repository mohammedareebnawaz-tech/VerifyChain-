"""Run with:  python -m unittest test_blockchain -v"""

import os
import tempfile
import unittest

from app import Blockchain


class VerifyChainTests(unittest.TestCase):
    def setUp(self):
        handle, self.path = tempfile.mkstemp(suffix=".json")
        os.close(handle)
        os.remove(self.path)  # start with no file so a fresh genesis block is created
        self.bc = Blockchain(self.path)
        self.bc.issue("Asha Rao", "B.Tech CSE", "CERT-001", "2026-06-01")

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_genuine_certificate_is_valid(self):
        result = self.bc.verify("Asha Rao", "B.Tech CSE", "CERT-001", "2026-06-01")
        self.assertEqual(result["status"], "valid")

    def test_edited_details_are_detected_as_fake(self):
        result = self.bc.verify("Asha Rao", "B.Tech CSE", "CERT-001", "2025-06-01")
        self.assertEqual(result["status"], "fake")

    def test_unknown_certificate_is_fake(self):
        result = self.bc.verify("Ravi", "MBA", "CERT-999", "2026-06-01")
        self.assertEqual(result["status"], "fake")

    def test_duplicate_certificate_id_is_rejected(self):
        ok, _ = self.bc.issue("Someone Else", "B.Sc", "CERT-001", "2026-06-02")
        self.assertFalse(ok)

    def test_chain_is_valid_before_tampering(self):
        ok, _ = self.bc.is_valid()
        self.assertTrue(ok)

    def test_tampering_breaks_the_chain(self):
        self.bc.tamper_demo()
        ok, _ = self.bc.is_valid()
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
