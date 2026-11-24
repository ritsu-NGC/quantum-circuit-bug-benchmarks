import qiskit
print("Running with Qiskit version:", qiskit.__version__)

from qiskit.circuit.library import PhaseOracle
import qiskit.qasm2 as qasm2

# Tautological expression (always True)
expression = "x | ~x"

try:
    # PhaseOracle directly builds the circuit
    oracle = PhaseOracle(expression)
    print("PhaseOracle created successfully:", oracle)
    
    # Serialize the faulty circuit
    qasm_str = qasm2.dumps(oracle)
    with open("qiskit_16524_fault.qasm", "w") as f:
        f.write(qasm_str)
    print("Successfully generated qiskit_16524_fault.qasm")
except Exception as e:
    print("Caught expected synthesis/oracle failure:", type(e).__name__, e)
