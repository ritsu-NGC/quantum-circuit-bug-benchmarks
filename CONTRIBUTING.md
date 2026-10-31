# Contributing

Preserve provenance and distinguish a report from a confirmed circuit bug.
Some retained reports have been disputed or explained as expected behavior.
Do not silently remove them or turn issue closure into a claim of a fix.

## Updating the corpus

1. Edit `benchmarks/manifest.json` to update curated assessments and versions.
   Reported versions must come from the original post or a linked comment.
   Use an empty list when no numerical version is supplied.
2. Keep the upstream post and all issue comments in the benchmark's
   `source.json`, including resolving or closing comments. Preserve body
   strings verbatim and maintain comment order. Record the retrieval time
   and issue closure/reopening events.
3. For a fixed release, verify a merged fix or backport commit is an ancestor
   of a published stable release tag. Keep the PR number, commit, release,
   comparison evidence, and verification date in the manifest. Milestones
   and unmerged PRs are not sufficient.
4. Regenerate and check the documentation:

   ```sh
   python3 scripts/render_readmes.py
   python3 scripts/render_readmes.py --check
   python3 -m unittest discover -s tests -v
   ```

All commands use the Python standard library. Run them from the repository root.
The renderer is offline and never executes issue snippets.

## Scope and review

Include incorrect circuit construction, gate definitions, decomposition,
optimization, parameter preservation, and serialized circuit representations.
Label representation-only failures explicitly. Exclude hangs, UI problems,
and performance-only reports from newly added entries.

For each change, describe the evidence and any uncertainty. Do not claim a
first affected or first fixed release unless that boundary has been verified.
Fixed release versions below 1.0 refer to the historical `qiskit-terra`
distribution, not the old `qiskit` metapackage. Reported versions retain their
original context; early SDK reports can predate the Terra distribution split.
Some original body strings use CRLF newlines. The benchmark READMEs preserve
them; `.gitattributes` disables newline conversion for those generated files.

See `NOTICE` before copying upstream contributions. Do not add credentials,
private information, or downloaded attachments without reviewing them.
