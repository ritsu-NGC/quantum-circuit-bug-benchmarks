# Qiskit issue #86: Bug in cu3 implementation

## Benchmark metadata

| Field | Value |
| --- | --- |
| Original issue | https://github.com/Qiskit/qiskit/issues/86 |
| Source repository | `Qiskit/qiskit` |
| Original author | @yoonbo |
| Reported Qiskit version(s) at the issue | `0.3.5` |
| Verified Qiskit version(s) containing the fix | Not applicable |
| Assessment | Explained upstream as not a bug |
| Upstream state at snapshot | closed (completed) |
| Created | 2017-09-26T21:31:05Z |
| Last upstream update | 2017-09-27T05:30:08Z |
| Closed | 2017-09-27T04:38:17Z |
| Retrieved | 2026-10-30T17:28:03+00:00 |

**Reported-version context:** The original report names Qiskit SDK 0.3.5, predating the historical Qiskit/Terra distribution split.

**Assessment:** The closing maintainer comment explicitly says this report is not a bug: the demonstrated output states differ only by a global phase. This entry is retained solely because it appeared in the initial list.

**Resolution:** Closed as explained/expected behavior; no code fix or fixed version should be inferred. The earlier research summary overstated this as a relative-phase bug.

Reported versions are not an exhaustive affected range. A verified fixed
version is a published release containing the fix, not necessarily the
first fixed version across all maintenance branches. Historical fixed
release versions below 1.0 refer to `qiskit-terra`, not the old `qiskit`
metapackage. Reported versions retain their original distribution context.

## Fix and resolution evidence

- https://github.com/Qiskit/qiskit/issues/86#issuecomment-332406713

## Original issue post

The body below is reproduced verbatim from the original issue post as
returned by GitHub at retrieval time. It may include upstream edits,
mistakes, HTML, and externally hosted attachments. It is not a
reconstruction of the issue's initial, pre-edit revision.

Source: https://github.com/Qiskit/qiskit/issues/86 by @yoonbo.

<details>
<summary>Full original issue text</summary>

<!--- Provide a general summary of the issue in the Title above -->

cu3(pi, 0, pi) gate should work as controlled X gate, but it is not.

## Expected Behavior
<!--- If you're describing a bug, tell us what should happen -->
<!--- If you're suggesting a change/improvement, tell us how it should work -->

cx: (1, 0) ---> (0, 1)
cu3(pi, 0, pi) : (1, 0) ---> (0, 1)

## Current Behavior
<!--- If describing a bug, tell us what happens instead of the expected behavior -->
<!--- If suggesting a change/improvement, explain the difference from current behavior -->

cx: (1, 0) ---> (0, 1)
cu3(pi, 0, pi) : (1, 0) ---> (0, -i)

## Steps to Reproduce (for bugs)
<!--- Provide a link to a live example, or an unambiguous set of steps to -->
<!--- reproduce this bug. Include code to reproduce, if relevant -->
```
import numpy as np

sys.path.append("../qiskit-sdk-py/")

from qiskit import QuantumProgram
import Qconfig

np.set_printoptions(precision=2)

Q_program = QuantumProgram()
n = 2
q = Q_program.create_quantum_register('q', n)
c = Q_program.create_classical_register('c', n)
  
state = Q_program.create_circuit('bug', [q], [c])

state.x(q[0])
state.cx(q[0], q[1])

state.measure(q[1], c[1])

backend = 'local_qasm_simulator'
result = Q_program.execute(['bug'], backend=backend, shots=1, silent = True)
print("Controlled X gate:")
print(result.get_data('bug')['quantum_state'])

print("")


Q_program = QuantumProgram()
n = 2
q = Q_program.create_quantum_register('q', n)
c = Q_program.create_classical_register('c', n)
  
state = Q_program.create_circuit('bug', [q], [c])

state.x(q[0])
state.cu3(np.pi, 0.0, np.pi, q[0], q[1])

state.measure(q[1], c[1])

backend = 'local_qasm_simulator'
result = Q_program.execute(['bug'], backend=backend, shots=1, silent = True)
print("CU3(pi, 0, pi) gate:")
print(result.get_data('bug')['quantum_state'])
```

Above code prints out

```
Controlled X gate:
[ 0.+0.j  0.+0.j  0.+0.j  1.+0.j]

CU3(pi, 0, pi) gate:
[  0.00e+00+0.j   0.00e+00+0.j   0.00e+00+0.j   6.12e-17-1.j]
```

## Your Environment
<!--- Include as many relevant details about the environment you experienced the bug in -->
* Version used: 0.3.5
* Environment name and version (e.g. Python 3.6.1): Python 3.6.2
* Operating System and version: OSX

</details>

## Issue discussion, including closing and resolving comments

All fetched issue comments are preserved below in upstream chronological
order, including any closing or resolving comments. Comments are
third-party statements, not automatically verified benchmark claims.

### Comment 332378296 by @rraymondhp

Posted: 2017-09-27T01:02:01Z. Updated: 2017-09-27T01:03:59Z.

Source: https://github.com/Qiskit/qiskit/issues/86#issuecomment-332378296

<details>
<summary>Full comment by @rraymondhp</summary>

Hi,  

But, essentially the state 
`[ 0.+0.j  0.+0.j  0.+0.j  1.+0.j]` and the state 
`[  0.00e+00+0.j   0.00e+00+0.j   0.00e+00+0.j   6.12e-17-1.j]` 
are the same up to global phase `-j`. I have confirmed that the `cu3` with target `1` results in essentially the same state with `cx` up to the global phase `-j`. 

Please refer to: 
https://en.wikipedia.org/wiki/Quantum_state
```... A unit vector is usually picked, but its phase factor can be chosen freely anyway. Nevertheless, such factors are important when state vectors are added together to form a superposition.```

</details>

### Comment 332406713 by @jaygambetta

Posted: 2017-09-27T04:38:17Z. Updated: 2017-09-27T04:38:17Z.

Source: https://github.com/Qiskit/qiskit/issues/86#issuecomment-332406713

<details>
<summary>Full comment by @jaygambetta</summary>

@yoonbo and @rraymondhp this is correct. It is not a bug it is just a global phase that quantum computers can't be see. I suggest if you look at |<psi_expected|psi_made>|^2 and if this is one then the states are the same. 

</details>

### Comment 332413062 by @rraymondhp

Posted: 2017-09-27T05:30:08Z. Updated: 2017-09-27T05:30:08Z.

Source: https://github.com/Qiskit/qiskit/issues/86#issuecomment-332413062

<details>
<summary>Full comment by @rraymondhp</summary>

Thanks. I also wrote about the global phase equivalence of `u3` gate in the tutorial below:
https://nbviewer.jupyter.org/github/QISKit/qiskit-tutorial/blob/master/1_introduction/quantum_gates_and_linear_algebra.ipynb



</details>


## Closure and reopening events

- 2017-09-27T04:38:17Z: closed by @jaygambetta.

Closing an issue does not establish that a code fix was merged or released.

## Attribution and reuse

The original post and comments remain attributed to their upstream authors.
Their inclusion does not relicense them under this project's MIT license.
See [NOTICE](../../NOTICE). Machine-readable text and provenance are in
[source.json](source.json); curated version evidence is in
[the manifest](../manifest.json). Attachments are linked, not vendored.
