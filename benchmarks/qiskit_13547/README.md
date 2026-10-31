# Qiskit issue #13547: Incorrect transpilation with RY gate with a small angle

## Benchmark metadata

| Field | Value |
| --- | --- |
| Original issue | https://github.com/Qiskit/qiskit/issues/13547 |
| Source repository | `Qiskit/qiskit` |
| Original author | @t-imamichi |
| Reported Qiskit version(s) at the issue | `1.3.0`, `2.0.0.dev0+841cb29`, `1.2.4` |
| Verified Qiskit version(s) containing the fix | `2.0.0` |
| Assessment | Confirmed bug |
| Upstream state at snapshot | closed (completed) |
| Created | 2024-12-10T13:58:53Z |
| Last upstream update | 2025-03-06T00:34:44Z |
| Closed | 2025-03-06T00:34:43Z |
| Retrieved | 2026-10-30T17:28:03+00:00 |

**Reported-version context:** The first RY example fails on 1.3.0/main but passes on 1.2.4. The second PauliEvolutionGate example also fails on 1.2.4. The development-version string comes from the original output.

**Assessment:** Small-angle RY/Pauli evolution can be treated inconsistently by commutation and identity-removal passes, leading to invalid entangling-gate cancellation.

**Resolution:** Merged fix #13874 aligns commutation-check fidelity thresholds and is verified in 2.0.0.

Reported versions are not an exhaustive affected range. A verified fixed
version is a published release containing the fix, not necessarily the
first fixed version across all maintenance branches. Historical fixed
release versions below 1.0 refer to `qiskit-terra`, not the old `qiskit`
metapackage. Reported versions retain their original distribution context.

## Fix and resolution evidence


### Verified fixed release: 2.0.0

- Distribution: `qiskit`.
- Original fix: https://github.com/Qiskit/qiskit/pull/13874.
- Included fix/backport PR: https://github.com/Qiskit/qiskit/pull/13874.
- Merged: 2025-03-06T00:34:42Z.
- Fix commit: `d2f486180ffbf410150961ccf35fa8984a3324c9`.
- Published release: https://github.com/Qiskit/qiskit/releases/tag/2.0.0 (2025-03-31T19:17:28Z).
- Ancestry comparison: https://github.com/Qiskit/qiskit/compare/d2f486180ffbf410150961ccf35fa8984a3324c9...2.0.0.
- Verification: Fix merge commit is an ancestor of the published release tag.
- Verified at: 2026-10-30T17:28:03+00:00.

## Original issue post

The body below is reproduced verbatim from the original issue post as
returned by GitHub at retrieval time. It may include upstream edits,
mistakes, HTML, and externally hosted attachments. It is not a
reconstruction of the issue's initial, pre-edit revision.

Source: https://github.com/Qiskit/qiskit/issues/13547 by @t-imamichi.

<details>
<summary>Full original issue text</summary>

### Environment

- **Qiskit version**: 1.3.0, main
- **Python version**: 3.12.8
- **Operating system**: macOS 15.1.1


### What is happening?

Transpilation with optimization level 2 and 3 results in a incorrect circuit for circuits with RY gate with a small angle.

Note that the following code does not have issue with 1.2.4.

### How can we reproduce the issue?

```python
from qiskit import QuantumCircuit, generate_preset_pass_manager, __version__
from qiskit.quantum_info import Operator

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.ry(1e-6, 1)
qc.cx(0, 1)

pm = generate_preset_pass_manager(optimization_level=2)
tqc = pm.run(qc)

print(__version__)
print(qc)
print(tqc)

print("equivalent?", Operator(qc).equiv(tqc))
```

```
2.0.0.dev0+841cb29
     ┌───┐
q_0: ┤ H ├──■─────────────────■──
     └───┘┌─┴─┐┌───────────┐┌─┴─┐
q_1: ─────┤ X ├┤ Ry(1e-06) ├┤ X ├
          └───┘└───────────┘└───┘
         ┌───┐
q_0: ────┤ H ├────
     ┌───┴───┴───┐
q_1: ┤ Ry(1e-06) ├
     └───────────┘
equivalent? False
```

```
1.3.0
     ┌───┐
q_0: ┤ H ├──■─────────────────■──
     └───┘┌─┴─┐┌───────────┐┌─┴─┐
q_1: ─────┤ X ├┤ Ry(1e-06) ├┤ X ├
          └───┘└───────────┘└───┘
         ┌───┐
q_0: ────┤ H ├────
     ┌───┴───┴───┐
q_1: ┤ Ry(1e-06) ├
     └───────────┘
equivalent? False
```

```
1.2.4
     ┌───┐
q_0: ┤ H ├──■─────────────────■──
     └───┘┌─┴─┐┌───────────┐┌─┴─┐
q_1: ─────┤ X ├┤ Ry(1e-06) ├┤ X ├
          └───┘└───────────┘└───┘
     ┌───┐
q_0: ┤ H ├──■─────────────────■──
     └───┘┌─┴─┐┌───────────┐┌─┴─┐
q_1: ─────┤ X ├┤ Ry(1e-06) ├┤ X ├
          └───┘└───────────┘└───┘
equivalent? True
```

### What should happen?

The transpiled circuit should be same as the input circuit as 1.2.4 does.


### Another example

The following example fails with 1.2.4, 1.3.0, and main branch probably due to a similar reason.
```python
from qiskit import QuantumCircuit, generate_preset_pass_manager, __version__
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.quantum_info import SparsePauliOp, Operator

qc = QuantumCircuit(2)
op = SparsePauliOp(["XX"], coeffs=[1])
evo = PauliEvolutionGate(op, 1e-6)
qc.append(evo, qargs=qc.qregs[0])

pm = generate_preset_pass_manager(optimization_level=2, basis_gates=["rz", "cx", "sx", "x"])
tqc = pm.run(qc)

print(__version__)
print(qc)
print(tqc)

print("equivalent?", Operator(qc).equiv(tqc))
```

```
2.0.0.dev0+841cb29
     ┌─────────────────────┐
q_0: ┤0                    ├
     │  exp(-it XX)(1e-06) │
q_1: ┤1                    ├
     └─────────────────────┘
global phase: π/2

q_0: ─────────────────────────────────────────────────
     ┌─────────┐┌────┐┌─────────────┐┌────┐┌─────────┐
q_1: ┤ Rz(π/2) ├┤ √X ├┤ Rz(-3.1416) ├┤ √X ├┤ Rz(π/2) ├
     └─────────┘└────┘└─────────────┘└────┘└─────────┘
equivalent? False
```

```
1.2.4
     ┌─────────────────────┐
q_0: ┤0                    ├
     │  exp(-it XX)(1e-06) │
q_1: ┤1                    ├
     └─────────────────────┘
global phase: π/2

q_0: ─────────────────────────────────────────────────
     ┌─────────┐┌────┐┌─────────────┐┌────┐┌─────────┐
q_1: ┤ Rz(π/2) ├┤ √X ├┤ Rz(-3.1416) ├┤ √X ├┤ Rz(π/2) ├
     └─────────┘└────┘└─────────────┘└────┘└─────────┘
equivalent? False
```

### Any suggestions?

_No response_

</details>

## Issue discussion, including closing and resolving comments

All fetched issue comments are preserved below in upstream chronological
order, including any closing or resolving comments. Comments are
third-party statements, not automatically verified benchmark claims.

### Comment 2531864957 by @Cryoris

Posted: 2024-12-10T14:51:45Z. Updated: 2024-12-10T14:51:45Z.

Source: https://github.com/Qiskit/qiskit/issues/13547#issuecomment-2531864957

<details>
<summary>Full comment by @Cryoris</summary>

The true problem here is that cutoff tolerances are handled differently in different parts of Qiskit. For example, also on 1.2.4 a small enough angle will remove the CX gates (and the RY):
```python
     ┌───┐
q_0: ┤ H ├──■─────────────────■──
     └───┘┌─┴─┐┌───────────┐┌─┴─┐
q_1: ─────┤ X ├┤ Ry(2e-08) ├┤ X ├
          └───┘└───────────┘└───┘
global phase: 0
     ┌──────────────┐
q_0: ┤ U3(π/2,0,-π) ├
     └──────────────┘
q_1: ────────────────

```
but this seems to match the tolerance in `Operator.equiv`, since this prints
```
equivalent? True
```

We need to ensure that our processes use the same tolerance algorithm. I'm thinking of `CommutationAnalysis/Checker`, `UnitarySynthesis`, `RemoveIdentityEquivalent` and `Operator.equiv`, but maybe there are also others. From offline discussions, doing what `UnitarySynthesis` and `RemoveIdentityEquivalent` do seems to be the best-motivated choice: consider a gate as the identity, if the process fidelity is below machine epsilon.

</details>

### Comment 2533523718 by @t-imamichi

Posted: 2024-12-11T03:06:54Z. Updated: 2024-12-11T03:06:54Z.

Source: https://github.com/Qiskit/qiskit/issues/13547#issuecomment-2533523718

<details>
<summary>Full comment by @t-imamichi</summary>

Thank you for investigating this issue. The transpilation behavior change between 1.2.4 and 1.3.0 breaks our client code.
Could you suggest me how to configure transpiler to behave in the same way as 1.2.4?

</details>

### Comment 2535498276 by @Cryoris

Posted: 2024-12-11T10:45:55Z. Updated: 2024-12-11T10:45:55Z.

Source: https://github.com/Qiskit/qiskit/issues/13547#issuecomment-2535498276

<details>
<summary>Full comment by @Cryoris</summary>

Unfortunately there's currently no way to directly adjust the threshold below which the commutation checker assumes anything commutes with a rotation `Ry(epsilon)`. There's two suboptimal workarounds: 
* you could either increase the tolerance in `Operator.equiv`, or
* if you directly set the angle to 1e-6 (or whatever the angle is) you could first build the circuit with parameters in the `Ry`, then transpile, and then bind the values. The commutation checker will then not assume that things commute.

We're working on a fix but I don't think it will make it for 1.3.1, which is scheduled tomorrow. 

</details>

### Comment 2536025757 by @t-imamichi

Posted: 2024-12-11T13:42:06Z. Updated: 2024-12-11T13:42:06Z.

Source: https://github.com/Qiskit/qiskit/issues/13547#issuecomment-2536025757

<details>
<summary>Full comment by @t-imamichi</summary>

Thank you for your advice.

</details>


## Closure and reopening events

- 2025-03-06T00:34:44Z: closed by @mtreinish.

Closing an issue does not establish that a code fix was merged or released.

## Attribution and reuse

The original post and comments remain attributed to their upstream authors.
Their inclusion does not relicense them under this project's MIT license.
See [NOTICE](../../NOTICE). Machine-readable text and provenance are in
[source.json](source.json); curated version evidence is in
[the manifest](../manifest.json). Attachments are linked, not vendored.
