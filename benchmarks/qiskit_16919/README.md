# Qiskit issue #16919: Qiskit generates invalid qasm3 for circuits with MCX/MCZ gates

## Benchmark metadata

| Field | Value |
| --- | --- |
| Original issue | https://github.com/Qiskit/qiskit/issues/16919 |
| Source repository | `Qiskit/qiskit` |
| Original author | @cnakhl |
| Reported Qiskit version(s) at the issue | `2.5.2` |
| Verified Qiskit version(s) containing the fix | `2.6.0` |
| Assessment | Confirmed bug |
| Upstream state at snapshot | closed (completed) |
| Created | 2026-09-03T06:40:00Z |
| Last upstream update | 2026-09-04T01:09:37Z |
| Closed | 2026-09-04T01:09:37Z |
| Retrieved | 2026-10-30T17:28:03+00:00 |

**Reported-version context:** Version(s) reported in the original issue environment; not a first-affected boundary.

**Assessment:** Circuit-representation bug: MCX/MCZ synthesis with at least five controls drops packed MCPhase parameter metadata, producing unparseable QASM3. This is not evidence that an executable circuit silently changes its unitary.

**Resolution:** The reporter confirmed that #16781 fixes the reproducer. Release 2.6.0 contains the merged fix.

Reported versions are not an exhaustive affected range. A verified fixed
version is a published release containing the fix, not necessarily the
first fixed version across all maintenance branches. Historical fixed
release versions below 1.0 refer to `qiskit-terra`, not the old `qiskit`
metapackage. Reported versions retain their original distribution context.

## Fix and resolution evidence

- https://github.com/Qiskit/qiskit/issues/16919#issuecomment-5534225404

### Verified fixed release: 2.6.0

- Distribution: `qiskit`.
- Original fix: https://github.com/Qiskit/qiskit/pull/16781.
- Included fix/backport PR: https://github.com/Qiskit/qiskit/pull/16781.
- Merged: 2026-08-17T05:20:31Z.
- Fix commit: `23f9e8f7aee57465cd757a16312f735531c1fce4`.
- Published release: https://github.com/Qiskit/qiskit/releases/tag/2.6.0 (2026-10-16T12:04:54Z).
- Ancestry comparison: https://github.com/Qiskit/qiskit/compare/23f9e8f7aee57465cd757a16312f735531c1fce4...2.6.0.
- Verification: Fix merge commit is an ancestor of the published release tag.
- Verified at: 2026-10-30T17:28:03+00:00.

## Original issue post

The body below is reproduced verbatim from the original issue post as
returned by GitHub at retrieval time. It may include upstream edits,
mistakes, HTML, and externally hosted attachments. It is not a
reconstruction of the issue's initial, pre-edit revision.

Source: https://github.com/Qiskit/qiskit/issues/16919 by @cnakhl.

<details>
<summary>Full original issue text</summary>

### Environment

- **Qiskit version**:  2.5.2
- **Python version**:  3.14.7
- **Operating system**: macOS 26.6.2


### What is happening?

Given a quantum circuit which has a multiply-controlled X (or multiply-controlled Z) gate with 5 or more controls, the qasm3 code generated is invalid. In particular the mcphase gate it defines includes an unused phase parameter, similar to https://github.com/Qiskit/qiskit/issues/13350. In this case however, this unused parameter is not included when calling the mcphase gate in the mcx/mcz definitions in QASM. This predictably results in an error if you attempt to then load the qasm file with qiskit (or anything else that parses qasm3 files). 

### How can we reproduce the issue?

Here's a minimal example that will result in an exception 

```python
from qiskit.circuit.library import MCMTGate, ZGate
from qiskit import qasm3, QuantumCircuit
import qiskit

num_qubits = 6
qc = QuantumCircuit(num_qubits)
qc.mcx([0,1,2,3,4], 5)

qasm_string = qasm3.dumps(qc)

qasm3.loads(qasm_string)
```

The qasm in ``qasm_string`` is given by

```qasm
OPENQASM 3.0;
include "stdgates.inc";
gate mcphase(_gate_p_0) _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4, _gate_q_5 {
  h _gate_q_5;
  p(pi/8) _gate_q_0;
  p(pi/8) _gate_q_1;
  p(pi/8) _gate_q_2;
  p(pi/8) _gate_q_5;
  cx _gate_q_0, _gate_q_1;
  p(-pi/8) _gate_q_1;
  cx _gate_q_0, _gate_q_1;
  cx _gate_q_1, _gate_q_2;
  p(-pi/8) _gate_q_2;
  cx _gate_q_0, _gate_q_2;
  p(pi/8) _gate_q_2;
  cx _gate_q_1, _gate_q_2;
  p(-pi/8) _gate_q_2;
  cx _gate_q_0, _gate_q_2;
  cx _gate_q_2, _gate_q_5;
  p(-pi/8) _gate_q_5;
  cx _gate_q_1, _gate_q_5;
  p(pi/8) _gate_q_5;
  cx _gate_q_2, _gate_q_5;
  p(-pi/8) _gate_q_5;
  cx _gate_q_0, _gate_q_5;
  p(pi/8) _gate_q_5;
  cx _gate_q_2, _gate_q_5;
  p(-pi/8) _gate_q_5;
  cx _gate_q_1, _gate_q_5;
  p(pi/8) _gate_q_5;
  cx _gate_q_2, _gate_q_5;
  p(-pi/8) _gate_q_5;
  cx _gate_q_0, _gate_q_5;
  h _gate_q_5;
  rz(-pi/4) _gate_q_5;
  h _gate_q_5;
  cx _gate_q_4, _gate_q_5;
  tdg _gate_q_5;
  cx _gate_q_3, _gate_q_5;
  t _gate_q_5;
  cx _gate_q_4, _gate_q_5;
  tdg _gate_q_5;
  cx _gate_q_3, _gate_q_5;
  t _gate_q_4;
  t _gate_q_5;
  h _gate_q_5;
  cx _gate_q_3, _gate_q_4;
  t _gate_q_3;
  tdg _gate_q_4;
  cx _gate_q_3, _gate_q_4;
  rz(pi/4) _gate_q_5;
  h _gate_q_5;
  p(pi/8) _gate_q_0;
  p(pi/8) _gate_q_1;
  p(pi/8) _gate_q_2;
  p(pi/8) _gate_q_5;
  cx _gate_q_0, _gate_q_1;
  p(-pi/8) _gate_q_1;
  cx _gate_q_0, _gate_q_1;
  cx _gate_q_1, _gate_q_2;
  p(-pi/8) _gate_q_2;
  cx _gate_q_0, _gate_q_2;
  p(pi/8) _gate_q_2;
  cx _gate_q_1, _gate_q_2;
  p(-pi/8) _gate_q_2;
  cx _gate_q_0, _gate_q_2;
  cx _gate_q_2, _gate_q_5;
  p(-pi/8) _gate_q_5;
  cx _gate_q_1, _gate_q_5;
  p(pi/8) _gate_q_5;
  cx _gate_q_2, _gate_q_5;
  p(-pi/8) _gate_q_5;
  cx _gate_q_0, _gate_q_5;
  p(pi/8) _gate_q_5;
  cx _gate_q_2, _gate_q_5;
  p(-pi/8) _gate_q_5;
  cx _gate_q_1, _gate_q_5;
  p(pi/8) _gate_q_5;
  cx _gate_q_2, _gate_q_5;
  p(-pi/8) _gate_q_5;
  cx _gate_q_0, _gate_q_5;
  h _gate_q_5;
  rz(-pi/4) _gate_q_5;
  h _gate_q_5;
  cx _gate_q_4, _gate_q_5;
  tdg _gate_q_5;
  cx _gate_q_3, _gate_q_5;
  t _gate_q_5;
  cx _gate_q_4, _gate_q_5;
  tdg _gate_q_5;
  cx _gate_q_3, _gate_q_5;
  t _gate_q_4;
  t _gate_q_5;
  h _gate_q_5;
  cx _gate_q_3, _gate_q_4;
  t _gate_q_3;
  tdg _gate_q_4;
  cx _gate_q_3, _gate_q_4;
  rz(pi/4) _gate_q_5;
  h _gate_q_4;
  cx _gate_q_1, _gate_q_4;
  tdg _gate_q_4;
  cx _gate_q_0, _gate_q_4;
  t _gate_q_4;
  cx _gate_q_1, _gate_q_4;
  tdg _gate_q_4;
  cx _gate_q_0, _gate_q_4;
  t _gate_q_1;
  t _gate_q_4;
  h _gate_q_4;
  cx _gate_q_0, _gate_q_1;
  t _gate_q_0;
  tdg _gate_q_1;
  cx _gate_q_0, _gate_q_1;
  rz(-pi/8) _gate_q_4;
  h _gate_q_4;
  cx _gate_q_3, _gate_q_4;
  tdg _gate_q_4;
  cx _gate_q_2, _gate_q_4;
  t _gate_q_4;
  cx _gate_q_3, _gate_q_4;
  tdg _gate_q_4;
  cx _gate_q_2, _gate_q_4;
  t _gate_q_3;
  t _gate_q_4;
  h _gate_q_4;
  cx _gate_q_2, _gate_q_3;
  t _gate_q_2;
  tdg _gate_q_3;
  cx _gate_q_2, _gate_q_3;
  rz(pi/8) _gate_q_4;
  h _gate_q_4;
  cx _gate_q_1, _gate_q_4;
  tdg _gate_q_4;
  cx _gate_q_0, _gate_q_4;
  t _gate_q_4;
  cx _gate_q_1, _gate_q_4;
  tdg _gate_q_4;
  cx _gate_q_0, _gate_q_4;
  t _gate_q_1;
  t _gate_q_4;
  h _gate_q_4;
  cx _gate_q_0, _gate_q_1;
  t _gate_q_0;
  tdg _gate_q_1;
  cx _gate_q_0, _gate_q_1;
  rz(-pi/8) _gate_q_4;
  h _gate_q_4;
  cx _gate_q_3, _gate_q_4;
  tdg _gate_q_4;
  cx _gate_q_2, _gate_q_4;
  t _gate_q_4;
  cx _gate_q_3, _gate_q_4;
  tdg _gate_q_4;
  cx _gate_q_2, _gate_q_4;
  t _gate_q_3;
  t _gate_q_4;
  h _gate_q_4;
  cx _gate_q_2, _gate_q_3;
  t _gate_q_2;
  tdg _gate_q_3;
  cx _gate_q_2, _gate_q_3;
  rz(pi/8) _gate_q_4;
  h _gate_q_3;
  cx _gate_q_1, _gate_q_3;
  tdg _gate_q_3;
  cx _gate_q_0, _gate_q_3;
  t _gate_q_3;
  cx _gate_q_1, _gate_q_3;
  tdg _gate_q_3;
  cx _gate_q_0, _gate_q_3;
  t _gate_q_1;
  t _gate_q_3;
  h _gate_q_3;
  cx _gate_q_0, _gate_q_1;
  t _gate_q_0;
  tdg _gate_q_1;
  cx _gate_q_0, _gate_q_1;
  rz(-pi/16) _gate_q_3;
  cx _gate_q_2, _gate_q_3;
  rz(pi/16) _gate_q_3;
  h _gate_q_3;
  cx _gate_q_1, _gate_q_3;
  tdg _gate_q_3;
  cx _gate_q_0, _gate_q_3;
  t _gate_q_3;
  cx _gate_q_1, _gate_q_3;
  tdg _gate_q_3;
  cx _gate_q_0, _gate_q_3;
  t _gate_q_1;
  t _gate_q_3;
  h _gate_q_3;
  cx _gate_q_0, _gate_q_1;
  t _gate_q_0;
  tdg _gate_q_1;
  cx _gate_q_0, _gate_q_1;
  rz(-pi/16) _gate_q_3;
  cx _gate_q_2, _gate_q_3;
  rz(pi/16) _gate_q_3;
  cx _gate_q_0, _gate_q_2;
  rz(-pi/32) _gate_q_2;
  cx _gate_q_1, _gate_q_2;
  rz(pi/32) _gate_q_2;
  cx _gate_q_0, _gate_q_2;
  rz(-pi/32) _gate_q_2;
  cx _gate_q_1, _gate_q_2;
  rz(pi/32) _gate_q_2;
  crz(pi/16) _gate_q_0, _gate_q_1;
  p(pi/32) _gate_q_0;
}
gate mcx _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4, _gate_q_5 {
  h _gate_q_5;
  mcphase _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4, _gate_q_5;
  h _gate_q_5;
}
qubit[6] q;
mcx q[0], q[1], q[2], q[3], q[4], q[5];
```
 

### What should happen?

The mcphase gate definition should not include an angle parameter when no such parameter is used in the definition. At the very least the qasm generated by qiskit.qasm3.dump should be correct enough to be parseable.

</details>

## Issue discussion, including closing and resolving comments

All fetched issue comments are preserved below in upstream chronological
order, including any closing or resolving comments. Comments are
third-party statements, not automatically verified benchmark claims.

### Comment 5524384032 by @GauravSinghgit

Posted: 2026-09-03T10:34:24Z. Updated: 2026-09-03T10:34:24Z.

Source: https://github.com/Qiskit/qiskit/issues/16919#issuecomment-5524384032

<details>
<summary>Full comment by @GauravSinghgit</summary>

# Proposal: Fix QASM3 Export of Parameterized Controlled Gates

The QASM3 exporter currently generates invalid QASM3 for `MCXGate` with 5 or more controls. Its decomposition contains an `MCPhaseGate` whose definition expects a parameter, but the generated gate call omits it.

### Root Cause

In `qiskit/qasm3/exporter.py`, `build_gate_call()` uses `instruction.params` to build the gate-call parameters. For the affected decomposed operation:

```text
operation.params = [pi]
instruction.params = []
```

This causes the generated `mcphase` call to have zero parameters despite its definition requiring one.

### Proposed Fix

Change:

```python
parameters = self._build_quantum_call_parameters(instruction.params)
```

to:

```python
parameters = self._build_quantum_call_parameters(operation.params)
```

This ensures the gate call uses the parameters of the actual operation being exported.

### Validation

The existing Qiskit QASM3 test suites pass:

```text
test.python.qasm3.test_export
Ran 118 tests — OK

test.python.qasm3.test_import
Ran 18 tests — OK
```

The original issue reproducer also now successfully exports and re-imports the generated QASM3.

The change is minimal and isolated to `build_gate_call()`.

**If this approach looks good, could you please assign this issue to me? I would like to proceed with creating the PR.**


</details>

### Comment 5525028925 by @ShellyGarion

Posted: 2026-09-03T11:29:42Z. Updated: 2026-09-03T11:29:42Z.

Source: https://github.com/Qiskit/qiskit/issues/16919#issuecomment-5525028925

<details>
<summary>Full comment by @ShellyGarion</summary>

I think that perhaps this PR may fix it? https://github.com/Qiskit/qiskit/pull/16781
If so, this was fixed in both the main and stable branches. Could you please check it?

</details>

### Comment 5534225404 by @cnakhl

Posted: 2026-09-04T01:09:29Z. Updated: 2026-09-04T01:09:29Z.

Source: https://github.com/Qiskit/qiskit/issues/16919#issuecomment-5534225404

<details>
<summary>Full comment by @cnakhl</summary>

Yes that indeed fixes the problem, thanks!

</details>


## Closure and reopening events

- 2026-09-04T01:09:37Z: closed by @cnakhl.

Closing an issue does not establish that a code fix was merged or released.

## Attribution and reuse

The original post and comments remain attributed to their upstream authors.
Their inclusion does not relicense them under this project's MIT license.
See [NOTICE](../../NOTICE). Machine-readable text and provenance are in
[source.json](source.json); curated version evidence is in
[the manifest](../manifest.json). Attachments are linked, not vendored.
