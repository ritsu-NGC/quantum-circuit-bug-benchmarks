# Qiskit issue #14356: HoareOptimizer incorrectly optimizes unitary gates

## Benchmark metadata

| Field | Value |
| --- | --- |
| Original issue | https://github.com/Qiskit/qiskit/issues/14356 |
| Source repository | `Qiskit/qiskit` |
| Original author | @ryanscott111 |
| Reported Qiskit version(s) at the issue | `2.0.0` |
| Verified Qiskit version(s) containing the fix | Not verified |
| Assessment | Confirmed bug |
| Upstream state at snapshot | open |
| Created | 2025-05-13T15:12:30Z |
| Last upstream update | 2025-05-18T08:44:21Z |
| Closed | Not closed |
| Retrieved | 2026-10-30T17:28:03+00:00 |

**Reported-version context:** Version(s) reported in the original issue environment; not a first-affected boundary.

**Assessment:** HoareOptimizer can treat distinct composite instructions as matching and remove them incorrectly. Preserve the circuit unless identity has been proved; the original report includes a reference circuit.

**Resolution:** Issue and proposed #16807 were open at collection time. No released fixed version is verified.

Reported versions are not an exhaustive affected range. A verified fixed
version is a published release containing the fix, not necessarily the
first fixed version across all maintenance branches. Historical fixed
release versions below 1.0 refer to `qiskit-terra`, not the old `qiskit`
metapackage. Reported versions retain their original distribution context.

## Fix and resolution evidence

No merged fix or fixed release was verified; see the full discussion below.

## Original issue post

The body below is reproduced verbatim from the original issue post as
returned by GitHub at retrieval time. It may include upstream edits,
mistakes, HTML, and externally hosted attachments. It is not a
reconstruction of the issue's initial, pre-edit revision.

Source: https://github.com/Qiskit/qiskit/issues/14356 by @ryanscott111.

<details>
<summary>Full original issue text</summary>

### Environment

- **Qiskit version**: 2.0.0
- **Python version**: 3.12.9
- **Operating system**: Ubuntu 22.04.1 LTS


### What is happening?

When using HoareOptimizer to optimize the following circuit, the output is incorrect.
```
from qiskit import QuantumCircuit

qc1 = QuantumCircuit(4, 1)
qc1.h(3)

qc2 = QuantumCircuit(4)
qc2.cx(0, 1)
qc2.cx(0, 2)
qc2.cx(0, 3)
qc2.h(3)
qc1.append(qc2, range(4), []) # circuit-158

qc3 = QuantumCircuit(4, 1)
qc1.append(qc3, range(4), range(1)) # circuit-161

qc1.measure_all()
```
The actual optimized circuit output:

![Image](https://github.com/user-attachments/assets/0ad4d3af-dac0-4d6c-9243-aabc107ff644)

However, the expected optimized output should be an empty circuit.

**Optimization Analysis**

In the `_traverse_dag` function, HoareOptimizer records the following gatecache:
```
q0: circuit-158, circuit-161, barrier, measure
q1: circuit-158, circuit-161, barrier, measure
q2: circuit-158, circuit-161, barrier, measure
q3: h, circuit-158, circuit-161, barrier, measure
```
Then HoareOptimizer attempts to remove identity blocks by calling `_remove_successive_identity` three times:

For q3: node1 = h, node2 = circuit-158
Targets differ, so skip.

For q0: node1 = circuit-158, node2 = circuit-161
HoareOptimizer checks node1 == node2 and returns True since both are Instruction instances, even though their internal semantics differ. As a result, it incorrectly removes both nodes.

For q0 again: node1 = barrier, node2 = measure
Targets differ, so skip.

### How can we reproduce the issue?

Create the above circuit and compare circuits before and after optimized:
```
from qiskit_aer import AerSimulator
backend = AerSimulator()
trans_qc = transpile(qc1, optimization_level=0, backend=backend)
print(trans_qc)  // This will display a correct circuit.

pm = PassManager()
pm.append(HoareOptimizer(size=2))
opt_qc = pm.run(qc1)
print(opt_qc) // This will display an incorrect circuit.
```

### What should happen?

The optimizer should either:
+ Successfully simplify the circuit to an empty circuit, or
+ Retain the original circuit if it cannot prove semantic identity.

### Any suggestions?

A possible fix is to decompose composite instructions (like `qc2` and `qc3`) into their base gates before comparison, to ensure proper semantic checking of identity.

</details>

## Issue discussion, including closing and resolving comments

All fetched issue comments are preserved below in upstream chronological
order, including any closing or resolving comments. Comments are
third-party statements, not automatically verified benchmark claims.

### Comment 2888861756 by @alexanderivrii

Posted: 2025-05-18T08:44:20Z. Updated: 2025-05-18T08:44:20Z.

Source: https://github.com/Qiskit/qiskit/issues/14356#issuecomment-2888861756

<details>
<summary>Full comment by @alexanderivrii</summary>

Thanks for detecting and investigating the problem @ryanscott111 . As `HoareOptimizer` is not a part of Qiskit's default transpilation pipeline even with optimization level 3, it's significantly less tested than other transpiler passes and thus could have other bugs. In fact, as far as I know, #13165 has not been addressed either, and if I recall correctly also stemmed from some problems in the caching mechanism. Would one of these two issues be something you would be interested in investigating further and potentially submitting a fix?

I have not thought too deeply about this, but I don't think we should enforce running the decomposition pass prior to running `HoareOptimizer`, the optimizer should not make invalid reductions even in the presence of custom gates, subcircuits, etc. Though I do agree that to get the most benefit of the pass, we should probably run the `HighLevelSynthesis` pass (aka the decomposition pass) before `HoareOptimizer`.



</details>


## Closure and reopening events

No closure or reopening events were present in the fetched timeline.

Closing an issue does not establish that a code fix was merged or released.

## Attribution and reuse

The original post and comments remain attributed to their upstream authors.
Their inclusion does not relicense them under this project's MIT license.
See [NOTICE](../../NOTICE). Machine-readable text and provenance are in
[source.json](source.json); curated version evidence is in
[the manifest](../manifest.json). Attachments are linked, not vendored.
