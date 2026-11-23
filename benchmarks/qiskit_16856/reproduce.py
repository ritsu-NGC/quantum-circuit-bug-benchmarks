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

operator = SparsePauliOp(
    ["ZZ", "ZZ"],
    coeffs=[0.2, 0.4],
)

source = QuantumCircuit(2)
source.append(
    PauliEvolutionGate(operator, time=1.0),
    [0, 1],
)

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

combined = QuantumCircuit(2)
combined.append(
    PauliEvolutionGate(Pauli("ZZ"), time=0.6),
    [0, 1],
)

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
