"""Reproduce Qiskit issue #16594 with CommutativeCancellation.

Run against the affected release with:
    python -m pip install "qiskit==2.5.0"
    python reproduce.py
The bug is fixed in Qiskit 2.5.1.
"""

from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import CommutativeCancellation

qc = QuantumCircuit(1)
qc.sxdg(0)
qc.sxdg(0)
qc.sx(0)

optimized = PassManager([CommutativeCancellation()]).run(qc)

print("Before:", qc.count_ops())
print("After: ", optimized.count_ops())
print("Equivalent:", Operator(qc).equiv(Operator(optimized)))