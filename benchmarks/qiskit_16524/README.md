# Qiskit issue #16524: PhaseOracleGate (All 1s)

## Benchmark metadata

| Field | Value |
| --- | --- |
| Original issue | https://github.com/Qiskit/qiskit/issues/16524 |
| Source repository | `Qiskit/qiskit` |
| Original author | @as21507-art |
| Reported Qiskit version(s) at the issue | Not specified |
| Verified Qiskit version(s) containing the fix | `2.5.1`, `2.6.0` |
| Assessment | Confirmed bug |
| Upstream state at snapshot | closed (completed) |
| Created | 2026-07-02T13:53:56Z |
| Last upstream update | 2026-07-07T10:29:59Z |
| Closed | 2026-07-07T10:09:04Z |
| Retrieved | 2026-10-30T17:28:03+00:00 |

**Reported-version context:** The original Environment fields are blank. No numerical affected Qiskit version is supplied; none is inferred from the report date.

**Assessment:** Circuit-synthesis failure for a tautological Boolean oracle. A phase oracle for an all-true function should implement -I; a bit-flip oracle should apply an unconditional X. The issue's original expression contains a typo corrected in the first comment.

**Resolution:** Merged fix #16530 is verified in 2.6.0; its stable backport is already verified in 2.5.1.

Reported versions are not an exhaustive affected range. A verified fixed
version is a published release containing the fix, not necessarily the
first fixed version across all maintenance branches. Historical fixed
release versions below 1.0 refer to `qiskit-terra`, not the old `qiskit`
metapackage. Reported versions retain their original distribution context.

## Fix and resolution evidence

- https://github.com/Qiskit/qiskit/issues/16524#issuecomment-4866519479

### Verified fixed release: 2.5.1

- Distribution: `qiskit`.
- Original fix: https://github.com/Qiskit/qiskit/pull/16530.
- Included fix/backport PR: https://github.com/Qiskit/qiskit/pull/16543.
- Merged: 2026-07-08T07:25:58Z.
- Fix commit: `e1bf45efc1fc60f261f6127fad07bbafc33e8646`.
- Published release: https://github.com/Qiskit/qiskit/releases/tag/2.5.1 (2026-07-23T17:09:41Z).
- Ancestry comparison: https://github.com/Qiskit/qiskit/compare/e1bf45efc1fc60f261f6127fad07bbafc33e8646...2.5.1.
- Verification: Fix merge commit is an ancestor of the published release tag.
- Verified at: 2026-10-30T17:28:03+00:00.

### Verified fixed release: 2.6.0

- Distribution: `qiskit`.
- Original fix: https://github.com/Qiskit/qiskit/pull/16530.
- Included fix/backport PR: https://github.com/Qiskit/qiskit/pull/16530.
- Merged: 2026-07-07T10:09:03Z.
- Fix commit: `705667a1380dc7d069b6df84d9b613eb6de8ca0d`.
- Published release: https://github.com/Qiskit/qiskit/releases/tag/2.6.0 (2026-10-16T12:04:54Z).
- Ancestry comparison: https://github.com/Qiskit/qiskit/compare/705667a1380dc7d069b6df84d9b613eb6de8ca0d...2.6.0.
- Verification: Fix merge commit is an ancestor of the published release tag.
- Verified at: 2026-10-30T17:28:03+00:00.

## Original issue post

The body below is reproduced verbatim from the original issue post as
returned by GitHub at retrieval time. It may include upstream edits,
mistakes, HTML, and externally hosted attachments. It is not a
reconstruction of the issue's initial, pre-edit revision.

Source: https://github.com/Qiskit/qiskit/issues/16524 by @as21507-art.

<details>
<summary>Full original issue text</summary>

### Environment

- **Qiskit version**: 
- **Python version**: 
- **Operating system**: 


### What is happening?

I wanted to create a 3-qubit phase-oracle gate with f(x) = 1 for all x. This adds a negative sign to all qubits, which is a global phase. But even so, it should have produced some output. Instead, it throws the following error.

TranspilerError: 'HighLevelSynthesis is unable to synthesize "Phase Oracle"'

### How can we reproduce the issue?

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.circuit.library import PhaseOracleGate

oracle_gate = PhaseOracleGate("(x1 | ~x1) & (x2 | ~x2) & x3", label=" Oracle ")       # Creates oracle from a function where f(x) is always 1

qc = QuantumCircuit(oracle_gate.num_qubits)

for i in range(3):
    qc.h(i)
qc.append(oracle_gate, range(oracle_gate.num_qubits))    
for i in range(3):
    qc.h(i)

qc.measure_all()

simulator = AerSimulator()
compiled = transpile(qc, simulator)

num_shots = 1000
results = simulator.run(compiled, shots=num_shots).result()
count = results.get_counts()

count = percentage(dict(sorted(count.items())))
print(count)        

qc.draw(output="mpl")

### What should happen?

I think it should have been able to process this function. It does perfectly fine with the function f(x) = 0 for all x implemented using "(x1 & ~x1) | (x2 & ~x2) | (x3 & ~x3)"

### Any suggestions?

_No response_

</details>

## Issue discussion, including closing and resolving comments

All fetched issue comments are preserved below in upstream chronological
order, including any closing or resolving comments. Comments are
third-party statements, not automatically verified benchmark claims.

### Comment 4866519479 by @as21507-art

Posted: 2026-07-02T13:55:49Z. Updated: 2026-07-02T13:55:49Z.

Source: https://github.com/Qiskit/qiskit/issues/16524#issuecomment-4866519479

<details>
<summary>Full comment by @as21507-art</summary>

Typo in the 5th line where he Oracle gate should have been the following:

oracle_gate = PhaseOracleGate("(x1 | ~x1) & (x2 | ~x2) & (x3 | ~x3)", label=" Oracle ")  

</details>


## Closure and reopening events

- 2026-07-07T10:09:04Z: closed by @Cryoris.

Closing an issue does not establish that a code fix was merged or released.

## Attribution and reuse

The original post and comments remain attributed to their upstream authors.
Their inclusion does not relicense them under this project's MIT license.
See [NOTICE](../../NOTICE). Machine-readable text and provenance are in
[source.json](source.json); curated version evidence is in
[the manifest](../manifest.json). Attachments are linked, not vendored.
