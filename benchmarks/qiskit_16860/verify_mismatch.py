from mqt.qcec import verify
import sys

def verify_circuits():
    result = verify("qiskit_16860_fault.qasm", "qiskit_16860_fixed.qasm")
    print(f"Equivalence check result: {result.equivalence}")
    
    if result.equivalence.name.lower() == "not_equivalent":
        print("Verification successful: Circuits are correctly identified as not equivalent.")
        sys.exit(0)
    else:
        print("Unexpected equivalence result.")
        sys.exit(1)

if __name__ == "__main__":
    verify_circuits()
