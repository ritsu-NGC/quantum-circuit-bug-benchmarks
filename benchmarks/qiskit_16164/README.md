# Qiskit issue #16164: CommutationChecker yields false positives for CRZ and SWAP resulting in silent miscompilation

## Benchmark metadata

| Field | Value |
| --- | --- |
| Original issue | https://github.com/Qiskit/qiskit/issues/16164 |
| Source repository | `Qiskit/qiskit` |
| Original author | @Timeless-hep |
| Reported Qiskit version(s) at the issue | `2.4.1` |
| Verified Qiskit version(s) containing the fix | `2.4.2`, `2.5.0` |
| Assessment | Confirmed bug |
| Upstream state at snapshot | closed (completed) |
| Created | 2026-05-11T09:21:48Z |
| Last upstream update | 2026-06-08T21:20:01Z |
| Closed | 2026-06-08T21:20:01Z |
| Retrieved | 2026-10-30T17:28:03+00:00 |

**Reported-version context:** Version(s) reported in the original issue environment; not a first-affected boundary.

**Assessment:** False CRZ/SWAP commutation permits invalid SWAP cancellation and changes the circuit unitary.

**Resolution:** Merged fix #16337 is verified in 2.5.0; backport #16395 is verified in 2.4.2.

Reported versions are not an exhaustive affected range. A verified fixed
version is a published release containing the fix, not necessarily the
first fixed version across all maintenance branches. Historical fixed
release versions below 1.0 refer to `qiskit-terra`, not the old `qiskit`
metapackage. Reported versions retain their original distribution context.

## Fix and resolution evidence


### Verified fixed release: 2.4.2

- Distribution: `qiskit`.
- Original fix: https://github.com/Qiskit/qiskit/pull/16337.
- Included fix/backport PR: https://github.com/Qiskit/qiskit/pull/16395.
- Merged: 2026-06-09T07:53:05Z.
- Fix commit: `1da93bbdb50008f778e93e394b4653b111031181`.
- Published release: https://github.com/Qiskit/qiskit/releases/tag/2.4.2 (2026-06-12T17:39:03Z).
- Ancestry comparison: https://github.com/Qiskit/qiskit/compare/1da93bbdb50008f778e93e394b4653b111031181...2.4.2.
- Verification: Fix merge commit is an ancestor of the published release tag.
- Verified at: 2026-10-30T17:28:03+00:00.

### Verified fixed release: 2.5.0

- Distribution: `qiskit`.
- Original fix: https://github.com/Qiskit/qiskit/pull/16337.
- Included fix/backport PR: https://github.com/Qiskit/qiskit/pull/16337.
- Merged: 2026-06-08T21:19:59Z.
- Fix commit: `592c1de0065816fb6f4c52fbd0bfdc5922936111`.
- Published release: https://github.com/Qiskit/qiskit/releases/tag/2.5.0 (2026-07-02T18:51:37Z).
- Ancestry comparison: https://github.com/Qiskit/qiskit/compare/592c1de0065816fb6f4c52fbd0bfdc5922936111...2.5.0.
- Verification: Fix merge commit is an ancestor of the published release tag.
- Verified at: 2026-10-30T17:28:03+00:00.

## Original issue post

The body below is reproduced verbatim from the original issue post as
returned by GitHub at retrieval time. It may include upstream edits,
mistakes, HTML, and externally hosted attachments. It is not a
reconstruction of the issue's initial, pre-edit revision.

Source: https://github.com/Qiskit/qiskit/issues/16164 by @Timeless-hep.

<details>
<summary>Full original issue text</summary>

### Environment

- **Qiskit version**: 2.4.1
- **Python version**: 3.13.13
- **Operating system**: MacOS


### What is happening?

The CommutationChecker incorrectly evaluates the commutation relation between topological exchange gates (like SwapGate or iSwapGate) and asymmetric controlled continuous rotation gates (like CRZGate). It returns True (commutes) when they mathematically do NOT commute.

Because core transpiler passes rely on this checker, this underlying logic flaw leads to silent miscompilation. Specifically, passes like CommutativeInverseCancellation will illegally push gates past each other and erroneously cancel required topological routing gates. This completely alters the physical meaning and the unitary matrix of the circuit without raising any warnings or errors.

### How can we reproduce the issue?

Here is a minimal reproducible example demonstrating how this bug silently corrupts the transpilation process.

We construct a SWAP -> CRZ -> SWAP sequence, which mathematically represents a direction-reversed CRZ gate. However, the CommutativeInverseCancellation pass incorrectly assumes CRZ commutes with SWAP, illegally bringing the two SWAP gates together and cancelling them out.
# code
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import CommutativeInverseCancellation
import numpy as np


qc = QuantumCircuit(2)
qc.swap(0, 1)
qc.crz(1.0, 0, 1)
qc.swap(0, 1)


out = PassManager([CommutativeInverseCancellation()]).run(qc)


print(out.count_ops()) 
print(np.allclose(Operator(qc).data, Operator(out).data)) 
print(out)

### What should happen?

The transpiler pass should recognize that SWAP and CRZ do NOT commute, so the two SWAP gates in the sequence must NOT be canceled. 

### Any suggestions?

The bug appears to originate in the Rust backend: qiskit/circuit/commutation_checker.rs. In the build_supported_rotations() mapping, CRZ is mapped to its discrete generator, the CZ gate.
While CZ is perfectly symmetric ($CZ_{0,1} = CZ_{1,0}$) and thus genuinely commutes with SWAP, CRZ is asymmetric. The checker incorrectly allows CRZ to inherit the spatial symmetry of CZ, leading to the false positive. It's better to consider removing the CRZ -> CZ mapping from build_supported_rotations(), or introducing an explicit symmetry check in the Rust backend to ensure that asymmetric controlled rotations cannot inherit the commutation rules of symmetric topological configurations.

</details>

## Issue discussion, including closing and resolving comments

All fetched issue comments are preserved below in upstream chronological
order, including any closing or resolving comments. Comments are
third-party statements, not automatically verified benchmark claims.

### Comment 4419525434 by @Cryoris

Posted: 2026-05-11T10:02:31Z. Updated: 2026-05-11T10:02:31Z.

Source: https://github.com/Qiskit/qiskit/issues/16164#issuecomment-4419525434

<details>
<summary>Full comment by @Cryoris</summary>

Thanks for the report, that's definitely a bug. This actually goes deeper and affects all reductions from controlled rotations to fixed-controlled gates, since we can always construct some gate that commutes with `C<Pauli>` but does not with `CR<Pauli>(some angle)`. For example
```python
from qiskit.circuit import CommutationChecker, QuantumCircuit, library
from qiskit.quantum_info import Operator

# Example from this issue
# swap = library.SwapGate()
# cr = library.CRZGate(0.2)

# X-version of this......
some_swap = QuantumCircuit(2)
some_swap.h(1)
some_swap.swap(0, 1)
some_swap.h(1)

swap = library.UnitaryGate(Operator(some_swap).data)
cr = library.CRXGate(1.2)

cc = CommutationChecker()
print(cc.commute(swap, [0, 1], [], cr, [0, 1], []))  # reduces CRX -> CX, prints `True`

cr_matrix = library.UnitaryGate(cr.to_matrix())
print(cc.commute(swap, [0, 1], [], cr_matrix, [0, 1], []))  # sanity check, prints `False`
```
This reduction seems to only be correct for `CPhase -> CZ`. We should be able to leverage the newly added standard gate exponents of #15925 to handle this correctly.

</details>

### Comment 4422837712 by @alexanderivrii

Posted: 2026-05-11T16:50:30Z. Updated: 2026-05-11T16:50:30Z.

Source: https://github.com/Qiskit/qiskit/issues/16164#issuecomment-4422837712

<details>
<summary>Full comment by @alexanderivrii</summary>

Thanks, indeed looking at the `standard_generators` and `convert_to_pauli_rotation` code, the generator for CRX is `1/2 (-ZX + IX)`, which is different from CX or its generator.

I do agree about `CPhase -> CZ` since both `CPhase(t) = exp(-i t/4 (-ZZ + ZI + IZ))` and `CZ = exp(-i pi/4 (ZZ - ZI - IZ))` have the same generator up to a constant.

</details>

### Comment 4427725696 by @ShellyGarion

Posted: 2026-05-12T05:57:45Z. Updated: 2026-05-12T05:57:45Z.

Source: https://github.com/Qiskit/qiskit/issues/16164#issuecomment-4427725696

<details>
<summary>Full comment by @ShellyGarion</summary>

It seems that some of the elements in this table are not correct:
https://github.com/Qiskit/qiskit/blob/02f052dfce3bb1fd9a5818d72d1536811acbaea4/crates/transpiler/src/commutation_checker.rs#L111

According to https://github.com/Qiskit/qiskit/blob/main/crates/circuit/src/standard_gate/standard_generators.rs, we can only use generators if they have the same standard generator (up to a coefficient).

This is correct for RX, RY, RZ, Phase, U1, CPhase.
But this does not hold for CRX, CRY and CRZ which have different standard generators than CX, CY and CZ respectively.

The immediate solution is to remove CRX, CRY and CRZ from `build_supported_rotations`.

</details>

### Comment 4429417716 by @Cryoris

Posted: 2026-05-12T10:05:30Z. Updated: 2026-05-12T10:05:30Z.

Source: https://github.com/Qiskit/qiskit/issues/16164#issuecomment-4429417716

<details>
<summary>Full comment by @Cryoris</summary>

Yeah this is what the issue description also already mentions:

> It's better to consider removing the CRZ -> CZ mapping from build_supported_rotations()

I don't think we can simply remove them, since CRX/CRY/CRZ are not in the commutation library and removing them would change the commutation checker's behavior (if the max. matrix qubits are set to below 2). Instead it would be nice to use the standard exponent path, or, as maybe less-preferred option, add these gates to the commutation library.

</details>


## Closure and reopening events

- 2026-06-08T21:20:01Z: closed by @alexanderivrii.

Closing an issue does not establish that a code fix was merged or released.

## Attribution and reuse

The original post and comments remain attributed to their upstream authors.
Their inclusion does not relicense them under this project's MIT license.
See [NOTICE](../../NOTICE). Machine-readable text and provenance are in
[source.json](source.json); curated version evidence is in
[the manifest](../manifest.json). Attachments are linked, not vendored.
