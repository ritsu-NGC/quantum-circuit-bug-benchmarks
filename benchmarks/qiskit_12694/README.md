# Qiskit issue #12694: Wrong export/import of OpenQASM2 with custom Unitary

## Benchmark metadata

| Field | Value |
| --- | --- |
| Original issue | https://github.com/Qiskit/qiskit/issues/12694 |
| Source repository | `Qiskit/qiskit` |
| Original author | @hJaffaliColibritd |
| Reported Qiskit version(s) at the issue | `1.1.0` |
| Verified Qiskit version(s) containing the fix | Not verified |
| Assessment | Mixed report: confirmed and disputed/expected aspects |
| Upstream state at snapshot | open |
| Created | 2024-06-30T10:21:44Z |
| Last upstream update | 2024-07-23T15:29:41Z |
| Closed | Not closed |
| Retrieved | 2026-10-30T17:28:03+00:00 |

**Reported-version context:** Version(s) reported in the original issue environment; not a first-affected boundary.

**Assessment:** The author acknowledges reversed matrix/qubit conventions. The maintainer explains that QASM2 does not preserve precise global phase. A real legacy 'u' import/export mismatch is mentioned, and later comments allege additional errors; do not classify all claims as a confirmed wrong-unitary circuit bug.

**Resolution:** Issue remains open; comments include explanations and a reported workaround. No released fix is verified for the combined report.

Reported versions are not an exhaustive affected range. A verified fixed
version is a published release containing the fix, not necessarily the
first fixed version across all maintenance branches. Historical fixed
release versions below 1.0 refer to `qiskit-terra`, not the old `qiskit`
metapackage. Reported versions retain their original distribution context.

## Fix and resolution evidence

- https://github.com/Qiskit/qiskit/issues/12694#issuecomment-2198579280
- https://github.com/Qiskit/qiskit/issues/12694#issuecomment-2200178184
- https://github.com/Qiskit/qiskit/issues/12694#issuecomment-2200368141

## Original issue post

The body below is reproduced verbatim from the original issue post as
returned by GitHub at retrieval time. It may include upstream edits,
mistakes, HTML, and externally hosted attachments. It is not a
reconstruction of the issue's initial, pre-edit revision.

Source: https://github.com/Qiskit/qiskit/issues/12694 by @hJaffaliColibritd.

<details>
<summary>Full original issue text</summary>

### Environment

- **Qiskit version**: Version: 1.1.0
- **Python version**: 3.9.5
- **Operating system**: Windows 10 Professional


### What is happening?

When we use the method `unitary` on a QuantumCircuit to define a custom gate from a unitary matrix for instance, and when we try to export the circuit to OpenQASM2 code using  `qasm2.dumps(qc)`, the custom gate we obtain in OpenQASM2 is not exactly corresponding to the unitary we passed as input. Either sometimes there is an additional phase, or the operations are wrong (sometimes i observe that if I take the inverse of the unitary, I get something looking like the right result).

Also sometimes when I use simple native gates like `u` in the openQASM code, and try to reconstruct a circuit from it, it tells me that "QASM2ParseError: "<input>:3,18: 'u' is not defined in this scope"".

### How can we reproduce the issue?

```Python
from qiskit import *
import qiskit
import numpy as np
from qiskit import qasm2

matrix = np.array([[0,1], [1,0]])

qc = QuantumCircuit(1)
qc.unitary(matrix, 0)
print(qc)
qasm_str = qasm2.dumps(qc)
print(qasm_str)

qc2 = qiskit.qasm2.loads(qasm_str)
print(qc2.qasm())

matrix = np.array([[0,0,1,0],[1,0,0,0],[0,1,0,0],[0,0,0,1]])
print(matrix)

qc3 = QuantumCircuit(2)
qc3.unitary(matrix, [0,1])
print(qc3)
qasm_str = qasm2.dumps(qc3)
print(qasm_str)

def u(a,b,c):
    cc = np.cos(a/2)
    ss = np.sin(a/2)
    return np.array([[np.exp(-1j*(b+c)/2)*cc,
                     -np.exp(-1j*(b-c)/2)*ss],
                     [np.exp(1j*(b-c)/2)*ss,
                     np.exp(1j*(b+c)/2)*cc]])

def cnot():
    return np.array([[1,0,0,0], [0,1,0,0], [0,0,0,1], [0,0,1,0]])

pi = np.pi
decomp_matrix = np.kron(u(pi/2,pi/2,pi/2), u(1.4512678518986026,pi/2,pi/2)).dot(cnot().dot(np.kron(u(pi/2,-pi,-pi/2),u(1.6894679218926363,0.014320349886192574,-1.4504171294224655)).dot(cnot().dot(np.kron(u(pi/2,pi/2,0),u(1.4512678518986009,pi/2,-pi))))))
print(np.round(decomp_matrix))
print(np.round(decomp_matrix.transpose()))
print(np.round(decomp_matrix.transpose())-matrix)
```

### What should happen?

A correct OpenQASM2 code should be exported that can be used on other devices wthout error, en respecting the OpenQASM2 synthax.

The possiblity to load OpenQASM2 code that contains native gate that are indeed included in qelib1.inc

### Any suggestions?

_No response_

</details>

## Issue discussion, including closing and resolving comments

All fetched issue comments are preserved below in upstream chronological
order, including any closing or resolving comments. Comments are
third-party statements, not automatically verified benchmark claims.

### Comment 2198579280 by @jakelishman

Posted: 2024-06-30T14:21:57Z. Updated: 2024-06-30T14:21:57Z.

Source: https://github.com/Qiskit/qiskit/issues/12694#issuecomment-2198579280

<details>
<summary>Full comment by @jakelishman</summary>

OpenQASM 2 as a language is only defined up to a global phase; there's no way to represent the precise global phase in it, so Qiskit will output a decomposition of the gate that is correct up to an undefined global phase.

I note that in your `cnot` function, you are using a different bit-labelling and/or Kronecker-product convention to Qiskit (compare `np.array(qiskit.circuit.library.CXGate())`, for example).  I haven't checked, but that could well be the discrepancy you are seeing. 

In OpenQASM 2, `u` is actually not in `qelib1.inc`, though due to a long-standing bug, Qiskit's OpenQASM 2 exporter hallucinates it as being there, which then causes problems with `qasm2.loads` (see #12124).  More immediately, you can do
```python
from qiskit import qasm2

qc = qasm2.loads(qasm_str, custom_instructions=qasm2.LEGACY_CUSTOM_INSTRUCTIONS)
```

</details>

### Comment 2200178184 by @hJaffaliColibritd

Posted: 2024-07-01T13:34:24Z. Updated: 2024-07-01T13:35:12Z.

Source: https://github.com/Qiskit/qiskit/issues/12694#issuecomment-2200178184

<details>
<summary>Full comment by @hJaffaliColibritd</summary>

Thank for the answer. Concerning the ordering of the qubits and the matrix you're right, I was doing it in the reversed order.

Concerning the global phase error, this is quite annoying, because I need to provide an exact state vector, and having any additional global phase can lead to mistakes if this gate is then controlled later. 
There is a way to define the global phase in OpenQASM2 by using a succession of `p` (phase shift) and `y` (pauli) instructions, but to do this I need to know exactly what the error/difference in terms of phase that the decomposition algorithm does when transforming unitary into a succession of native gates. 

For instance, even for a simple gate like the X gate, it introduces a global phase of -1. Is this due to the fact that you are mixiing several definitions of U/u in the decomposition ? 

</details>

### Comment 2200368141 by @jakelishman

Posted: 2024-07-01T14:49:44Z. Updated: 2024-07-01T14:49:44Z.

Source: https://github.com/Qiskit/qiskit/issues/12694#issuecomment-2200368141

<details>
<summary>Full comment by @jakelishman</summary>

OpenQASM 2 was never intended to represent global phase faithfully; you'll see that in things like the `qelib1.inc` header where `p` and `rz` have the exact same definition - we'll end up with inconsistent mathematics if we try to respect the standard phase difference between those while trying to treat other gates as having well-defined global phase.

OpenQASM 2 isn't really a suitable serialisation format for unitaries that might later be controlled because of this.  The language was only intended for complete programs, for which global phase is unobservable.  Qiskit (and other software) often uses this - since we can't faithfully represent the global phase in an output, nor assume what the user intended from an input, we just don't - we'd probably end up putting out unsound/inconsistent code if we tried.

For X: we don't commit to any particular decomposition of gates for output to OpenQASM 2, just that all decompositions will be correct up to a global phase on the operation.  Within Qiskit's transpiler we track global phase explicitly through all decompositions, though, so if you're after something that'll definitely work in OpenQASM 2 and has a known global phase, you can do
```python
from qiskit import tranpsile, QuantumCircuit

qc = QuantumCircuit(...)
# ... build the circuit ...

qc2 = transpile(qc, basis_gates=["u", "cx"])
```
then the output `qc2` will have a `global_phase` attribute that's well defined and will contain only the basis gates of the OpenQASM 2 language.

</details>

### Comment 2245514271 by @1ucian0

Posted: 2024-07-23T15:08:28Z. Updated: 2024-07-23T15:08:28Z.

Source: https://github.com/Qiskit/qiskit/issues/12694#issuecomment-2245514271

<details>
<summary>Full comment by @1ucian0</summary>

Can we close this one as _discussion solved_?

</details>

### Comment 2245557587 by @hJaffaliColibritd

Posted: 2024-07-23T15:25:52Z. Updated: 2024-07-23T15:29:41Z.

Source: https://github.com/Qiskit/qiskit/issues/12694#issuecomment-2245557587

<details>
<summary>Full comment by @hJaffaliColibritd</summary>

I actually found that the decomposition of a `unitary` and the export to QASM2 not only sometimes involve an additional global phase that doesn't change the sampling results, but that it can lead to totally wrong results, more important than just a phase difference.

Indeed, what is happening is that we add the unitary in the `QuantumCircuit` directly. When we export to OpenQASM2, the unitary is transpiled by means of 'u' and 'cx' gates. However, here, the 'u' gate is the usual unitary 'U' operator, that follows the definition given in OpenQASM3 (not phase in front of the top left cos(\theta) in the matrix).

When the export is done in OpenQASM2, the keyword 'u' is used without taking into account that there is a phase between the OpenQASM3 (and the `QuantumCircuit`) 'U', and the OpenQASM2 one. Here appears the extra phase at the one-qubit level.
However, if the unitary is a multi-qubit unitary, 'cx' gates may appear on the way when decomposed. The phase will propagate and will affect other qubits, resulting in a much more important error than the previous one. 

One our user side, we found a work-around to this problem, which is to manually correct the global phase after each one-qubit 'u' before applying any control gate. We cannot use the `GlobalPhaseGate` of Qiskit because it is not supported by the OpenQAM2 exporter, so we use the trick of applying a succession of single qubit phase and Pauli-Y gates.

One solution from the dev side, is to take into account that the `U` present in the QuantumCircuit is not the same `U` as the one manipulated in OpenQASM2, and then to do an extra effort either to decompose the circuit with the right 'u' definition, or to correct the local phases so they don't propagate.

Here is an example of work-around code in the context of our MPQP library : https://github.com/ColibrITD-SAS/mpqp/

```python
from qiskit import qasm2, transpile, QuantumCircuit
from qiskit.circuit import CircuitInstruction

def apply_gphase(circuit: QuantumCircuit, global_phase: float, qubit: int) -> None:
	"""
	Apply a global phase to a given circuit by appending the right sequence of Phase and Y gates on the qubit
	given in parameter.

	Args:
		circuit: QuantumCircuit to which we want to add the global phase.
		global_phase: Global phase g parametrizing the global phase `e^{i \times g}` to add.
		qubit: Index of the qubit on which the sequence of gates will be applied.

	"""
	# circuit.append(GlobalPhaseGate(-global_phase)) --> We cannot use it because OQASM2 doesn't not support
	circuit.p(global_phase, qubit)
	circuit.y(qubit)
	circuit.p(global_phase, qubit)
	circuit.y(qubit)

def replace_custom_gate(custom_unitary: CircuitInstruction, nb_qubits: int) -> QuantumCircuit:
	"""
	Decompose and replace the (custom) qiskit unitary given in parameter by a ``QuantumCircuit`` composed of
	``U`` and ``CX`` gates, with the global phase (related to usage of ``u`` in OpenQASM2) corrected.

	Args:
		custom_unitary: Qiskit CircuitInstruction containing the custom unitary operator.
		nb_qubits: Number of qubits of the circuit from which the unitary instruction was taken.

	Returns:
		QuantumCircuit containing the decomposition of the unitary in terms of native gates ``U`` and ``CX``,
		with a correction in the global phase of each ``U`` operator.
	"""
	transpilation_circuit = QuantumCircuit(nb_qubits)
	transpilation_circuit.append(custom_unitary)
	transpiled = transpile(transpilation_circuit, basis_gates=['u', 'cx'])
	replace_circuit = QuantumCircuit(nb_qubits)
	for instr in transpiled.data:
		replace_circuit.append(instr)
		if instr.operation.name == 'u':
			phi = instr.operation.params[1]
			gamma = instr.operation.params[2]
			apply_gphase(replace_circuit, -(phi+gamma)/2, instr.qubits[0]._index)
	return replace_circuit

qiskit_circ = # The circuit containing some custom unitaries

new_circuit = QuantumCircuit(qiskit_circ.num_qubits, qiskit_circ.num_clbits)
for instruction in qiskit_circ.data:
	if instruction.operation.name == 'unitary':
		new_circuit.compose(replace_custom_gate(instruction, qiskit_circ.num_qubits), inplace=True)
	else:
		new_circuit.append(instruction)

qasm_str = qasm2.dumps(new_circuit)
```

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
