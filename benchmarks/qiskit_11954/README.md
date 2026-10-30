# Qiskit issue #11954: qasm3 returns wrong results with pauli evolution gate

## Benchmark metadata

| Field | Value |
| --- | --- |
| Original issue | https://github.com/Qiskit/qiskit/issues/11954 |
| Source repository | `Qiskit/qiskit` |
| Original author | @LenaPer |
| Reported Qiskit version(s) at the issue | Not specified |
| Verified Qiskit version(s) containing the fix | `1.2.0` |
| Assessment | Confirmed bug |
| Upstream state at snapshot | closed (completed) |
| Created | 2024-03-06T08:49:00Z |
| Last upstream update | 2024-07-22T14:23:10Z |
| Closed | 2024-07-22T14:23:10Z |
| Retrieved | 2026-10-30T17:28:03+00:00 |

**Reported-version context:** The original issue has no Environment section or numerical affected Qiskit version. The report date is not a version.

**Assessment:** QASM3 export conflates distinct XX, YY, and ZZ PauliEvolutionGate definitions, changing the exported circuit.

**Resolution:** Merged symbol-table rewrite #12776 is verified in 1.2.0.

Reported versions are not an exhaustive affected range. A verified fixed
version is a published release containing the fix, not necessarily the
first fixed version across all maintenance branches. Historical fixed
release versions below 1.0 refer to `qiskit-terra`, not the old `qiskit`
metapackage. Reported versions retain their original distribution context.

## Fix and resolution evidence


### Verified fixed release: 1.2.0

- Distribution: `qiskit`.
- Original fix: https://github.com/Qiskit/qiskit/pull/12776.
- Included fix/backport PR: https://github.com/Qiskit/qiskit/pull/12776.
- Merged: 2024-07-22T14:23:07Z.
- Fix commit: `59fc49593a6695fa2dffd8c8f291207706c1686f`.
- Published release: https://github.com/Qiskit/qiskit/releases/tag/1.2.0 (2024-08-15T20:41:15Z).
- Ancestry comparison: https://github.com/Qiskit/qiskit/compare/59fc49593a6695fa2dffd8c8f291207706c1686f...1.2.0.
- Verification: Fix merge commit is an ancestor of the published release tag.
- Verified at: 2026-10-30T17:28:03+00:00.

## Original issue post

The body below is reproduced verbatim from the original issue post as
returned by GitHub at retrieval time. It may include upstream edits,
mistakes, HTML, and externally hosted attachments. It is not a
reconstruction of the issue's initial, pre-edit revision.

Source: https://github.com/Qiskit/qiskit/issues/11954 by @LenaPer.

<details>
<summary>Full original issue text</summary>

When trying to turn this circuit into a qasm3 : 

```
from qiskit.circuit import QuantumCircuit, ParameterVector
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.quantum_info import SparsePauliOp
from qiskit.qasm3 import dumps, loads, dump, load

t = ParameterVector("t", 3)
X, Y, Z = SparsePauliOp("X"), SparsePauliOp("Y"), SparsePauliOp("Z")
op1, op2, op3 = (X^X), (Y^Y), (Z^Z)
evo1 = PauliEvolutionGate(op1, time=t[0])
evo2 = PauliEvolutionGate(op2, time=t[1])
evo3 = PauliEvolutionGate(op3, time=t[2])
 
dec0 = QuantumCircuit(2)
dec0.append(evo1, range(2))
dec0.append(evo2, range(2))
dec0.append(evo3, range(2))
dec0.count_ops() #returns OrderedDict([('PauliEvolution', 3)])
```

after dumping into a qasm3, we would expect the qasm to have 3 different gates for the XX, YY, ZZ but it only looks into the first Pauli evolution gate and repeats it 3 times : 

```
q0 = dumps(dec0)
print(q0)
#returns 
OPENQASM 3.0;
include "stdgates.inc";
input float[64] _t_0_;
input float[64] _t_1_;
input float[64] _t_2_;
gate rxx_4948547280(_t_0_) _gate_q_0, _gate_q_1 {
  h _gate_q_0;
  h _gate_q_1;
  cx _gate_q_0, _gate_q_1;
  rz(2.0*_t_0_) _gate_q_1;
  cx _gate_q_0, _gate_q_1;
  h _gate_q_1;
  h _gate_q_0;
}
gate PauliEvolution(_t_0_) _gate_q_0, _gate_q_1 {
  rxx_4948547280(2.0*_t_0_) _gate_q_0, _gate_q_1;
}
qubit[2] q;
PauliEvolution(_t_0_) q[0], q[1];
PauliEvolution(_t_1_) q[0], q[1];
PauliEvolution(_t_2_) q[0], q[1];
```


</details>

## Issue discussion, including closing and resolving comments

All fetched issue comments are preserved below in upstream chronological
order, including any closing or resolving comments. Comments are
third-party statements, not automatically verified benchmark claims.

### Comment 2018501508 by @LenaPer

Posted: 2024-03-25T17:12:47Z. Updated: 2024-03-25T17:12:47Z.

Source: https://github.com/Qiskit/qiskit/issues/11954#issuecomment-2018501508

<details>
<summary>Full comment by @LenaPer</summary>

It looks like the same problem as in https://github.com/Qiskit/qiskit/issues/7335 but the workaround doesn't work for this specific example. It might be because the op doesn't appear in the name or in the parameters and fall through the cracks of the fix.
```
print(evo1.params, evo1.name)
# returns [ParameterVectorElement(t[0])] PauliEvolution
```

</details>

### Comment 2034861821 by @jakelishman

Posted: 2024-04-03T15:00:34Z. Updated: 2024-04-03T15:00:34Z.

Source: https://github.com/Qiskit/qiskit/issues/11954#issuecomment-2034861821

<details>
<summary>Full comment by @jakelishman</summary>

Thanks for the report.  It looks like the OpenQASM 3 exporter still maintains a lot of the same problems that the OpenQASM 2 exporter used to have until we fixed a whole load of them in #9953 - this kind of duplicate definition / bad definition reuse / whatever used to be rife in the old one as well.  I'm not sure of a timespan for when we'll get this entirely fixed, but I think such a fix will tie into the implementation of #10737, since to handle exporting against multiple possible library files, we'll need to rethink how we do the definition decomposition quite heavily.

</details>

### Comment 2230684051 by @jakelishman

Posted: 2024-07-16T11:42:59Z. Updated: 2024-07-16T11:42:59Z.

Source: https://github.com/Qiskit/qiskit/issues/11954#issuecomment-2230684051

<details>
<summary>Full comment by @jakelishman</summary>

This should be fixed by #12776 for `PauliEvolutionGate`.

</details>


## Closure and reopening events

- 2024-07-22T14:23:10Z: closed by @ElePT.

Closing an issue does not establish that a code fix was merged or released.

## Attribution and reuse

The original post and comments remain attributed to their upstream authors.
Their inclusion does not relicense them under this project's MIT license.
See [NOTICE](../../NOTICE). Machine-readable text and provenance are in
[source.json](source.json); curated version evidence is in
[the manifest](../manifest.json). Attachments are linked, not vendored.
