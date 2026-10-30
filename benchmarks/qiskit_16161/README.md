# Qiskit issue #16161: CommutativeOptimization silently corrupts direction-sensitive XXPlusYYGate by incorrectly treating it as a symmetric gate

## Benchmark metadata

| Field | Value |
| --- | --- |
| Original issue | https://github.com/Qiskit/qiskit/issues/16161 |
| Source repository | `Qiskit/qiskit` |
| Original author | @Timeless-hep |
| Reported Qiskit version(s) at the issue | `2.4.1` |
| Verified Qiskit version(s) containing the fix | `2.5.0` |
| Assessment | Confirmed bug |
| Upstream state at snapshot | closed (completed) |
| Created | 2026-05-09T08:04:05Z |
| Last upstream update | 2026-05-18T10:12:04Z |
| Closed | 2026-05-18T10:12:04Z |
| Retrieved | 2026-10-30T17:28:03+00:00 |

**Reported-version context:** Version(s) reported in the original issue environment; not a first-affected boundary.

**Assessment:** A general two-parameter XXPlusYY gate is direction-sensitive, so reversed-qarg gates must not be canceled as a symmetric inverse pair.

**Resolution:** Merged fix #16163 is verified in 2.5.0. The issue's 2.4.2 milestone alone is not used as release evidence.

Reported versions are not an exhaustive affected range. A verified fixed
version is a published release containing the fix, not necessarily the
first fixed version across all maintenance branches. Historical fixed
release versions below 1.0 refer to `qiskit-terra`, not the old `qiskit`
metapackage. Reported versions retain their original distribution context.

## Fix and resolution evidence


### Verified fixed release: 2.5.0

- Distribution: `qiskit`.
- Original fix: https://github.com/Qiskit/qiskit/pull/16163.
- Included fix/backport PR: https://github.com/Qiskit/qiskit/pull/16163.
- Merged: 2026-05-18T10:12:02Z.
- Fix commit: `1e13f243026334c68f4b760823dccf3cb3c4f03b`.
- Published release: https://github.com/Qiskit/qiskit/releases/tag/2.5.0 (2026-07-02T18:51:37Z).
- Ancestry comparison: https://github.com/Qiskit/qiskit/compare/1e13f243026334c68f4b760823dccf3cb3c4f03b...2.5.0.
- Verification: Fix merge commit is an ancestor of the published release tag.
- Verified at: 2026-10-30T17:28:03+00:00.

## Original issue post

The body below is reproduced verbatim from the original issue post as
returned by GitHub at retrieval time. It may include upstream edits,
mistakes, HTML, and externally hosted attachments. It is not a
reconstruction of the issue's initial, pre-edit revision.

Source: https://github.com/Qiskit/qiskit/issues/16161 by @Timeless-hep.

<details>
<summary>Full original issue text</summary>

### Environment

- **Qiskit version**: 2.4.1
- **Python version**: 3.13.13
- **Operating system**: macOS


### What is happening?

In the transpiler source code, StandardGate::XXPlusYY is erroneously hardcoded into the SYMMETRIC_GATES list. Because of this misclassification, CommutativeOptimization ignores the qubit order for this gate.

XXPlusYYGate(theta, beta) is actually a direction-sensitive operation whenever beta != 0 and beta != pi. Its action on the qubit order [0, 1] is mathematically distinct from its action on [1, 0].

If a user constructs a circuit with a forward rotation on [0, 1] followed by an inverse rotation on [1, 0], the optimizer incorrectly treats them as identical inverse operations on the same wire order. It then erroneously cancels and deletes both gates. This leads to a silent correctness error where a non-trivial two-qubit operation is wrongly optimized into an identity operation, altering the mathematical semantics of the circuit.

### How can we reproduce the issue?

import numpy as np
import qiskit
from qiskit import QuantumCircuit
from qiskit.circuit.library import XXPlusYYGate
from qiskit.quantum_info import Statevector
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import CommutativeOptimization

theta = np.pi / 2
beta = np.pi / 3
xy = XXPlusYYGate(theta, beta)

qc = QuantumCircuit(2)
qc.append(xy, [0, 1])
qc.append(xy.power(-1), [1, 0])  

qc_opt = PassManager([CommutativeOptimization()]).run(qc)

initial_state = Statevector.from_label("01")
state_before = initial_state.evolve(qc)
state_after = initial_state.evolve(qc_opt)


print("Probabilities before:", state_before.probabilities_dict())
print("Probabilities after:", state_after.probabilities_dict())


### What should happen?

The transpiler must not alter the circuit semantics. CommutativeOptimization should recognize that XXPlusYYGate on [0, 1] and its inverse on [1, 0] are not mathematically equivalent operations that cancel each other out. The optimizer should leave the two XXPlusYYGate instances intact. The optimized circuit must remain mathematically equivalent to the original circuit and produce the identical probability distribution.

### Any suggestions?

The most direct fix is to remove StandardGate::XXPlusYY from the SYMMETRIC_GATES list in crates/transpiler/src/passes/commutative_optimization.rs (around line 79).

If optimization for special cases is desired, the logic must be updated to dynamically check the beta parameter and only treat the gate as symmetric when it is explicitly known that beta = 0 or beta = pi. By default, it must not be treated as a qubit permutation invariant gate.

</details>

## Issue discussion, including closing and resolving comments

All fetched issue comments are preserved below in upstream chronological
order, including any closing or resolving comments. Comments are
third-party statements, not automatically verified benchmark claims.

### Comment 4414529503 by @alexanderivrii

Posted: 2026-05-10T05:32:00Z. Updated: 2026-05-10T05:32:00Z.

Source: https://github.com/Qiskit/qiskit/issues/16161#issuecomment-4414529503

<details>
<summary>Full comment by @alexanderivrii</summary>

Thank you for the report, @YujinSong-hep. I have pushed a fix in #16163.

</details>


## Closure and reopening events

- 2026-05-18T10:12:04Z: closed by @alexanderivrii.

Closing an issue does not establish that a code fix was merged or released.

## Attribution and reuse

The original post and comments remain attributed to their upstream authors.
Their inclusion does not relicense them under this project's MIT license.
See [NOTICE](../../NOTICE). Machine-readable text and provenance are in
[source.json](source.json); curated version evidence is in
[the manifest](../manifest.json). Attachments are linked, not vendored.
