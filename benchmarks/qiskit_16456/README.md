# Qiskit issue #16456: `Commuting2qBlock` loses parameters from parametric gates

## Benchmark metadata

| Field | Value |
| --- | --- |
| Original issue | https://github.com/Qiskit/qiskit/issues/16456 |
| Source repository | `Qiskit/qiskit` |
| Original author | @TalKozlovski |
| Reported Qiskit version(s) at the issue | Not specified |
| Verified Qiskit version(s) containing the fix | `2.6.0` |
| Assessment | Confirmed bug |
| Upstream state at snapshot | closed (completed) |
| Created | 2026-06-21T13:01:26Z |
| Last upstream update | 2026-07-07T12:42:44Z |
| Closed | 2026-07-07T12:42:44Z |
| Retrieved | 2026-10-30T17:28:03+00:00 |

**Reported-version context:** The issue reports 'main branch', without a numerical release or commit. Python 3.10+ in the environment is not a Qiskit version.

**Assessment:** Circuit-representation/parameter-tracking bug: Commuting2qBlock exposes an empty parameter list for parametric input gates.

**Resolution:** Merged fix #16459 is verified in 2.6.0.

Reported versions are not an exhaustive affected range. A verified fixed
version is a published release containing the fix, not necessarily the
first fixed version across all maintenance branches. Historical fixed
release versions below 1.0 refer to `qiskit-terra`, not the old `qiskit`
metapackage. Reported versions retain their original distribution context.

## Fix and resolution evidence


### Verified fixed release: 2.6.0

- Distribution: `qiskit`.
- Original fix: https://github.com/Qiskit/qiskit/pull/16459.
- Included fix/backport PR: https://github.com/Qiskit/qiskit/pull/16459.
- Merged: 2026-07-07T12:42:43Z.
- Fix commit: `5647a61094ae99c07aaee0f4358b4a19f5a42fd8`.
- Published release: https://github.com/Qiskit/qiskit/releases/tag/2.6.0 (2026-10-16T12:04:54Z).
- Ancestry comparison: https://github.com/Qiskit/qiskit/compare/5647a61094ae99c07aaee0f4358b4a19f5a42fd8...2.6.0.
- Verification: Fix merge commit is an ancestor of the published release tag.
- Verified at: 2026-10-30T17:28:03+00:00.

## Original issue post

The body below is reproduced verbatim from the original issue post as
returned by GitHub at retrieval time. It may include upstream edits,
mistakes, HTML, and externally hosted attachments. It is not a
reconstruction of the issue's initial, pre-edit revision.

Source: https://github.com/Qiskit/qiskit/issues/16456 by @TalKozlovski.

<details>
<summary>Full original issue text</summary>

### Environment

- **Qiskit version**: main branch 
- **Python version**: 3.10+

### What is happening?

`Commuting2qBlock` loses all parameters from input parametric gates because `params` is hardcoded to an empty list in `__init__`


### How can we reproduce the issue?

```python
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.converters import circuit_to_dag
from qiskit.transpiler.passes.routing.commuting_2q_gate_routing.commuting_2q_block import Commuting2qBlock

# Create parametric circuit
qc = QuantumCircuit(3)
c_0 = Parameter('c_0')
c_1 = Parameter('c_1')
qc.rzz(c_0, 0, 1)
qc.rzz(c_1, 1, 2)

# Create block
dag = circuit_to_dag(qc)
nodes = list(dag.topological_op_nodes())
block = Commuting2qBlock(nodes)

print(f"Circuit parameters: {qc.parameters}")  # Shows c_0, c_1
print(f"Block parameters: {block.params}")     # Shows []

```

### What should happen?

`block.params` should contain `[Parameter('c_0'), Parameter('c_1')]`

### Any suggestions?

The bug is in commuting_2q_block.py line 53 where params=[] is hardcoded. The fix should extract parameters from gate operations and handle ParameterExpression objects.

</details>

## Issue discussion, including closing and resolving comments

All fetched issue comments are preserved below in upstream chronological
order, including any closing or resolving comments. Comments are
third-party statements, not automatically verified benchmark claims.

### Comment 4762132487 by @ShellyGarion

Posted: 2026-06-21T13:30:28Z. Updated: 2026-06-21T13:30:28Z.

Source: https://github.com/Qiskit/qiskit/issues/16456#issuecomment-4762132487

<details>
<summary>Full comment by @ShellyGarion</summary>

Hi @TalKozlovski - thanks for reporting this bug, would you like to open a PR to fix it?

</details>


## Closure and reopening events

- 2026-07-07T12:42:44Z: closed by @Cryoris.

Closing an issue does not establish that a code fix was merged or released.

## Attribution and reuse

The original post and comments remain attributed to their upstream authors.
Their inclusion does not relicense them under this project's MIT license.
See [NOTICE](../../NOTICE). Machine-readable text and provenance are in
[source.json](source.json); curated version evidence is in
[the manifest](../manifest.json). Attachments are linked, not vendored.
