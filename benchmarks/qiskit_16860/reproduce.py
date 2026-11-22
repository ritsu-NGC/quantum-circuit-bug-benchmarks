from qiskit import QuantumCircuit
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler.passes.routing.commuting_2q_gate_routing import FindCommutingPauliEvolutions
from qiskit.transpiler import PassManager
import qiskit.qasm2

def reproduce_issue():
    qc = QuantumCircuit(3)
    op = SparsePauliOp.from_list([("XZ", 1.0)])
    evolution_gate = PauliEvolutionGate(op, time=1.0)
    qc.append(evolution_gate, [2, 0])

    pm = PassManager([FindCommutingPauliEvolutions()])
    
    try:
        transformed_qc = pm.run(qc)
    except Exception as e:
        print(f"Caught expected error/mismatch: {e}")
        transformed_qc = qc  # Fallback to serializing the circuit that triggers it

    output_filename = "qiskit_16860_fault.qasm"
    with open(output_filename, "w") as f:
        qiskit.qasm2.dump(transformed_qc, f)
    
    print(f"Successfully serialized circuit to {output_filename}")

if __name__ == "__main__":
    reproduce_issue()
