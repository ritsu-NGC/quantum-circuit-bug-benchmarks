# Qiskit issue #16377: `CommutativeCancellation` incorrectly adds spurious global phase to P/U1 gates accumulating to 2π

## Benchmark metadata

| Field | Value |
| --- | --- |
| Original issue | https://github.com/Qiskit/qiskit/issues/16377 |
| Source repository | `Qiskit/qiskit` |
| Original author | @Timeless-hep |
| Reported Qiskit version(s) at the issue | `2.4.1` |
| Verified Qiskit version(s) containing the fix | `2.5.0` |
| Assessment | Confirmed bug |
| Upstream state at snapshot | closed (completed) |
| Created | 2026-06-05T05:04:40Z |
| Last upstream update | 2026-07-01T13:25:46Z |
| Closed | 2026-07-01T13:25:46Z |
| Retrieved | 2026-10-30T17:28:03+00:00 |

**Reported-version context:** Version(s) reported in the original issue environment; not a first-affected boundary.

**Assessment:** CommutativeCancellation adds an erroneous pi global phase when P/U1 rotations sum to 2*pi. The expected operator is I, not -I; a later control can make this phase observable.

**Resolution:** Merged fix #16402 is verified in 2.5.0.

Reported versions are not an exhaustive affected range. A verified fixed
version is a published release containing the fix, not necessarily the
first fixed version across all maintenance branches. Historical fixed
release versions below 1.0 refer to `qiskit-terra`, not the old `qiskit`
metapackage. Reported versions retain their original distribution context.

## Fix and resolution evidence


### Verified fixed release: 2.5.0

- Distribution: `qiskit`.
- Original fix: https://github.com/Qiskit/qiskit/pull/16402.
- Included fix/backport PR: https://github.com/Qiskit/qiskit/pull/16509.
- Merged: 2026-07-01T14:15:26Z.
- Fix commit: `8be74007537cd1a396ddf95e86872f20764a08d8`.
- Published release: https://github.com/Qiskit/qiskit/releases/tag/2.5.0 (2026-07-02T18:51:37Z).
- Ancestry comparison: https://github.com/Qiskit/qiskit/compare/8be74007537cd1a396ddf95e86872f20764a08d8...2.5.0.
- Verification: Fix merge commit is an ancestor of the published release tag.
- Verified at: 2026-10-30T17:28:03+00:00.

## Original issue post

The body below is reproduced verbatim from the original issue post as
returned by GitHub at retrieval time. It may include upstream edits,
mistakes, HTML, and externally hosted attachments. It is not a
reconstruction of the issue's initial, pre-edit revision.

Source: https://github.com/Qiskit/qiskit/issues/16377 by @Timeless-hep.

<details>
<summary>Full original issue text</summary>

### Environment

- **Qiskit version**: 2.4.1
- **Python version**: 3.13.13 
- **Operating system**: macOS


### What is happening?

When `transpiling` a circuit at `optimization_level=2` or `3`, the `CommutativeCancellation` pass silently alters the unitary operator of the circuit if commuting Z-rotations accumulate to `2π` and the pass selects PhaseGate (P) or U1Gate as the target gate. The compiler assumes all Z-axis rotations behave like the RZ gate where $RZ(2\pi) = -I$, and blindly subtracts a π phase to compensate. However, for Phase and U1 gates, $P(2\pi) = I$. Subtracting a π phase here results in an unwarranted $-I$ operator shift, breaking unitary equivalence (which escalates into a catastrophic local phase error if the circuit is later controlled).

### How can we reproduce the issue?

```python
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Operator

qc = QuantumCircuit(1)
qc.p(np.pi/4, 0)
for _ in range(7):
    qc.t(0)

print(f"Global Phase: {float(qc.global_phase):.4f}")
print("Operator Matrix:")
print(Operator(qc).data)

qc_t3 = transpile(qc, optimization_level=3, basis_gates=['p', 't', 'rz', 'cx'])

print(f"Global Phase: {float(qc_t3.global_phase):.4f}")
print("Operator Matrix:")
print(Operator(qc_t3).data)
```
Output:
```text
Global Phase: 0.0000
Operator Matrix:
[[1.+0.j 0.+0.j]
 [0.+0.j 1.+0.j]]
Global Phase: 3.1416
Operator Matrix:
[[-1.+0.j -0.+0.j]
 [-0.+0.j -1.+0.j]]
```

### What should happen?

The global phase after transpilation should remain `0.0000`, and the operator matrix should remain the identity matrix `[[1.+0.j, 0.+0.j], [0.+0.j, 1.+0.j]]`. The original and transpiled circuits must remain strictly unitarily equivalent.

### Any suggestions?

The bug is located in the Rust transpiler core at `crates/transpiler/src/passes/commutation_cancellation.rs`.

When the accumulated angle `mod4` reaches `2π`, the code unconditionally executes `total_phase -= PI;`. This logic is mathematically valid for `RX` and `RZ` variants but incorrect for `P` or `U1` gates.

To fix this, the phase correction step needs to be conditional based on the resolved identity of `z_var_gate`. The `-PI` compensation should only be applied if the target gate is symmetric (like `RZ`). If `z_var_gate` evaluates to `P` or `U1`, the `-PI` global phase subtraction must be explicitly skipped.

</details>

## Issue discussion, including closing and resolving comments

All fetched issue comments are preserved below in upstream chronological
order, including any closing or resolving comments. Comments are
third-party statements, not automatically verified benchmark claims.

### Comment 4636158715 by @7673502

Posted: 2026-06-05T22:44:08Z. Updated: 2026-06-05T22:44:08Z.

Source: https://github.com/Qiskit/qiskit/issues/16377#issuecomment-4636158715

<details>
<summary>Full comment by @7673502</summary>

I'd like to work on this. Could I be assigned?

</details>

### Comment 4637161402 by @alexanderivrii

Posted: 2026-06-06T03:03:15Z. Updated: 2026-06-06T03:03:15Z.

Source: https://github.com/Qiskit/qiskit/issues/16377#issuecomment-4637161402

<details>
<summary>Full comment by @alexanderivrii</summary>

Assigned.

</details>


## Closure and reopening events

- 2026-07-01T13:25:46Z: closed by @jakelishman.

Closing an issue does not establish that a code fix was merged or released.

## Attribution and reuse

The original post and comments remain attributed to their upstream authors.
Their inclusion does not relicense them under this project's MIT license.
See [NOTICE](../../NOTICE). Machine-readable text and provenance are in
[source.json](source.json); curated version evidence is in
[the manifest](../manifest.json). Attachments are linked, not vendored.
