from mqt.qcec import verify

# Compare the faulty and fixed QASM files
result = verify("qiskit_16856_fault.qasm", "qiskit_16856_fixed.qasm")

print("Equivalence result:", result.equivalence)

# Assert that they are not equivalent (as expected for the bug comparison)
assert result.equivalence.name == "not_equivalent", f"Expected not_equivalent, but got {result.equivalence}"
print("Verification successful: Circuits are correctly identified as not equivalent!")
