from mqt.qcec import verify

# Compare the faulty and fixed QASM files
result = verify("qiskit_16524_fault.qasm", "qiskit_16524_fixed.qasm")

print("Equivalence result:", result.equivalence)

# Assert that they are not equivalent
assert result.equivalence.name == "not_equivalent", f"Expected not_equivalent, but got {result.equivalence}"
print("Verification successful: Circuits are correctly identified as not equivalent!")
