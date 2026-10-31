"""Check that the faulty and fixed Qiskit #16594 circuits are not equivalent.

Requires the QASM files produced by reproduce.py:
    qiskit_16594_fault.qasm  (Qiskit 2.5.0)
    qiskit_16594_fixed.qasm  (Qiskit 2.5.1)

Usage:
    python -m pip install mqt.qcec
    python verify_mismatch.py [FAULT_QASM] [FIXED_QASM]

Exits 0 if QCEC proves the circuits are not equivalent, 1 otherwise.
"""

import sys
from pathlib import Path

from mqt import qcec

here = Path(__file__).resolve().parent
fault = Path(sys.argv[1]) if len(sys.argv) > 1 else here / "qiskit_16594_fault.qasm"
fixed = Path(sys.argv[2]) if len(sys.argv) > 2 else here / "qiskit_16594_fixed.qasm"

result = qcec.verify(str(fault), str(fixed))
equivalence = result.equivalence
print(f"{fault.name} vs {fixed.name}: {equivalence.name}")

if equivalence.name == "not_equivalent":
    print("MISMATCH confirmed: the faulty and fixed circuits differ.")
    sys.exit(0)

print("Mismatch NOT confirmed.")
sys.exit(1)
