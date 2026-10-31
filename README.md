# Quantum Circuit Bug Benchmarks

A source-attributed archive of 26 Qiskit circuit-related issue reports,
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
