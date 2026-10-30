# Qiskit issue #16168: MultiplierGate(1, 1).decompose() fails because its definition has the wrong number of qubits

## Benchmark metadata

| Field | Value |
| --- | --- |
| Original issue | https://github.com/Qiskit/qiskit/issues/16168 |
| Source repository | `Qiskit/qiskit` |
| Original author | @Timeless-hep |
| Reported Qiskit version(s) at the issue | `2.4.1` |
| Verified Qiskit version(s) containing the fix | `2.4.2`, `2.5.0` |
| Assessment | Confirmed bug |
| Upstream state at snapshot | closed (completed) |
| Created | 2026-05-12T05:49:59Z |
| Last upstream update | 2026-06-09T09:21:23Z |
| Closed | 2026-06-09T09:21:23Z |
| Retrieved | 2026-10-30T17:28:03+00:00 |

**Reported-version context:** Version(s) reported in the original issue environment; not a first-affected boundary.

**Assessment:** Circuit-definition width bug: MultiplierGate(1,1) declares three qubits but generates a four-qubit definition, making decomposition fail.

**Resolution:** Merged fix #16394 is verified in 2.5.0, and a stable backport is verified in 2.4.2. Comments mentioning other unmerged proposals are not treated as proof that those proposals shipped.

Reported versions are not an exhaustive affected range. A verified fixed
version is a published release containing the fix, not necessarily the
first fixed version across all maintenance branches. Historical fixed
release versions below 1.0 refer to `qiskit-terra`, not the old `qiskit`
metapackage. Reported versions retain their original distribution context.

## Fix and resolution evidence


### Verified fixed release: 2.4.2

- Distribution: `qiskit`.
- Original fix: https://github.com/Qiskit/qiskit/pull/16394.
- Included fix/backport PR: https://github.com/Qiskit/qiskit/pull/16399.
- Merged: 2026-06-09T11:10:39Z.
- Fix commit: `b75807b84298b7e851479e43c72cf883671a2b19`.
- Published release: https://github.com/Qiskit/qiskit/releases/tag/2.4.2 (2026-06-12T17:39:03Z).
- Ancestry comparison: https://github.com/Qiskit/qiskit/compare/b75807b84298b7e851479e43c72cf883671a2b19...2.4.2.
- Verification: Fix merge commit is an ancestor of the published release tag.
- Verified at: 2026-10-30T17:28:03+00:00.

### Verified fixed release: 2.5.0

- Distribution: `qiskit`.
- Original fix: https://github.com/Qiskit/qiskit/pull/16394.
- Included fix/backport PR: https://github.com/Qiskit/qiskit/pull/16394.
- Merged: 2026-06-09T09:21:21Z.
- Fix commit: `d89a84bd7450b80211d7999bc603acbd91676f07`.
- Published release: https://github.com/Qiskit/qiskit/releases/tag/2.5.0 (2026-07-02T18:51:37Z).
- Ancestry comparison: https://github.com/Qiskit/qiskit/compare/d89a84bd7450b80211d7999bc603acbd91676f07...2.5.0.
- Verification: Fix merge commit is an ancestor of the published release tag.
- Verified at: 2026-10-30T17:28:03+00:00.

## Original issue post

The body below is reproduced verbatim from the original issue post as
returned by GitHub at retrieval time. It may include upstream edits,
mistakes, HTML, and externally hosted attachments. It is not a
reconstruction of the issue's initial, pre-edit revision.

Source: https://github.com/Qiskit/qiskit/issues/16168 by @Timeless-hep.

<details>
<summary>Full original issue text</summary>

### Environment

- **Qiskit version**: 2.4.1
- **Python version**: 3.13.13
- **Operating system**: macOS


### What is happening?

`MultiplierGate` accepts `num_result_qubits` values in the documented range `[num_state_qubits, 2 * num_state_qubits]`, but decomposing a truncated-result multiplier fails.

For example, `MultiplierGate(1, 1)` reports that it is a 3-qubit gate, which is expected because it has two 1-qubit input registers and one 1-qubit result register. However, calling `QuantumCircuit.decompose()` raises:

`DAGCircuitError: 'bit mapping invalid: expected 3, got 4'`

This suggests that the gate's generated definition has 4 qubits even though the gate itself has 3 qubits.


### How can we reproduce the issue?

```python
from qiskit import QuantumCircuit
from qiskit.circuit.library import MultiplierGate


n, t = 1, 1

gate = MultiplierGate(n, t)
print("gate.num_qubits:", gate.num_qubits)

qc = QuantumCircuit(gate.num_qubits)
qc.append(gate, range(gate.num_qubits))

print("calling qc.decompose()...")
qc.decompose()
```
Output:


gate.num_qubits: 3
calling qc.decompose()...
DAGCircuitError: 'bit mapping invalid: expected 3, got 4'



### What should happen?




`qc.decompose()` should succeed for `MultiplierGate(1, 1)`, since `num_result_qubits=1` is valid for `num_state_qubits=1`.

The decomposition should have the same number of qubits as the gate itself, i.e. 3 qubits in this example.




### Any suggestions?

The issue appears to be in `MultiplierGate._define()`.

Currently it calls:

```python
self.definition = multiplier_qft_r17(self.num_state_qubits)

```
This drops `self.num_result_qubits`, so `multiplier_qft_r17` uses its default result width of `2 * num_state_qubits`. For `MultiplierGate(1, 1)`, that creates a 4-qubit definition instead of the expected 3-qubit definition.

This can be observed with:
``` python
from qiskit.circuit.library import MultiplierGate
from qiskit.synthesis.arithmetic import multiplier_qft_r17

n, t = 1, 1
gate = MultiplierGate(n, t)

definition_width = gate.definition.num_qubits
correct_width = multiplier_qft_r17(n, t).num_qubits

print("gate width:", gate.num_qubits)
print("definition width:", definition_width)
print("correct synthesis width:", correct_width)
```
Expected fix may be to pass self.num_result_qubits through:
``` python
self.definition = multiplier_qft_r17(
    self.num_state_qubits,
    self.num_result_qubits,
)
```


</details>

## Issue discussion, including closing and resolving comments

All fetched issue comments are preserved below in upstream chronological
order, including any closing or resolving comments. Comments are
third-party statements, not automatically verified benchmark claims.

### Comment 4428987086 by @Cryoris

Posted: 2026-05-12T09:08:57Z. Updated: 2026-05-12T09:08:57Z.

Source: https://github.com/Qiskit/qiskit/issues/16168#issuecomment-4428987086

<details>
<summary>Full comment by @Cryoris</summary>

Thanks for the report! Your suggestion sounds like the correct fix, would you like to open a bugfix PR?

</details>

### Comment 4440104245 by @Timeless-hep

Posted: 2026-05-13T10:50:00Z. Updated: 2026-05-13T10:50:00Z.

Source: https://github.com/Qiskit/qiskit/issues/16168#issuecomment-4440104245

<details>
<summary>Full comment by @Timeless-hep</summary>

It seems @cfcryptotrader-rgb has fixed it. Glad to see this getting fixed!

</details>

### Comment 4556620362 by @Jah-yee

Posted: 2026-05-27T16:44:24Z. Updated: 2026-05-27T16:44:24Z.

Source: https://github.com/Qiskit/qiskit/issues/16168#issuecomment-4556620362

<details>
<summary>Full comment by @Jah-yee</summary>

Fixed in #16288. The issue was in `MultiplierGate._define()` — it wasn't passing `num_result_qubits` to `multiplier_qft_r17`. One line fix.


</details>


## Closure and reopening events

- 2026-06-09T09:21:23Z: closed by @ShellyGarion.

Closing an issue does not establish that a code fix was merged or released.

## Attribution and reuse

The original post and comments remain attributed to their upstream authors.
Their inclusion does not relicense them under this project's MIT license.
See [NOTICE](../../NOTICE). Machine-readable text and provenance are in
[source.json](source.json); curated version evidence is in
[the manifest](../manifest.json). Attachments are linked, not vendored.
