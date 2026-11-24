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

# Operator containing duplicate Pauli terms: 0.2 * ZZ + 0.4 * ZZ = 0.6 * ZZ
operator = SparsePauliOp(
    ["ZZ", "ZZ"],
    coeffs=[0.2, 0.4],
)

source = QuantumCircuit(2)
source.append(
    PauliEvolutionGate(operator, time=1.0),
    [0, 1],
)

# Run FindCommutingPauliEvolutions
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

# Run the full routing pipeline
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

# Expected combined circuit: exp(-i * 0.6 * ZZ)
combined = QuantumCircuit(2)
combined.append(
    PauliEvolutionGate(Pauli("ZZ"), time=0.6),
    [0, 1],
)

source_operator = Operator(source)
routed_operator = Operator(routed)
combined_operator = Operator(combined)

print(
    "input equivalent to combined 0.6 evolution:",
    source_operator.equiv(combined_operator),
)
print(
    "routed circuit equivalent to input:",
    routed_operator.equiv(source_operator),
)
print(
    "maximum matrix difference from input:",
    np.max(np.abs(routed_operator.data - source_operator.data)),
)
