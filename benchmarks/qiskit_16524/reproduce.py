import qiskit
print("Running with fixed Qiskit version:", qiskit.__version__)

from qiskit.circuit.library import PhaseOracle
import qiskit.qasm2 as qasm2

# Tautological expression
expression = "x | ~x"
oracle = PhaseOracle(expression)

# Serialize the fixed circuit
qasm_str = qasm2.dumps(oracle)
with open("qiskit_16524_fixed.qasm", "w") as f:
    f.write(qasm_str)

print("Successfully generated qiskit_16524_fixed.qasm!")
