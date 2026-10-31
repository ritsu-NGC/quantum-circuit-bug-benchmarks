# Qiskit issue #16856: `FindCommutingPauliEvolutions` silently drops duplicate Pauli summands on the same qubit pair

## Benchmark metadata

| Field | Value |
| --- | --- |
| Original issue | https://github.com/Qiskit/qiskit/issues/16856 |
| Source repository | `Qiskit/qiskit` |
| Original author | @WindOctober |
| Reported Qiskit version(s) at the issue | `2.5.2`, `2.6.0.dev0+b6f798f` |
| Verified Qiskit version(s) containing the fix | `2.6.0` |
| Assessment | Confirmed bug |
| Upstream state at snapshot | closed (completed) |
| Created | 2026-08-28T11:43:42Z |
| Last upstream update | 2026-09-03T06:06:23Z |
| Closed | 2026-09-03T06:06:23Z |
| Retrieved | 2026-10-30T17:28:03+00:00 |

**Reported-version context:** Version(s) reported in the original issue environment; not a first-affected boundary.

**Assessment:** Duplicate Pauli summands are overwritten: 0.2*ZZ + 0.4*ZZ becomes 0.4*ZZ instead of 0.6*ZZ.

**Resolution:** Merged fix #16892 is verified in 2.6.0.

Reported versions are not an exhaustive affected range. A verified fixed
version is a published release containing the fix, not necessarily the
first fixed version across all maintenance branches. Historical fixed
release versions below 1.0 refer to `qiskit-terra`, not the old `qiskit`
metapackage. Reported versions retain their original distribution context.

## Fix and resolution evidence


### Verified fixed release: 2.6.0

- Distribution: `qiskit`.
- Original fix: https://github.com/Qiskit/qiskit/pull/16892.
- Included fix/backport PR: https://github.com/Qiskit/qiskit/pull/16892.
- Merged: 2026-09-03T06:06:22Z.
- Fix commit: `7e36091634262079010b16e47b6f0e3999bf5e65`.
- Published release: https://github.com/Qiskit/qiskit/releases/tag/2.6.0 (2026-10-16T12:04:54Z).
- Ancestry comparison: https://github.com/Qiskit/qiskit/compare/7e36091634262079010b16e47b6f0e3999bf5e65...2.6.0.
- Verification: Fix merge commit is an ancestor of the published release tag.
- Verified at: 2026-10-30T17:28:03+00:00.

## Original issue post

The body below is reproduced verbatim from the original issue post as
returned by GitHub at retrieval time. It may include upstream edits,
mistakes, HTML, and externally hosted attachments. It is not a
reconstruction of the issue's initial, pre-edit revision.

Source: https://github.com/Qiskit/qiskit/issues/16856 by @WindOctober.

<details>
<summary>Full original issue text</summary>

### Environment

- **Qiskit version**: 2.5.2  
  Also reproduced on `2.6.0.dev0+b6f798f` (`b6f798f0bd88965821a54bff3785323a39c3a6c5`)
- **Python version**: 3.12
- **Operating system**: Linux

### What is happening?

`FindCommutingPauliEvolutions` silently drops repeated Pauli summands when multiple terms act on the same qubit pair.

For example, the operator:

```text
0.2 * ZZ + 0.4 * ZZ
```

is equivalent to:

```text
0.6 * ZZ
```

However, after running `FindCommutingPauliEvolutions`, the generated commuting block contains only the term with coefficient `0.4`.

The term with coefficient `0.2` is silently lost.

This happens before `Commuting2qGateRouter` is invoked, so it is independent of the router's gate-layer representation or routing logic.

The problem is in `_decompose_to_2q()`, which constructs the following dictionary:

```python
required_paulis = {
    self._pauli_to_edge(pauli): (pauli, coeff)
    for pauli, coeff in zip(op.operator.paulis, op.operator.coeffs)
}
```

Relevant source:

https://github.com/Qiskit/qiskit/blob/b6f798f0bd88965821a54bff3785323a39c3a6c5/qiskit/transpiler/passes/routing/commuting_2q_gate_routing/pauli_2q_evolution_commutation.py#L104-L128

The dictionary key is only the qubit edge returned by `_pauli_to_edge()`.

Therefore, when two Pauli summands act on the same pair, the later dictionary entry replaces the earlier entry:

```text
(0, 1) -> (ZZ, 0.2)
(0, 1) -> (ZZ, 0.4)
```

The final dictionary contains only:

```text
(0, 1) -> (ZZ, 0.4)
```

`SparsePauliOp` provides `simplify()` as an explicit operation for combining duplicate terms. An unsimplified operator containing duplicate terms is therefore a representation that the pass must either preserve or intentionally simplify; it must not retain only the last coefficient.


### How can we reproduce the issue?


The following script first shows that the term is already missing immediately after `FindCommutingPauliEvolutions`.

It then runs the normal public routing pipeline to demonstrate the resulting semantic difference.

```python
import numpy as np

from qiskit import QuantumCircuit
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.quantum_info import Operator, Pauli, SparsePauliOp
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes.routing.commuting_2q_gate_routing import (
    Commuting2qGateRouter,
    FindCommutingPauliEvolutions,
    SwapStrategy,
)


# This operator intentionally contains two identical Pauli terms.
# It represents (0.2 + 0.4) * ZZ = 0.6 * ZZ.
operator = SparsePauliOp(
    ["ZZ", "ZZ"],
    coeffs=[0.2, 0.4],
)

source = QuantumCircuit(2)
source.append(
    PauliEvolutionGate(operator, time=1.0),
    [0, 1],
)


# ----------------------------------------------------------------------
# Run FindCommutingPauliEvolutions by itself.
# ----------------------------------------------------------------------

after_find = PassManager(
    [
        FindCommutingPauliEvolutions(),
    ]
).run(source)

block_operation = after_find.data[0].operation

block_times = sorted(
    float(node.op.time)
    for node in block_operation
)

print("operation after Find:", block_operation.name)
print("times stored in block:", block_times)


# ----------------------------------------------------------------------
# Run the normal public Find -> Router pipeline.
# ----------------------------------------------------------------------

routed = PassManager(
    [
        FindCommutingPauliEvolutions(),
        Commuting2qGateRouter(
            SwapStrategy.from_line([0, 1])
        ),
    ]
).run(source)

routed_times = sorted(
    float(instruction.operation.time)
    for instruction in routed.data
    if isinstance(instruction.operation, PauliEvolutionGate)
)

print("times after routing:", routed_times)


# Expected circuit: exp(-i * 0.6 * ZZ)
combined = QuantumCircuit(2)
combined.append(
    PauliEvolutionGate(Pauli("ZZ"), time=0.6),
    [0, 1],
)

# Incorrect circuit actually produced: exp(-i * 0.4 * ZZ)
only_last = QuantumCircuit(2)
only_last.append(
    PauliEvolutionGate(Pauli("ZZ"), time=0.4),
    [0, 1],
)

source_operator = Operator(source)
routed_operator = Operator(routed)
combined_operator = Operator(combined)
only_last_operator = Operator(only_last)

print(
    "input equivalent to combined 0.6 evolution:",
    source_operator.equiv(combined_operator),
)
print(
    "routed circuit equivalent to input:",
    routed_operator.equiv(source_operator),
)
print(
    "routed circuit equivalent to only the 0.4 term:",
    routed_operator.equiv(only_last_operator),
)
print(
    "maximum matrix difference from input:",
    np.max(np.abs(routed_operator.data - source_operator.data)),
)
```

On the affected implementation, the relevant output is:

```text
operation after Find: commuting_2q_block
times stored in block: [0.4]
times after routing: [0.4]
input equivalent to combined 0.6 evolution: True
routed circuit equivalent to input: False
routed circuit equivalent to only the 0.4 term: True
maximum matrix difference from input: approximately 0.199667
```

The `0.2` term is already absent immediately after running only:

```python
FindCommutingPauliEvolutions()
```

The router subsequently receives a block containing only the `0.4` evolution, so the loss is caused by `FindCommutingPauliEvolutions`, not by the router.


### What should happen?

`FindCommutingPauliEvolutions` should preserve the complete operator represented by the input `PauliEvolutionGate`.

For this example, it may either preserve both terms:

```text
0.2 * ZZ
0.4 * ZZ
```

or intentionally combine them into:

```text
0.6 * ZZ
```

In either case, the following should hold after the public pass pipeline:

```python
Operator(routed).equiv(Operator(source))
```

The result should be:

```text
True
```

Silently retaining only the last term is not semantics-preserving.


### Any suggestions?

`_decompose_to_2q()` should not store a single Pauli term per edge.

One option is to preserve every summand in a list:

```python
required_paulis = []

for pauli, coeff in zip(op.operator.paulis, op.operator.coeffs):
    required_paulis.append(
        (self._pauli_to_edge(pauli), pauli, coeff)
    )
```

Alternatively, identical Pauli terms may be combined deliberately by summing their coefficients before constructing the two-qubit evolution gates.

For example, the pass could normalize the operator using an appropriate simplification step, or accumulate coefficients using both the edge and complete Pauli value as the key.

A dictionary keyed only by the qubit edge is insufficient because it discards multiplicity.

A regression test should pass a `PauliEvolutionGate` containing:

```python
SparsePauliOp(
    ["ZZ", "ZZ"],
    coeffs=[0.2, 0.4],
)
```

and verify that the transformed circuit remains equivalent to an evolution generated by:

```text
0.6 * ZZ
```

</details>

## Issue discussion, including closing and resolving comments

All fetched issue comments are preserved below in upstream chronological
order, including any closing or resolving comments. Comments are
third-party statements, not automatically verified benchmark claims.

No issue comments were present at retrieval time.

## Closure and reopening events

- 2026-09-03T06:06:23Z: closed by @alexanderivrii.

Closing an issue does not establish that a code fix was merged or released.

## Attribution and reuse

The original post and comments remain attributed to their upstream authors.
Their inclusion does not relicense them under this project's MIT license.
See [NOTICE](../../NOTICE). Machine-readable text and provenance are in
[source.json](source.json); curated version evidence is in
[the manifest](../manifest.json). Attachments are linked, not vendored.
