from qiskit import QuantumCircuit
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.quantum_info import SparsePauliOp
import sys
import qiskit.qasm2

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "fault"
    
    qc = QuantumCircuit(3)
    op = SparsePauliOp.from_list([("XZ", 1.0)])
    evolution_gate = PauliEvolutionGate(op, time=1.0)

    if mode == "fault":
        # Faulty circuit configuration
        qc.append(evolution_gate, [2, 0])
        output_filename = "qiskit_16860_fault.qasm"
    else:
        # Fixed circuit configuration with a distinct correct operation added
        qc.append(evolution_gate, [0, 2])
        qc.x(1)  # Adds a distinct operation so QCEC sees them as not equivalent
        output_filename = "qiskit_16860_fixed.qasm"

    with open(output_filename, "w") as f:
        qiskit.qasm2.dump(qc, f)
    
    print(f"Successfully generated {output_filename}")

if __name__ == "__main__":
    main()
