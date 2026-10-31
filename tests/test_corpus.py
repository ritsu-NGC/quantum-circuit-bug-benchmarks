"""Offline corpus integrity, provenance, and documentation checks."""

from datetime import datetime
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.render_readmes import ASSESSMENTS, generate, render_issue


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_ISSUES = {
    17057, 16919, 16860, 16856, 16594, 16524, 16456, 16411, 16377,
    16164, 16161, 16168, 14356, 14265, 13547, 12948, 12694, 11954,
    9805, 9327, 5666, 5453, 6134, 7209, 3433, 86,
}


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class CorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(
            (ROOT / "benchmarks/manifest.json").read_text(encoding="utf-8")
        )
        cls.entries = cls.manifest["benchmarks"]

    def test_exact_requested_issue_set_and_directories(self):
        numbers = [entry["issue_number"] for entry in self.entries]
        self.assertEqual(len(numbers), 26)
        self.assertEqual(set(numbers), EXPECTED_ISSUES)
        directories = {
            int(path.name.removeprefix("qiskit_"))
            for path in (ROOT / "benchmarks").glob("qiskit_*") if path.is_dir()
        }
        self.assertEqual(directories, EXPECTED_ISSUES)

    def test_source_integrity_complete_comments_and_provenance(self):
        for entry in self.entries:
            number = entry["issue_number"]
            with self.subTest(issue=number):
                path = ROOT / "benchmarks" / f"qiskit_{number}" / "source.json"
                text = path.read_text(encoding="utf-8")
                self.assertEqual(digest(text), entry["source_sha256"])
                source = json.loads(text)
                self.assertEqual(source["repository"], "Qiskit/qiskit")
                issue = source["issue"]
                self.assertEqual(issue["number"], number)
                self.assertEqual(
                    issue["html_url"], f"https://github.com/Qiskit/qiskit/issues/{number}"
                )
                self.assertTrue(issue["author"])
                self.assertTrue(issue["body"])
                self.assertEqual(digest(issue["body"]), source["integrity"]["body_sha256"])
                comments = source["comments"]
                self.assertEqual(len(comments), source["integrity"]["expected_comment_count"])
                self.assertEqual(len({comment["id"] for comment in comments}), len(comments))
                self.assertEqual(
                    [comment["created_at"] for comment in comments],
                    sorted(comment["created_at"] for comment in comments),
                )
                for comment in comments:
                    self.assertTrue(comment["author"])
                    self.assertEqual(
                        comment["html_url"],
                        f"{issue['html_url']}#issuecomment-{comment['id']}",
                    )
                    self.assertEqual(
                        digest(comment["body"]),
                        source["integrity"]["comment_body_sha256"][str(comment["id"])],
                    )
                self.assertLessEqual(
                    datetime.fromisoformat(issue["updated_at"]),
                    datetime.fromisoformat(source["retrieved_at"]),
                )

    def test_readmes_preserve_full_source_bodies_and_required_fields(self):
        for entry in self.entries:
            number = entry["issue_number"]
            with self.subTest(issue=number):
                directory = ROOT / "benchmarks" / f"qiskit_{number}"
                source = json.loads((directory / "source.json").read_text(encoding="utf-8"))
                readme = (directory / "README.md").read_bytes().decode("utf-8")
                self.assertEqual(readme, render_issue(entry, source))
                for value in [source["issue"]["body"]] + [
                    comment["body"] for comment in source["comments"]
                ]:
                    self.assertIn(value, readme)
                for comment in source["comments"]:
                    self.assertIn(comment["html_url"], readme)
                for heading in [
                    "Original issue",
                    "Reported Qiskit version(s) at the issue",
                    "Verified Qiskit version(s) containing the fix",
                    "Issue discussion, including closing and resolving comments",
                    "Closure and reopening events",
                ]:
                    self.assertIn(heading, readme)

    def test_versions_assessments_and_fix_ancestry(self):
        for entry in self.entries:
            with self.subTest(issue=entry["issue_number"]):
                self.assertIn(entry["assessment"], ASSESSMENTS)
                self.assertTrue(entry["assessment_notes"])
                self.assertTrue(entry["reported_version_notes"])
                self.assertTrue(entry["resolution_notes"])
                for version in entry["reported_versions"]:
                    self.assertRegex(version, r"^\d+\.\d+")
                for release in entry["verified_fixed_releases"]:
                    self.assertRegex(release["version"], r"^\d+\.\d+\.\d+$")
                    self.assertIn(release["ancestry"]["status"], {"ahead", "identical"})
                    self.assertEqual(release["ancestry"]["behind_by"], 0)
                    self.assertEqual(
                        release["merge_commit"], release["ancestry"]["base_commit"]
                    )
                    self.assertEqual(
                        release["merge_commit"], release["ancestry"]["merge_base_commit"]
                    )
                    self.assertRegex(release["merge_commit"], r"^[0-9a-f]{40}$")
                    self.assertLessEqual(
                        datetime.fromisoformat(release["merged_at"]),
                        datetime.fromisoformat(release["release_published_at"]),
                    )
                    self.assertFalse(release["earliest_release_claimed"])
                    expected = (
                        "qiskit-terra" if release["version"].startswith("0.") else "qiskit"
                    )
                    self.assertEqual(release["distribution"], expected)

    def test_nonbugs_and_unspecified_versions_are_not_fabricated(self):
        entries = {entry["issue_number"]: entry for entry in self.entries}
        self.assertEqual(entries[86]["assessment"], "not_a_bug")
        self.assertFalse(entries[86]["verified_fixed_releases"])
        self.assertEqual(entries[14265]["assessment"], "disputed_report")
        for number in [16524, 16456, 11954, 5666, 6134]:
            self.assertEqual(entries[number]["reported_versions"], [])
        for number in [16860, 16411, 14356, 14265, 12694, 3433]:
            self.assertEqual(entries[number]["verified_fixed_releases"], [])

    def test_generated_documentation_is_current(self):
        self.assertEqual(generate(check=True), 28)

    def test_check_reports_missing_or_stale_files_without_writing(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "benchmarks").mkdir()
            manifest = self.manifest | {"benchmarks": []}
            (root / "benchmarks/manifest.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(SystemExit, "Generated documentation is stale"):
                generate(root=root, check=True)
            self.assertFalse((root / "README.md").exists())
            self.assertEqual(generate(root=root), 2)
            self.assertEqual(generate(root=root, check=True), 2)
            (root / "README.md").write_text("stale\n")
            with self.assertRaisesRegex(SystemExit, "README.md"):
                generate(root=root, check=True)
            self.assertEqual((root / "README.md").read_text(), "stale\n")


if __name__ == "__main__":
    unittest.main()
