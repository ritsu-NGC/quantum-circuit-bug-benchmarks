"""Reproduce Qiskit issue #16594 with CommutativeCancellation.

Run against the affected release with:
    python -m pip install "qiskit==2.5.0"
    python reproduce.py
The bug is fixed in Qiskit 2.5.1.

Optionally dump the optimized circuit as OpenQASM 2.0:
    python reproduce.py --qasm qiskit_16594_fault.qasm   # with qiskit==2.5.0
    python reproduce.py --qasm qiskit_16594_fixed.qasm   # with qiskit==2.5.1
"""

import argparse

import qiskit
from qiskit import QuantumCircuit, qasm2
from qiskit.quantum_info import Operator
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import CommutativeCancellation

parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
parser.add_argument(
    "--qasm",
    metavar="PATH",
    help="write the optimized circuit to PATH as OpenQASM 2.0",
)
args = parser.parse_args()

qc = QuantumCircuit(1)
qc.sxdg(0)
qc.sxdg(0)
qc.sx(0)

optimized = PassManager([CommutativeCancellation()]).run(qc)

print("Qiskit:", qiskit.__version__)
print("Before:", qc.count_ops())
print("After: ", optimized.count_ops())
print("Equivalent:", Operator(qc).equiv(Operator(optimized)))

if args.qasm:
    with open(args.qasm, "w", encoding="utf-8") as f:
        qasm2.dump(optimized, f)
    print("Wrote optimized circuit to", args.qasm)
