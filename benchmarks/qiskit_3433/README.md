# Qiskit issue #3433: Incorrect transpilation of phase-gadgets with small angles on optimisation level 2 and 3

## Benchmark metadata

| Field | Value |
| --- | --- |
| Original issue | https://github.com/Qiskit/qiskit/issues/3433 |
| Source repository | `Qiskit/qiskit` |
| Original author | @alexcowtan |
| Reported Qiskit version(s) at the issue | `0.10.0` |
| Verified Qiskit version(s) containing the fix | Not verified |
| Assessment | Confirmed bug |
| Upstream state at snapshot | open |
| Created | 2019-11-07T21:35:42Z |
| Last upstream update | 2024-11-21T16:42:13Z |
| Closed | Not closed |
| Retrieved | 2026-10-30T17:28:03+00:00 |

**Reported-version context:** Version(s) reported in the original issue environment; not a first-affected boundary.

**Assessment:** A small-angle ZZ gadget loses its CX gates but retains its RZ. Expected behavior is to preserve the gadget or consistently approximate the entire gadget away.

**Resolution:** Issue remains open. Discussion connects the behavior to inconsistent identity thresholds, but no specific released fix for this report is verified. Closed/unmerged #3658 is not a shipped fix.

Reported versions are not an exhaustive affected range. A verified fixed
version is a published release containing the fix, not necessarily the
first fixed version across all maintenance branches. Historical fixed
release versions below 1.0 refer to `qiskit-terra`, not the old `qiskit`
metapackage. Reported versions retain their original distribution context.

## Fix and resolution evidence

No merged fix or fixed release was verified; see the full discussion below.

## Original issue post

The body below is reproduced verbatim from the original issue post as
returned by GitHub at retrieval time. It may include upstream edits,
mistakes, HTML, and externally hosted attachments. It is not a
reconstruction of the issue's initial, pre-edit revision.

Source: https://github.com/Qiskit/qiskit/issues/3433 by @alexcowtan.

<details>
<summary>Full original issue text</summary>

### Information

- **Qiskit Terra version**: 0.10.0
- **Python version**: 3.6.9
- **Operating system**: MacOS Mojave

### What is the current behavior?

If there is a ZZ pauli exponential with a small angle, Qiskit will remove the CXs and leave the small angle. (It will also do this if the Xs are not controlled)

### Steps to reproduce the problem

Create a `QuantumCircuit` with an Rz nested between the targets of two CX gates. See this qasm:

```
OPENQASM 2.0;
include "qelib1.inc";

qreg q[2];
cx q[1],q[0];
rz(3.978863630138309e-07*pi) q[0];
cx q[1],q[0];
```

Then load the qasm into qiskit and run an optimisation pass:
```
from qiskit import QuantumCircuit
from qiskit.compiler import transpile
from qiskit.transpiler import CouplingMap

qsc = QuantumCircuit.from_qasm_file("test_qiskit.qasm")
basis_gates = ['u1','u2','u3','cx']
cm = None

qsc2 = transpile(qsc,basis_gates=basis_gates,coupling_map=cm,optimization_level=2)
print(qsc2)
```

### What is the expected behavior?

Either the circuit should be left unchanged or, if the angle is considered to be too small to be worth leaving in and it should be approximated away, then remove the entire phase-gadget. I'm not sure whether this was a design choice or a bug, as I don't really understand how it is possible to write this behaviour by accident.

### Suggested solutions

See above.

</details>

## Issue discussion, including closing and resolving comments

All fetched issue comments are preserved below in upstream chronological
order, including any closing or resolving comments. Comments are
third-party statements, not automatically verified benchmark claims.

### Comment 552926988 by @kdk

Posted: 2019-11-12T14:52:40Z. Updated: 2019-11-12T14:52:40Z.

Source: https://github.com/Qiskit/qiskit/issues/3433#issuecomment-552926988

<details>
<summary>Full comment by @kdk</summary>

Good catch, this looks like an issue in the `CommutationAnalysis` pass ( https://github.com/Qiskit/qiskit-terra/blob/0e332a9/qiskit/transpiler/passes/commutation_analysis.py#L121 ).

(In #2442 , the `CommutationAnalysis` pass was refactored to use `qiskit.quantum_info.Operator` to determine if two instructions commuted, which in turn reduced its `atol` from `1e-10` to `1e-8`. The check for this circuit still would've failed though, due to the default `rtol=1e-5`.)

Reducing the `rtol` on the operator comparison would be one way to fix this (the current comparison passes because of the `rtol` on `np.isclose(1, 1+1.25e-6j)`) but maybe there's a more numerically robust way to determine commutativity than `np.allclose`. @DanPuzzuoli @chriseclectic ?

</details>

### Comment 552938915 by @DanPuzzuoli

Posted: 2019-11-12T15:19:21Z. Updated: 2019-11-12T15:19:21Z.

Source: https://github.com/Qiskit/qiskit/issues/3433#issuecomment-552938915

<details>
<summary>Full comment by @DanPuzzuoli</summary>

I think just lowering the tolerance makes sense... it seems efficient, and entry-wise comparison is the most stringent distance measure I think you can get for distances between matrices.

Only other consideration is if you want to allow for unitaries that are the same up to global phase to pass the test.

</details>

### Comment 569762715 by @ajavadia

Posted: 2019-12-30T18:51:54Z. Updated: 2019-12-30T18:51:54Z.

Source: https://github.com/Qiskit/qiskit/issues/3433#issuecomment-569762715

<details>
<summary>Full comment by @ajavadia</summary>

I think the desired behavior is to have the CXs cancelled *and* the Rz removed. 
`CX.RZ(theta).CX` is equal to `RZZ(theta)` which for tiny angles should just be identity.
So I would say the commutation detection is correct, we just do not have a mechanism to remove tiny rotations from the circuit yet. I can work on this as part of #3658 

</details>

### Comment 994597213 by @mrvee-qC

Posted: 2021-12-15T09:55:12Z. Updated: 2021-12-15T09:55:12Z.

Source: https://github.com/Qiskit/qiskit/issues/3433#issuecomment-994597213

<details>
<summary>Full comment by @mrvee-qC</summary>

# Update for Santa:elf:- QGoGP

✅ Issue reproducible! Removes CX's and keeps the small angle when optimized with level 2 or 3 as mentioned by OP. Optimization level 1 has expected behavior and does not change the circuit significantly. PR #3658 has a few checks to be passed which proposes a fix for this.
#### OP's Code -

```
qasm = """
OPENQASM 2.0;
include "qelib1.inc";

qreg q[2];
cx q[1],q[0];
rz(3.978863630138309e-07*pi) q[0];
cx q[1],q[0];
"""
from qiskit import QuantumCircuit
from qiskit.compiler import transpile
from qiskit.transpiler import CouplingMap

qsc = QuantumCircuit.from_qasm_str(qasm)
basis_gates = ['u1','u2','u3','cx']
cm = None
print(qsc)

qsc2 = transpile(qsc,basis_gates=basis_gates,coupling_map=cm,optimization_level=2)
print(qsc2)
```
#### Original Circuit
```
     ┌───┐┌──────────────┐┌───┐
q_0: ┤ X ├┤ Rz(1.25e-06) ├┤ X ├
     └─┬─┘└──────────────┘└─┬─┘
q_1: ──■────────────────────■──


```
#### Transpiled circuit (Level 2 and 3)
```
global phase: 2π
     ┌─────────────────────────┐
q_0: ┤ U1(1.24999687500781e-6) ├
     └─────────────────────────┘
q_1: ───────────────────────────
              
```
Will update comment/add more comments if cause is found/fixed!

> Python version 3.9.7
> qiskit-terra version: 0.19.1





</details>

### Comment 2491742368 by @Cryoris

Posted: 2024-11-21T16:42:12Z. Updated: 2024-11-21T16:42:12Z.

Source: https://github.com/Qiskit/qiskit/issues/3433#issuecomment-2491742368

<details>
<summary>Full comment by @Cryoris</summary>

We're currently using 2 different standards when it comes to checking if something behaves as identity:
1. `RemoveIdentityEquivalent` (and others) remove a gate, if the gate fidelity is 1 up to floating point precision
2. the commutation checker assumes a rotation gate commutes with anything, if the rotation angle is 0 (mod 2pi) up to a tolerance of 1e-5

We should be using 1. consistently, as it has a well-defined effect on the outcome that generalizes beyond rotations as well.

</details>


## Closure and reopening events

No closure or reopening events were present in the fetched timeline.

Closing an issue does not establish that a code fix was merged or released.

## Attribution and reuse

The original post and comments remain attributed to their upstream authors.
Their inclusion does not relicense them under this project's MIT license.
See [NOTICE](../../NOTICE). Machine-readable text and provenance are in
[source.json](source.json); curated version evidence is in
[the manifest](../manifest.json). Attachments are linked, not vendored.
