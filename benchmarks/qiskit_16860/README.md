# Qiskit issue #16860: `FindCommutingPauliEvolutions` ignores gate qargs and changes asymmetric Pauli evolutions

## Benchmark metadata

| Field | Value |
| --- | --- |
| Original issue | https://github.com/Qiskit/qiskit/issues/16860 |
| Source repository | `Qiskit/qiskit` |
| Original author | @WindOctober |
| Reported Qiskit version(s) at the issue | `2.5.2`, `2.6.0.dev0+b6f798f` |
| Verified Qiskit version(s) containing the fix | Not verified |
| Assessment | Confirmed bug |
| Upstream state at snapshot | open |
| Created | 2026-08-28T14:16:16Z |
| Last upstream update | 2026-08-28T14:16:16Z |
| Closed | Not closed |
| Retrieved | 2026-10-30T17:28:03+00:00 |

**Reported-version context:** Version(s) reported in the original issue environment; not a first-affected boundary.

**Assessment:** An asymmetric Pauli evolution on reversed qargs is rebuilt in global DAG qubit order, changing the unitary. The report supplies source and expected circuits.

**Resolution:** Issue and proposed fix #16979 were open at collection time. No merged fix or released fixed version is verified.

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

Source: https://github.com/Qiskit/qiskit/issues/16860 by @WindOctober.

<details>
<summary>Full original issue text</summary>

### Environment

- **Qiskit version**: 2.5.2  
  Also reproduced on `2.6.0.dev0+b6f798f` (`b6f798f0bd88965821a54bff3785323a39c3a6c5`)
- **Python version**: 3.12
- **Operating system**: Linux

### What is happening?

`FindCommutingPauliEvolutions` can change the unitary of a `PauliEvolutionGate` when the gate is applied to circuit qubits in an order different from the DAG's global qubit order.

For example:

```python
source.append(
    PauliEvolutionGate(
        SparsePauliOp.from_list([("XY", 1.0)]),
        time=0.37,
    ),
    [1, 0],
)
```

applies the local two-qubit evolution to the ordered qargs:

```text
[q1, q0]
```

However, `FindCommutingPauliEvolutions` reconstructs the two-qubit evolution on:

```text
[q0, q1]
```

The problem begins in `run()`, which calls `_decompose_to_2q()` without passing the original node's qargs:

```python
sub_dag = self._decompose_to_2q(dag, node.op)
```

Relevant source:

https://github.com/Qiskit/qiskit/blob/b6f798f0bd88965821a54bff3785323a39c3a6c5/qiskit/transpiler/passes/routing/commuting_2q_gate_routing/pauli_2q_evolution_commutation.py#L35-L49

`_decompose_to_2q()` obtains an edge containing local operand indices within the Pauli operator:

```python
edge = self._pauli_to_edge(pauli)
```

but interprets these local indices as global indices into the complete DAG:

```python
qubits = [
    dag.qubits[edge[0]],
    dag.qubits[edge[1]],
]
```

Relevant source:

https://github.com/Qiskit/qiskit/blob/b6f798f0bd88965821a54bff3785323a39c3a6c5/qiskit/transpiler/passes/routing/commuting_2q_gate_routing/pauli_2q_evolution_commutation.py#L115-L139

This implements the mapping:

```text
local Pauli operand i -> dag.qubits[i]
```

rather than the required mapping:

```text
local Pauli operand i -> node.qargs[i]
```

The resulting `Commuting2qBlock` therefore stores its internal evolution node on the wrong qargs. `Commuting2qGateRouter` later obtains the routing edge directly from those stored qargs, so the incorrect mapping is propagated into the output circuit.

In effect, the pass pipeline performs:

```text
PauliEvolutionGate(XY) on [q1, q0]
    ->
PauliEvolutionGate(XY) on [q0, q1]
```

Because `XY` is asymmetric under exchanging its two operands, these two evolutions are not equivalent.

This is related to #16856, but it is a separate issue:

- #16856 concerns duplicate Pauli summands being overwritten because `_decompose_to_2q()` stores only one summand per edge.
- This issue concerns local Pauli indices being mapped to the wrong circuit qargs.

The reproducer below contains only one Pauli summand, so no duplicate-term overwrite is involved.


### How can we reproduce the issue?


The following script first inspects the qargs stored inside the generated `Commuting2qBlock`. It then runs the normal public routing pipeline and compares the resulting operators.

```python
import numpy as np
import qiskit

from qiskit import QuantumCircuit
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.quantum_info import Operator, SparsePauliOp
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes.routing.commuting_2q_gate_routing import (
    Commuting2qGateRouter,
    FindCommutingPauliEvolutions,
    SwapStrategy,
)


TIME = 0.37

operator = SparsePauliOp.from_list(
    [
        ("XY", 1.0),
    ]
)

source = QuantumCircuit(2)

# Apply the local two-qubit operator to reversed circuit qargs.
source.append(
    PauliEvolutionGate(operator, time=TIME),
    [1, 0],
)


# Run FindCommutingPauliEvolutions by itself.
after_find = PassManager(
    [
        FindCommutingPauliEvolutions(),
    ]
).run(source.copy())

block_operation = after_find.data[0].operation
block_node = next(iter(block_operation))

source_qargs = [
    source.find_bit(qubit).index
    for qubit in source.data[0].qubits
]

internal_block_qargs = [
    after_find.find_bit(qubit).index
    for qubit in block_node.qargs
]


# Run the normal public Find -> Router pipeline.
routed = PassManager(
    [
        FindCommutingPauliEvolutions(),
        Commuting2qGateRouter(
            SwapStrategy.from_line([0, 1])
        ),
    ]
).run(source.copy())

routed_evolutions = [
    instruction
    for instruction in routed.data
    if isinstance(
        instruction.operation,
        PauliEvolutionGate,
    )
]

assert len(routed_evolutions) == 1

routed_qargs = [
    routed.find_bit(qubit).index
    for qubit in routed_evolutions[0].qubits
]


# Construct the incorrect natural-order circuit produced by the
# affected implementation.
natural_order = QuantumCircuit(2)
natural_order.append(
    PauliEvolutionGate(operator, time=TIME),
    [0, 1],
)

source_operator = Operator(source)
routed_operator = Operator(routed)
natural_order_operator = Operator(natural_order)

print("Qiskit:", qiskit.__version__)
print("operation after Find:", block_operation.name)
print("source qargs:", source_qargs)
print("internal qargs stored in block:", internal_block_qargs)
print("routed qargs:", routed_qargs)
print(
    "routed circuit equivalent to source:",
    routed_operator.equiv(source_operator),
)
print(
    "routed circuit equivalent to natural-order gate:",
    routed_operator.equiv(natural_order_operator),
)
print(
    "maximum matrix difference from source:",
    np.max(
        np.abs(
            routed_operator.data
            - source_operator.data
        )
    ),
)

assert source_qargs == [1, 0]
assert internal_block_qargs == [0, 1]
assert routed_qargs == [0, 1]

assert not routed_operator.equiv(source_operator)
assert routed_operator.equiv(natural_order_operator)
```

On the affected implementation, the relevant output is:

```text
Qiskit: 2.5.2
operation after Find: commuting_2q_block
source qargs: [1, 0]
internal qargs stored in block: [0, 1]
routed qargs: [0, 1]
routed circuit equivalent to source: False
routed circuit equivalent to natural-order gate: True
maximum matrix difference from source: approximately 0.723231
```

The incorrect qarg mapping is already present immediately after running:

```python
FindCommutingPauliEvolutions()
```

The router subsequently receives a block whose internal evolution node is attached to `[q0, q1]`, so the semantic change originates in `FindCommutingPauliEvolutions`, not in the routing strategy.

The example uses a two-qubit line, so no SWAP insertion or nontrivial layout permutation is involved.

### What should happen?


`FindCommutingPauliEvolutions` should preserve both:

1. the operator represented by the input `PauliEvolutionGate`; and
2. the binding between the operator's local operands and the original node qargs.

For this example, the internal evolution node should remain attached to:

```text
[q1, q0]
```

and the following should hold after the public pass pipeline:

```python
Operator(routed).equiv(Operator(source))
```

The result should be:

```text
True
```

The pass must not silently reinterpret local Pauli operand indices as global DAG qubit indices.

### Any suggestions?


`_decompose_to_2q()` should receive the original node qargs, or an equivalent local-to-global qubit mapping.

For example, the call in `run()` could be changed from:

```python
sub_dag = self._decompose_to_2q(
    dag,
    node.op,
)
```

to:

```python
sub_dag = self._decompose_to_2q(
    dag,
    node.op,
    node.qargs,
)
```

The helper could then map each local Pauli edge through those qargs:

```python
def _decompose_to_2q(
    self,
    dag,
    op,
    qargs,
):
    ...

    qubits = [
        qargs[edge[0]],
        qargs[edge[1]],
    ]
```

This preserves the required mapping:

```text
local Pauli operand i -> original node.qargs[i]
```

A regression test should apply an asymmetric operator such as:

```python
SparsePauliOp.from_list(
    [
        ("XY", 1.0),
    ]
)
```

to reversed qargs:

```python
[1, 0]
```

and verify that the complete:

```text
FindCommutingPauliEvolutions
    ->
Commuting2qGateRouter
```

pipeline remains operator-equivalent to the source circuit.

Symmetric terms such as `XX` or `ZZ` should not be the only regression cases, because exchanging their operands can hide this qarg-mapping error.

This fix is independent of the duplicate-summand preservation issue reported in #16856; regression coverage should include both behaviors.

</details>

## Issue discussion, including closing and resolving comments

All fetched issue comments are preserved below in upstream chronological
order, including any closing or resolving comments. Comments are
third-party statements, not automatically verified benchmark claims.

No issue comments were present at retrieval time.

## Closure and reopening events

No closure or reopening events were present in the fetched timeline.

Closing an issue does not establish that a code fix was merged or released.

## Attribution and reuse

The original post and comments remain attributed to their upstream authors.
Their inclusion does not relicense them under this project's MIT license.
See [NOTICE](../../NOTICE). Machine-readable text and provenance are in
[source.json](source.json); curated version evidence is in
[the manifest](../manifest.json). Attachments are linked, not vendored.
