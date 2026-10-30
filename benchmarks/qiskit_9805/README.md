# Qiskit issue #9805: `QuantumCircuit.qasm` cannot handle nested gates with different parameters

## Benchmark metadata

| Field | Value |
| --- | --- |
| Original issue | https://github.com/Qiskit/qiskit/issues/9805 |
| Source repository | `Qiskit/qiskit` |
| Original author | @Durd3nT |
| Reported Qiskit version(s) at the issue | `0.24.0.dev0+3005806` |
| Verified Qiskit version(s) containing the fix | `0.24.0` |
| Assessment | Confirmed bug |
| Upstream state at snapshot | closed (completed) |
| Created | 2023-03-16T16:02:52Z |
| Last upstream update | 2023-04-17T22:56:16Z |
| Closed | 2023-04-17T22:56:16Z |
| Retrieved | 2026-10-30T17:28:03+00:00 |

**Reported-version context:** Version(s) reported in the original issue environment; not a first-affected boundary.

**Assessment:** Nested QASM2 gate definitions with distinct coefficients collide, causing invalid export or evaluation with the wrong nested definition.

**Resolution:** Merged exporter rewrite #9953 is verified in qiskit-terra 0.24.0.

Reported versions are not an exhaustive affected range. A verified fixed
version is a published release containing the fix, not necessarily the
first fixed version across all maintenance branches. Historical fixed
release versions below 1.0 refer to `qiskit-terra`, not the old `qiskit`
metapackage. Reported versions retain their original distribution context.

## Fix and resolution evidence


### Verified fixed release: 0.24.0

- Distribution: `qiskit-terra`.
- Original fix: https://github.com/Qiskit/qiskit/pull/9953.
- Included fix/backport PR: https://github.com/Qiskit/qiskit/pull/9953.
- Merged: 2023-04-17T22:56:12Z.
- Fix commit: `639bd58fcbd0ef9505be61ab1c8e4ce95fba6d85`.
- Published release: https://github.com/Qiskit/qiskit/releases/tag/0.24.0 (2023-05-04T18:24:49Z).
- Ancestry comparison: https://github.com/Qiskit/qiskit/compare/639bd58fcbd0ef9505be61ab1c8e4ce95fba6d85...0.24.0.
- Verification: Fix merge commit is an ancestor of the published release tag.
- Verified at: 2026-10-30T17:28:03+00:00.

## Original issue post

The body below is reproduced verbatim from the original issue post as
returned by GitHub at retrieval time. It may include upstream edits,
mistakes, HTML, and externally hosted attachments. It is not a
reconstruction of the issue's initial, pre-edit revision.

Source: https://github.com/Qiskit/qiskit/issues/9805 by @Durd3nT.

<details>
<summary>Full original issue text</summary>

### Environment

- **Qiskit Terra version**:  0.24.0.dev0+3005806
- **Python version**: 3.9.13
- **Operating system**: MacOS Ventura 13.2.1


### What is happening?

Having a `QuantumCircuit` containing nested gates, such as `PauliEvolutionGate`, with different parameters leads to issues when translating these circuits to qasm strings. Qasm defines a new gate for these nested gates with parameters but discards gates that contain the same nested gates with different parameters.

The resulting qasm string looks like this, containing a duplicate definition of the gates `exp_it_ZZ_` and `exp_it_XI_`:
```python
OPENQASM 2.0;
include "qelib1.inc";
gate exp_it_ZZ_ q0,q1 { rzz(20.0) q0,q1; }
gate exp_it_XI_ q0,q1 { rx(20.0) q1; }
gate exp_it_ZZ_ q0,q1 { rzz(2.0) q0,q1; }
gate exp_it_XI_ q0,q1 { rx(2.0) q1; }
gate gate_PauliEvolution(param0) q0,q1 { exp_it_XI_ q0,q1; exp_it_ZZ_ q0,q1; }
gate gate_PauliEvolution_140709141623472(param0) q0,q1 { exp_it_XI_ q0,q1; exp_it_ZZ_ q0,q1; }
qreg q[2];
h q[0];
h q[1];
gate_PauliEvolution(1.0) q[0],q[1];
gate_PauliEvolution_140709141623472(1.0) q[0],q[1];
```
The result is that only one definition of these gates is used, ignoring the fact that they are used multiple times with different parameterizations.

This is a problem when sending such circuits to the cloud and results in the wrong circuits bein evaluated.

### How can we reproduce the issue?

```python
from qiskit.quantum_info import SparsePauliOp
from qiskit import QuantumCircuit
from qiskit.circuit.library import PauliEvolutionGate

circ = QuantumCircuit(1)
evo_gate1 = PauliEvolutionGate(
    SparsePauliOp(["X", "Z"], [1, 1]),
    1
)

evo_gate2 = PauliEvolutionGate(
    SparsePauliOp(["X", "Z"], [10, 10]),
    1
)

circ.append(evo_gate1, circ.qubits)
circ.append(evo_gate2, circ.qubits)

qasm_str = circ.qasm()
rebuilt = QuantumCircuit.from_qasm_str(qasm_str)
```

Output:
`qiskit.qasm.exceptions.QasmError: "Duplicate declaration for gate 'exp_it_Z_' at line 5, file .\nPrevious occurrence at line 3, file "`

### What should happen?

Qasm should define distinct gates for each nested gate with a distinct parameterization.

### Any suggestions?

_No response_

</details>

## Issue discussion, including closing and resolving comments

All fetched issue comments are preserved below in upstream chronological
order, including any closing or resolving comments. Comments are
third-party statements, not automatically verified benchmark claims.

### Comment 1472264552 by @Durd3nT

Posted: 2023-03-16T16:06:33Z. Updated: 2023-03-16T16:09:53Z.

Source: https://github.com/Qiskit/qiskit/issues/9805#issuecomment-1472264552

<details>
<summary>Full comment by @Durd3nT</summary>

The code below shows that this issue is more deeply rooted and does not only apply to the `PauliEvolutionGate`, but to nested gates generally.

```python
from qiskit import QuantumCircuit
from qiskit.circuit import Gate

class Internal(Gate):
    def __init__(self, x):
        super().__init__("internal", 1, [x], label=f"I'm {x:.2f}")

    def _define(self):
        definition = QuantumCircuit(1)
        definition.rx(self.params[0], 0)
        self._definition = definition

class MyGate(Gate):
    def __init__(self, x):
        super().__init__("breakstuff", 1, [x], label=f"I'm {x:.2f}")

    def _define(self):
        definition = QuantumCircuit(1)
        definition.append(Internal(self.params[0]), [0])
        self._definition = definition


gate1, gate2 = MyGate(1), MyGate(2)
circ = QuantumCircuit(1)
circ.append(gate1, [0])
circ.append(gate2, [0])


qasm_str = circ.qasm()
print(qasm_str)
rebuilt = QuantumCircuit.from_qasm_str(qasm_str)
```

Output Qasm string from print statement:
```python
OPENQASM 2.0;
include "qelib1.inc";
gate internal(param0) q0 { rx(2.0) q0; }
gate internal(param0) q0 { rx(1.0) q0; }
gate breakstuff(param0) q0 { internal(1.0) q0; }
gate breakstuff_4533491840(param0) q0 { internal(2.0) q0; }
qreg q[1];
breakstuff(1.0) q[0];
breakstuff_4533491840(2.0) q[0];
```

Error raised in the last line of code (same as above):
`
qiskit.qasm.exceptions.QasmError: "Duplicate declaration for gate 'internal' at line 4, file .\nPrevious occurrence at line 3, file "`

</details>

### Comment 1490113862 by @1ucian0

Posted: 2023-03-30T11:08:44Z. Updated: 2023-03-30T11:08:44Z.

Source: https://github.com/Qiskit/qiskit/issues/9805#issuecomment-1490113862

<details>
<summary>Full comment by @1ucian0</summary>

It seems like the exporter does not check the namespace of declared gates.

</details>


## Closure and reopening events

- 2023-04-17T22:56:17Z: closed by @1ucian0.

Closing an issue does not establish that a code fix was merged or released.

## Attribution and reuse

The original post and comments remain attributed to their upstream authors.
Their inclusion does not relicense them under this project's MIT license.
See [NOTICE](../../NOTICE). Machine-readable text and provenance are in
[source.json](source.json); curated version evidence is in
[the manifest](../manifest.json). Attachments are linked, not vendored.
