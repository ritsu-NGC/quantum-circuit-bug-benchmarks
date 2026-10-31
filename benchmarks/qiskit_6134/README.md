# Qiskit issue #6134: Controlled HamiltonianGate seems to be wrong

## Benchmark metadata

| Field | Value |
| --- | --- |
| Original issue | https://github.com/Qiskit/qiskit/issues/6134 |
| Source repository | `Qiskit/qiskit` |
| Original author | @Cryoris |
| Reported Qiskit version(s) at the issue | Not specified |
| Verified Qiskit version(s) containing the fix | `0.18.0` |
| Assessment | Confirmed bug |
| Upstream state at snapshot | closed (completed) |
| Created | 2021-04-01T15:57:46Z |
| Last upstream update | 2021-04-08T03:29:39Z |
| Closed | 2021-04-08T03:29:39Z |
| Retrieved | 2026-10-30T17:28:03+00:00 |

**Reported-version context:** The original environment reports master at commit 49baa6ee5222bc497951423afa0fc7cbdb434702, not a numerical Terra release.

**Assessment:** Nested unrolling drops global phase before controlling a Hamiltonian circuit. The reference is the equivalent controlled exponentiated UnitaryGate.

**Resolution:** Merged Unroller fix #6155 is verified in qiskit-terra 0.18.0. An earlier maintenance-branch fix is not asserted.

Reported versions are not an exhaustive affected range. A verified fixed
version is a published release containing the fix, not necessarily the
first fixed version across all maintenance branches. Historical fixed
release versions below 1.0 refer to `qiskit-terra`, not the old `qiskit`
metapackage. Reported versions retain their original distribution context.

## Fix and resolution evidence


### Verified fixed release: 0.18.0

- Distribution: `qiskit-terra`.
- Original fix: https://github.com/Qiskit/qiskit/pull/6155.
- Included fix/backport PR: https://github.com/Qiskit/qiskit/pull/6155.
- Merged: 2021-04-08T03:29:39Z.
- Fix commit: `8c41a8d1466bcc7f3770c61aa8885cca81f10a06`.
- Published release: https://github.com/Qiskit/qiskit/releases/tag/0.18.0 (2021-07-12T19:26:41Z).
- Ancestry comparison: https://github.com/Qiskit/qiskit/compare/8c41a8d1466bcc7f3770c61aa8885cca81f10a06...0.18.0.
- Verification: Fix merge commit is an ancestor of the published release tag.
- Verified at: 2026-10-30T17:28:03+00:00.

## Original issue post

The body below is reproduced verbatim from the original issue post as
returned by GitHub at retrieval time. It may include upstream edits,
mistakes, HTML, and externally hosted attachments. It is not a
reconstruction of the issue's initial, pre-edit revision.

Source: https://github.com/Qiskit/qiskit/issues/6134 by @Cryoris.

<details>
<summary>Full original issue text</summary>

<!-- ⚠️ If you do not respect this template, your issue will be closed -->
<!-- ⚠️ Make sure to browse the opened and closed issues -->

### Information

- **Qiskit Terra version**: master @ 49baa6ee5222bc497951423afa0fc7cbdb434702
- **Python version**: 3.7.9
- **Operating system**: macOS Big Sur

### What is the current behavior?

Controlled the `HamiltonianGate` seems to produce wrong results, whereas manually exponentiating and then using the `UnitaryGate` works fine.

### Steps to reproduce the problem

```python
import numpy as np
import scipy as sc

from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

np.set_printoptions(precision=2)

matrix = np.array([[2, 1], [1, 2]])
evolved = sc.linalg.expm(1j * matrix)

u = QuantumCircuit(1)
u.unitary(evolved, [0])

h = QuantumCircuit(1)
h.hamiltonian(matrix, -1, [0])

print('Unitary of e^(-matrix)')
print(Operator(u).data)

print('Hamiltonian of matrix')
print(Operator(h).data)

print('Controlled unitary of e^(-matrix)')
# so that the matrix of the controlled gate uses the "physics order", reverse bits
print(Operator(u.control().reverse_bits()).data)  

print('Controlled hamiltonian of matrix')
print(Operator(h.control().reverse_bits()).data)
```

This yields:
```
Unitary of e^(-matrix)
[[-0.22+0.49j -0.77-0.35j]
 [-0.77-0.35j -0.22+0.49j]]
Hamiltonian of matrix
[[-0.22+0.49j -0.77-0.35j]
 [-0.77-0.35j -0.22+0.49j]]
Controlled unitary of e^(-matrix)
[[ 1.  +0.j    0.  +0.j    0.  +0.j    0.  +0.j  ]
 [ 0.  +0.j    1.  +0.j    0.  +0.j    0.  +0.j  ]
 [ 0.  +0.j    0.  +0.j   -0.22+0.49j -0.77-0.35j]
 [ 0.  +0.j    0.  +0.j   -0.77-0.35j -0.22+0.49j]]
Controlled hamiltonian of matrix
[[ 1.00e+00+0.00e+00j  0.00e+00+0.00e+00j  0.00e+00+0.00e+00j 0.00e+00+0.00e+00j]
 [ 0.00e+00+0.00e+00j  1.00e+00+0.00e+00j  0.00e+00+0.00e+00j 0.00e+00+0.00e+00j]
 [ 0.00e+00+0.00e+00j  0.00e+00+0.00e+00j  5.40e-01+0.00e+00j 1.55e-16+8.41e-01j]
 [ 0.00e+00+0.00e+00j  0.00e+00+0.00e+00j -1.35e-16+8.41e-01j 5.40e-01-1.32e-16j]]
```


### What is the expected behavior?

Controlling the `HamiltonianGate` (and reversing bits) should produce this matrix:
```
[[ 1.  +0.j    0.  +0.j    0.  +0.j    0.  +0.j  ]
 [ 0.  +0.j    1.  +0.j    0.  +0.j    0.  +0.j  ]
 [ 0.  +0.j    0.  +0.j   -0.22+0.49j -0.77-0.35j]
 [ 0.  +0.j    0.  +0.j   -0.77-0.35j -0.22+0.49j]]
 ```

### Suggested solutions

Check what's going on in `HamiltonianGate.control`, maybe it's a relative phase that's introduced.


</details>

## Issue discussion, including closing and resolving comments

All fetched issue comments are preserved below in upstream chronological
order, including any closing or resolving comments. Comments are
third-party statements, not automatically verified benchmark claims.

### Comment 812820047 by @paniash

Posted: 2021-04-03T06:19:19Z. Updated: 2021-04-03T06:19:19Z.

Source: https://github.com/Qiskit/qiskit/issues/6134#issuecomment-812820047

<details>
<summary>Full comment by @paniash</summary>

@Cryoris Under `extensions/hamiltonian_gate.py`, I don't see a `.control` method for the `HamiltonianGate` class. Any ideas where I can look into this?

</details>

### Comment 812930420 by @ewinston

Posted: 2021-04-03T21:51:43Z. Updated: 2021-04-03T21:51:43Z.

Source: https://github.com/Qiskit/qiskit/issues/6134#issuecomment-812930420

<details>
<summary>Full comment by @ewinston</summary>

@paniash The `control` method is implemented in the parent `Gate` class.

</details>

### Comment 812931995 by @ewinston

Posted: 2021-04-03T22:07:04Z. Updated: 2021-04-03T22:07:04Z.

Source: https://github.com/Qiskit/qiskit/issues/6134#issuecomment-812931995

<details>
<summary>Full comment by @ewinston</summary>

I noticed that when you create a HamiltonianGate directly it looks ok,
```python
        evo = scipy.linalg.expm(-1j * hami * tdelta)
        cevo = _compute_control_matrix(evo, 1)
        print('-'*5 + 'hamiltonian')
        print(hami)
        print('-'*5 + 'evolution operator')
        print(evo)
        print('-'*5 + 'controlled evolution operator')        
        print(cevo)


        print('-'*5 + 'HamiltonianGate as QuantumCircuit')
        hami_circ = QuantumCircuit(1, name='hami_circ')
        hami_circ.hamiltonian(hami, -1, [0])
        chami_circ = hami_circ.control()
        print(Operator(hami_circ).data)
        print(Operator(chami_circ).data)

        print('-'*5 + 'HamiltonianGate as Gate appended to QuantumCircuit')
        hami_gate = HamiltonianGate(hami, tdelta)
        chami_gate = hami_gate.control()
        chami_circuit = QuantumCircuit(2, name='hami_circ')
        chami_circuit.append(chami_gate, [0, 1])
        print(Operator(chami_gate).data)
        print(Operator(chami_circuit).data)   
```
prints;
```
-----hamiltonian
[[2 1]
 [1 2]]
-----evolution operator
[[-0.22-0.49j -0.77+0.35j]
 [-0.77+0.35j -0.22-0.49j]]
-----controlled evolution operator
[[ 1.  +0.j    0.  +0.j    0.  +0.j    0.  +0.j  ]
 [ 0.  +0.j   -0.22-0.49j  0.  +0.j   -0.77+0.35j]
 [ 0.  +0.j    0.  +0.j    1.  +0.j    0.  +0.j  ]
 [ 0.  +0.j   -0.77+0.35j  0.  +0.j   -0.22-0.49j]]

-----HamiltonianGate as QuantumCircuit
hami_circ
                              
control_0: ─────────■─────────
           ┌────────┴────────┐
 target_0: ┤ U(2,π/2,3π/2,0) ├
           └─────────────────┘
[[-0.22+0.49j -0.77-0.35j]
 [-0.77-0.35j -0.22+0.49j]]
[[1.  +0.j   0.  +0.j   0.  +0.j   0.  +0.j  ]
 [0.  +0.j   0.54+0.j   0.  +0.j   0.  +0.84j]
 [0.  +0.j   0.  +0.j   1.  +0.j   0.  +0.j  ]
 [0.  +0.j   0.  +0.84j 0.  +0.j   0.54-0.j  ]]

-----HamiltonianGate as Gate appended to QuantumCircuit
gate hamiltonian has phase of -1.9999999999999998
hamiltonian
                              ┌───────┐
control_0: ─────────■─────────┤ P(-2) ├
           ┌────────┴────────┐└───────┘
 target_0: ┤ U(2,3π/2,π/2,0) ├─────────
           └─────────────────┘         
[[ 1.  +0.j    0.  +0.j    0.  +0.j    0.  +0.j  ]
 [ 0.  +0.j   -0.22-0.49j  0.  +0.j   -0.77+0.35j]
 [ 0.  +0.j    0.  +0.j    1.  +0.j    0.  +0.j  ]
 [ 0.  +0.j   -0.77+0.35j  0.  +0.j   -0.22-0.49j]]
[[ 1.  +0.j    0.  +0.j    0.  +0.j    0.  +0.j  ]
 [ 0.  +0.j   -0.22-0.49j  0.  +0.j   -0.77+0.35j]
 [ 0.  +0.j    0.  +0.j    1.  +0.j    0.  +0.j  ]
 [ 0.  +0.j   -0.77+0.35j  0.  +0.j   -0.22-0.49j]]


</details>

### Comment 812968549 by @ewinston

Posted: 2021-04-04T04:17:24Z. Updated: 2021-04-04T04:17:24Z.

Source: https://github.com/Qiskit/qiskit/issues/6134#issuecomment-812968549

<details>
<summary>Full comment by @ewinston</summary>

This may actually be an issue with the Unroller preserving global phase;
```python
        from qiskit.transpiler.passes.basis import Unroller
        from qiskit.transpiler import PassManager
        hami = np.array([[2, 1], [1, 2]])
        hami_gate = HamiltonianGate(hami, 1)
        hami_circ = QuantumCircuit(1)
        hami_circ.append(hami_gate, [0])
        pm = PassManager()
        pm.append(Unroller(['u']))
        unrolled_hami_circ = pm.run(hami_circ)
        np.set_printoptions(precision=2, linewidth=200, suppress=True)
        print(Operator(hami_circ).data)
        print(Operator(unrolled_hami_circ).data)        
```
yields,
```
[[-0.22-0.49j -0.77+0.35j]
 [-0.77+0.35j -0.22-0.49j]]

[[ 0.54+0.j   -0.  -0.84j]
 [-0.  -0.84j  0.54-0.j  ]]
```

</details>


## Closure and reopening events

- 2021-04-08T03:29:39Z: closed by @mergify[bot].

Closing an issue does not establish that a code fix was merged or released.

## Attribution and reuse

The original post and comments remain attributed to their upstream authors.
Their inclusion does not relicense them under this project's MIT license.
See [NOTICE](../../NOTICE). Machine-readable text and provenance are in
[source.json](source.json); curated version evidence is in
[the manifest](../manifest.json). Attachments are linked, not vendored.
