# Qiskit issue #5666: classical_function creates wrong circuits for some cases

## Benchmark metadata

| Field | Value |
| --- | --- |
| Original issue | https://github.com/Qiskit/qiskit/issues/5666 |
| Source repository | `Qiskit/qiskit` |
| Original author | @a-matsuo |
| Reported Qiskit version(s) at the issue | Not specified |
| Verified Qiskit version(s) containing the fix | `0.17.0` |
| Assessment | Mixed report: confirmed and disputed/expected aspects |
| Upstream state at snapshot | closed (completed) |
| Created | 2021-01-21T13:17:51Z |
| Last upstream update | 2021-03-31T18:11:32Z |
| Closed | 2021-03-31T18:11:32Z |
| Retrieved | 2026-10-30T17:28:03+00:00 |

**Reported-version context:** The original environment says 'master', with no numerical Qiskit Terra version or commit.

**Assessment:** The resolving discussion says case 1 (register ordering) is not a bug. Case 2 reports incorrect Boolean OR synthesis. Both original examples are retained, without presenting the first as a confirmed bug.

**Resolution:** Merged #5830 is linked as resolving the issue and verified in qiskit-terra 0.17.0.

Reported versions are not an exhaustive affected range. A verified fixed
version is a published release containing the fix, not necessarily the
first fixed version across all maintenance branches. Historical fixed
release versions below 1.0 refer to `qiskit-terra`, not the old `qiskit`
metapackage. Reported versions retain their original distribution context.

## Fix and resolution evidence

- https://github.com/Qiskit/qiskit/issues/5666#issuecomment-784192665

### Verified fixed release: 0.17.0

- Distribution: `qiskit-terra`.
- Original fix: https://github.com/Qiskit/qiskit/pull/5830.
- Included fix/backport PR: https://github.com/Qiskit/qiskit/pull/5830.
- Merged: 2021-03-31T18:11:32Z.
- Fix commit: `674a6e28984eefc74018acf881fd3aff9db19fc1`.
- Published release: https://github.com/Qiskit/qiskit/releases/tag/0.17.0 (2021-04-01T15:39:11Z).
- Ancestry comparison: https://github.com/Qiskit/qiskit/compare/674a6e28984eefc74018acf881fd3aff9db19fc1...0.17.0.
- Verification: Fix merge commit is an ancestor of the published release tag.
- Verified at: 2026-10-30T17:28:03+00:00.

## Original issue post

The body below is reproduced verbatim from the original issue post as
returned by GitHub at retrieval time. It may include upstream edits,
mistakes, HTML, and externally hosted attachments. It is not a
reconstruction of the issue's initial, pre-edit revision.

Source: https://github.com/Qiskit/qiskit/issues/5666 by @a-matsuo.

<details>
<summary>Full original issue text</summary>

### Information

- **Qiskit Terra version**: master
- **Python version**: 3.8
- **Operating system**: macOS Catalina

### What is the current behavior?
`classical_function` creates wrong circuits for some cases. I confirmed at least two cases. 

### Steps to reproduce the problem
Case 1) 
```
def expr1(x1: Int1, x2: Int1, x3: Int1) -> Int1:
    return x1

cf = classical_function(expr1)
print(cf.synth())

q_0: ──■──
       │  
q_1: ──┼──
       │  
q_2: ──┼──
     ┌─┴─┐
q_3: ┤ X ├
     └───┘
```

Case 2)
```
def expr2(x1: Int1, x2: Int1, x3: Int1) -> Int1:
    return x1 or x2 or x3

cf = classical_function(expr2)
print(cf.synth())

q_0: ──o────────────
       │            
q_1: ──o────o───────
       │    │       
q_2: ──■────■────■──
     ┌─┴─┐┌─┴─┐┌─┴─┐
q_3: ┤ X ├┤ X ├┤ X ├
     └───┘└───┘└───┘
```
### What is the expected behavior?
Case 1)
The control bit of the CNOT gate should be the most bottom bit. 

As written in the [documentation](https://qiskit.org/documentation/apidoc/classicalfunction.html), following Qiskit’s little-endian bit ordering convention, the left-most bit (x1) is the most significant bit and the right-most bit (x3) is the least significant bit. 
The following code is an example for the correct bit ordering.
```
def expr3(x1: Int1, x2: Int1, x3: Int1) -> Int1:
    return not x1 and x2 and x3

cf = classical_function(expr3)
print(cf.synth())

q_0: ──■──
       │  
q_1: ──■──
       │  
q_2: ──o──
     ┌─┴─┐
q_3: ┤ X ├
     └───┘
```

Case 2)
The circuit does not represent `x1 or x2 or x3`. For example, when (x1, x2, x3) = (001), $q_3$ of the circuit does not become 1.

### Suggested solutions



</details>

## Issue discussion, including closing and resolving comments

All fetched issue comments are preserved below in upstream chronological
order, including any closing or resolving comments. Comments are
third-party statements, not automatically verified benchmark claims.

### Comment 784192665 by @boschmitt

Posted: 2021-02-23T13:12:01Z. Updated: 2021-02-23T13:12:01Z.

Source: https://github.com/Qiskit/qiskit/issues/5666#issuecomment-784192665

<details>
<summary>Full comment by @boschmitt</summary>

Case 1 is not a bug.

Indeed, Qiskit's follows little-endian bit ordering convention but this happens __within__ a register, i.e., there will be a difference of between declaring two 1 qubit registers and a register of 2 qubits.  Hence, if you had declared a the function as
```python
def expr1(x: Int3) -> Int1:
    ...
```
then you would get `x` as a register of three bits following the little-endian bit ordering.

Case 2 will be fixed by #5830 


</details>


## Closure and reopening events

- 2021-03-31T18:11:32Z: closed by @mergify[bot].

Closing an issue does not establish that a code fix was merged or released.

## Attribution and reuse

The original post and comments remain attributed to their upstream authors.
Their inclusion does not relicense them under this project's MIT license.
See [NOTICE](../../NOTICE). Machine-readable text and provenance are in
[source.json](source.json); curated version evidence is in
[the manifest](../manifest.json). Attachments are linked, not vendored.
