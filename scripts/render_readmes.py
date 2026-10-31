#!/usr/bin/env python3
"""Render the benchmark documentation from the local, attributed snapshots."""

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSESSMENTS = {
    "confirmed_bug": "Confirmed bug",
    "mixed_report": "Mixed report: confirmed and disputed/expected aspects",
    "disputed_report": "Disputed report / expected behavior under discussion",
    "not_a_bug": "Explained upstream as not a bug",
}


def cell(value):
    """Keep arbitrary upstream titles on a single Markdown table row."""
    return value.replace("|", r"\|").replace("\r", " ").replace("\n", " ")


def versions(entry):
    values = entry["reported_versions"]
    return ", ".join(f"`{value}`" for value in values) if values else "Not specified"


def fixed_versions(entry):
    releases = entry["verified_fixed_releases"]
    if not releases:
        return "Not applicable" if entry["assessment"] == "not_a_bug" else "Not verified"
    values = dict.fromkeys(release["version"] for release in releases)
    return ", ".join(f"`{value}`" for value in values)


def render_issue(entry, source):
    issue = source["issue"]
    comments = source["comments"]
    state = issue["state"]
    if issue["state_reason"]:
        state += f" ({issue['state_reason']})"
    lines = [
        f"# Qiskit issue #{issue['number']}: {issue['title']}",
        "",
        "## Benchmark metadata",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Original issue | {issue['html_url']} |",
        f"| Source repository | `{source['repository']}` |",
        f"| Original author | @{issue['author']} |",
        f"| Reported Qiskit version(s) at the issue | {versions(entry)} |",
        f"| Verified Qiskit version(s) containing the fix | {fixed_versions(entry)} |",
        f"| Assessment | {ASSESSMENTS[entry['assessment']]} |",
        f"| Upstream state at snapshot | {state} |",
        f"| Created | {issue['created_at']} |",
        f"| Last upstream update | {issue['updated_at']} |",
        f"| Closed | {issue['closed_at'] or 'Not closed'} |",
        f"| Retrieved | {source['retrieved_at']} |",
        "",
        "**Reported-version context:** " + entry["reported_version_notes"],
        "",
        "**Assessment:** " + entry["assessment_notes"],
        "",
        "**Resolution:** " + entry["resolution_notes"],
        "",
        "Reported versions are not an exhaustive affected range. A verified fixed",
        "version is a published release containing the fix, not necessarily the",
        "first fixed version across all maintenance branches. Historical fixed",
        "release versions below 1.0 refer to `qiskit-terra`, not the old `qiskit`",
        "metapackage. Reported versions retain their original distribution context.",
        "",
        "## Fix and resolution evidence",
        "",
    ]
    for url in entry["assessment_sources"]:
        lines.append(f"- {url}")
    for release in entry["verified_fixed_releases"]:
        lines.extend([
            "",
            f"### Verified fixed release: {release['version']}",
            "",
            f"- Distribution: `{release['distribution']}`.",
            f"- Original fix: https://github.com/Qiskit/qiskit/pull/{release['original_pull_request']}.",
            f"- Included fix/backport PR: {release['pull_request_url']}.",
            f"- Merged: {release['merged_at']}.",
            f"- Fix commit: `{release['merge_commit']}`.",
            f"- Published release: {release['release_url']} ({release['release_published_at']}).",
            f"- Ancestry comparison: {release['ancestry']['html_url']}.",
            f"- Verification: {release['verification_method']}",
            f"- Verified at: {release['verified_at']}.",
        ])
    if not entry["assessment_sources"] and not entry["verified_fixed_releases"]:
        lines.append("No merged fix or fixed release was verified; see the full discussion below.")
    lines.extend([
        "",
        "## Original issue post",
        "",
        "The body below is reproduced verbatim from the original issue post as",
        "returned by GitHub at retrieval time. It may include upstream edits,",
        "mistakes, HTML, and externally hosted attachments. It is not a",
        "reconstruction of the issue's initial, pre-edit revision.",
        "",
        f"Source: {issue['html_url']} by @{issue['author']}.",
        "",
        "<details>",
        "<summary>Full original issue text</summary>",
        "",
        issue["body"],
        "",
        "</details>",
        "",
        "## Issue discussion, including closing and resolving comments",
        "",
        "All fetched issue comments are preserved below in upstream chronological",
        "order, including any closing or resolving comments. Comments are",
        "third-party statements, not automatically verified benchmark claims.",
        "",
    ])
    if not comments:
        lines.append("No issue comments were present at retrieval time.")
    for comment in comments:
        lines.extend([
            f"### Comment {comment['id']} by @{comment['author']}",
            "",
            f"Posted: {comment['created_at']}. Updated: {comment['updated_at']}.",
            "",
            f"Source: {comment['html_url']}",
            "",
            "<details>",
            f"<summary>Full comment by @{comment['author']}</summary>",
            "",
            comment["body"],
            "",
            "</details>",
            "",
        ])
    lines.extend(["", "## Closure and reopening events", ""])
    if not source["state_events"]:
        lines.append("No closure or reopening events were present in the fetched timeline.")
    for event in source["state_events"]:
        detail = f"- {event['created_at']}: {event['event']} by @{event['actor']}."
        if event["commit_url"]:
            detail += f" Associated commit: {event['commit_url']}."
        lines.append(detail)
    lines.extend([
        "",
        "Closing an issue does not establish that a code fix was merged or released.",
        "",
        "## Attribution and reuse",
        "",
        "The original post and comments remain attributed to their upstream authors.",
        "Their inclusion does not relicense them under this project's MIT license.",
        "See [NOTICE](../../NOTICE). Machine-readable text and provenance are in",
        "[source.json](source.json); curated version evidence is in",
        "[the manifest](../manifest.json). Attachments are linked, not vendored.",
        "",
    ])
    return "\n".join(lines)


def render_index(manifest, sources):
    lines = [
        "# Benchmark index",
        "",
        f"This snapshot contains {len(manifest['benchmarks'])} reports from "
        f"`{manifest['repository']}`.",
        "",
        "Fixed versions below are verified containing releases, not necessarily",
        "the first fixed release on every branch. See each README for provenance,",
        "complete original text, all issue comments, and verification evidence.",
        "Not every retained report is a confirmed circuit bug.",
        "",
        "| Benchmark | Original issue title | Reported version(s) | Verified fixed version(s) | Assessment |",
        "| --- | --- | --- | --- | --- |",
    ]
    for entry in manifest["benchmarks"]:
        number = entry["issue_number"]
        title = cell(sources[number]["issue"]["title"])
        lines.append(
            f"| [qiskit_{number}](qiskit_{number}/README.md) | {title} | "
            f"{versions(entry)} | {fixed_versions(entry)} | "
            f"{ASSESSMENTS[entry['assessment']]} |"
        )
    lines.extend(["", "Curated metadata: [manifest.json](manifest.json).", ""])
    return "\n".join(lines)


def render_root(manifest):
    count = len(manifest["benchmarks"])
    return f"""# Quantum Circuit Bug Benchmarks

A source-attributed archive of {count} Qiskit circuit-related issue reports,
their reported versions, verified releases containing fixes, and full issue
discussions. Start with the [benchmark index](benchmarks/README.md).

## Scope

The initial corpus preserves the 26 reports selected in the original research
request, including circuit construction, gate semantics, synthesis, transpiler
correctness, parameter preservation, and circuit serialization. It is not an
exhaustive list of Qiskit bugs and does not yet provide executable benchmark
harnesses.

**A report is not necessarily a confirmed bug.** Original discussions can
contradict the report or reveal expected behavior. Assessments explicitly mark
confirmed, mixed, disputed, and non-bug reports; all initial entries are retained
for traceability. Representation-only errors are distinguished in their notes.

## Version and resolution policy

- Reported versions come from the issue or its discussion, not inferred dates.
  Some reports name only `main` or supply no numerical version.
- Fixed versions require a merged fix or backport commit verified as an
  ancestor of a published stable release tag. A milestone or a closed issue
  alone is insufficient.
- Listed fixed versions are known containing releases, not an exhaustive list
  of fixed branches or a guaranteed first-fixed boundary.
- Fixed release versions below 1.0 refer to historical **qiskit-terra**, not the
  former **qiskit metapackage**. Use the distribution named in each fix record.
  Reported versions retain their original context, including pre-Terra SDK reports.
- Full source discussions, including closing and resolving comments, are
  preserved verbatim as retrieved. They may contain upstream errors. Original
  posts are current-body snapshots, not pre-edit history.

## Layout

```text
.github/PULL_REQUEST_TEMPLATE.md
benchmarks/
  README.md
  manifest.json
  qiskit_<issue_number>/
    README.md
    source.json
scripts/render_readmes.py
tests/test_corpus.py
CODE_OF_CONDUCT.md
CONTRIBUTING.md
LICENSE
NOTICE
README.md
```

Each benchmark README contains the original issue link, reported Qiskit version,
verified fixed version or an explicit unknown/not-applicable marker, complete
issue post, all comments, and closure/reopening events. `source.json` preserves
the exact post/comment body strings with authors, source URLs, and timestamps.
`benchmarks/manifest.json` contains curated assessments and fix ancestry evidence.

## Regenerating documentation

Python 3.10+ and its standard library are sufficient:

```sh
python3 scripts/render_readmes.py
python3 scripts/render_readmes.py --check
python3 -m unittest discover -s tests -v
```

The renderer is offline. It does not import Qiskit or execute third-party issue
snippets. Review snippets and isolate environments before trying reproducers.
See [CONTRIBUTING.md](CONTRIBUTING.md) for the evidence and update policy.

## Attribution and license

Original project tooling and documentation are MIT licensed. Imported issue
posts and comments are attributed third-party material and are not relicensed
by this repository. See [NOTICE](NOTICE) and [LICENSE](LICENSE). Attachments remain
linked upstream, not mirrored. This project is not affiliated with Qiskit.
"""


def generate(root=ROOT, check=False):
    manifest = json.loads((root / "benchmarks/manifest.json").read_text(encoding="utf-8"))
    sources = {}
    outputs = {}
    for entry in manifest["benchmarks"]:
        number = entry["issue_number"]
        directory = root / "benchmarks" / f"qiskit_{number}"
        source = json.loads((directory / "source.json").read_text(encoding="utf-8"))
        sources[number] = source
        outputs[directory / "README.md"] = render_issue(entry, source)
    outputs[root / "benchmarks/README.md"] = render_index(manifest, sources)
    outputs[root / "README.md"] = render_root(manifest)
    stale = []
    for path, content in outputs.items():
        if check:
            if not path.exists() or path.read_bytes().decode("utf-8") != content:
                stale.append(str(path.relative_to(root)))
        else:
            path.write_text(content, encoding="utf-8")
    if stale:
        raise SystemExit("Generated documentation is stale: " + ", ".join(stale))
    return len(outputs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if generated files differ")
    options = parser.parse_args()
    print(f"{'Checked' if options.check else 'Rendered'} {generate(check=options.check)} READMEs.")
