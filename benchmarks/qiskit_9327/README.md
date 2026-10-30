# Qiskit issue #9327: Approximate quantum compiler (AQC) returns a wrong circuit when the unitary has a determinant −1

## Benchmark metadata

| Field | Value |
| --- | --- |
| Original issue | https://github.com/Qiskit/qiskit/issues/9327 |
| Source repository | `Qiskit/qiskit` |
| Original author | @EgrettaThula |
| Reported Qiskit version(s) at the issue | `0.22.3` |
| Verified Qiskit version(s) containing the fix | `0.23.0` |
| Assessment | Confirmed bug |
| Upstream state at snapshot | closed (completed) |
| Created | 2022-12-28T09:05:53Z |
| Last upstream update | 2023-01-13T21:38:32Z |
| Closed | 2023-01-13T21:38:32Z |
| Retrieved | 2026-10-30T17:28:03+00:00 |

**Reported-version context:** Version(s) reported in the original issue environment; not a first-affected boundary.

**Assessment:** AQC computes an invalid real fractional power of a negative determinant and emits a circuit that does not approximate the target unitary.

**Resolution:** Merged fix #9331 is verified in qiskit-terra 0.23.0. An earlier maintenance-branch fix is not asserted.

Reported versions are not an exhaustive affected range. A verified fixed
version is a published release containing the fix, not necessarily the
first fixed version across all maintenance branches. Historical fixed
release versions below 1.0 refer to `qiskit-terra`, not the old `qiskit`
metapackage. Reported versions retain their original distribution context.

## Fix and resolution evidence


### Verified fixed release: 0.23.0

- Distribution: `qiskit-terra`.
- Original fix: https://github.com/Qiskit/qiskit/pull/9331.
- Included fix/backport PR: https://github.com/Qiskit/qiskit/pull/9331.
- Merged: 2023-01-13T21:38:31Z.
- Fix commit: `b4268b9afb91234b5389a11448e23299377ccaa4`.
- Published release: https://github.com/Qiskit/qiskit/releases/tag/0.23.0 (2023-01-26T21:24:47Z).
- Ancestry comparison: https://github.com/Qiskit/qiskit/compare/b4268b9afb91234b5389a11448e23299377ccaa4...0.23.0.
- Verification: Fix merge commit is an ancestor of the published release tag.
- Verified at: 2026-10-30T17:28:03+00:00.

## Original issue post

The body below is reproduced verbatim from the original issue post as
returned by GitHub at retrieval time. It may include upstream edits,
mistakes, HTML, and externally hosted attachments. It is not a
reconstruction of the issue's initial, pre-edit revision.

Source: https://github.com/Qiskit/qiskit/issues/9327 by @EgrettaThula.

<details>
<summary>Full original issue text</summary>

### Environment

- **Qiskit Terra version**: 0.22.3
- **Python version**: 3.9.5
- **Operating system**: Windows 10


### What is happening?

When the approximate quantum compiler (AQC) is used to synthesis a unitary which has a determinant −1 (e.g., an "odd parity" permutation matrix), a warning message is displayed:
```
[...]synthesis\aqc\aqc.py:83: RuntimeWarning: invalid value encountered in power
  su_matrix = target_matrix / np.power(target_det, (1 / matrix_dim))
```
then it continues its work and generates a circuit. The unitary of the generated circuit, however, is not an approximation to the original one.


### How can we reproduce the issue?

```python
unitary = np.ndarray(shape=(8, 8), buffer=np.array([
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 1],
], dtype=int), dtype=int)

num_qubits = 3

cnots = make_cnot_network(num_qubits = num_qubits, network_layout = 'spin', connectivity_type = 'full', depth = 0)

optimizer = L_BFGS_B()
aqc = AQC(optimizer)
approximate_circuit = CNOTUnitCircuit(num_qubits=num_qubits, cnots=cnots)
approximating_objective = DefaultCNOTUnitObjective(num_qubits=num_qubits, cnots=cnots)

aqc.compile_unitary(
    target_matrix=unitary,
    approximate_circuit=approximate_circuit,
    approximating_objective=approximating_objective,
)

approx_matrix = Operator(approximate_circuit).data
error = 0.5 * (np.linalg.norm(approx_matrix - unitary, "fro") ** 2)

print(error)
array_to_latex(approx_matrix)
```

### What should happen?

The code must take this case into account

### Any suggestions?

The root cause of this wrong behavior is this line of code:
```
su_matrix = target_matrix / np.power(target_det, (1 / matrix_dim))
```
As per numpy.power documentation:

> Negative values raised to a non-integral value will return `nan`. To get complex results, cast the input to `complex`.

The issue can be simply fixed by replacing this line with:
```
su_matrix = target_matrix / np.power(target_det, (1 / matrix_dim), dtype=complex)
```


</details>

## Issue discussion, including closing and resolving comments

All fetched issue comments are preserved below in upstream chronological
order, including any closing or resolving comments. Comments are
third-party statements, not automatically verified benchmark claims.

### Comment 1366840705 by @ajavadia

Posted: 2022-12-28T18:26:49Z. Updated: 2022-12-28T18:26:49Z.

Source: https://github.com/Qiskit/qiskit/issues/9327#issuecomment-1366840705

<details>
<summary>Full comment by @ajavadia</summary>

Thanks @EgrettaThula for finding this bug, would you like to make a PR to implement your suggestion? You would just have to make the change you suggest, and add a test case.

</details>

### Comment 1367919879 by @EgrettaThula

Posted: 2022-12-30T13:26:46Z. Updated: 2022-12-30T13:26:46Z.

Source: https://github.com/Qiskit/qiskit/issues/9327#issuecomment-1367919879

<details>
<summary>Full comment by @EgrettaThula</summary>

I'll work on it.

</details>


## Closure and reopening events

- 2023-01-13T21:38:33Z: closed by @mergify[bot].

Closing an issue does not establish that a code fix was merged or released.

## Attribution and reuse

The original post and comments remain attributed to their upstream authors.
Their inclusion does not relicense them under this project's MIT license.
See [NOTICE](../../NOTICE). Machine-readable text and provenance are in
[source.json](source.json); curated version evidence is in
[the manifest](../manifest.json). Attachments are linked, not vendored.
