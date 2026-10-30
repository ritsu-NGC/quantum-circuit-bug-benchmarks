# Qiskit issue #7209: `C3SXGate` inconsistent with `SXGate`

## Benchmark metadata

| Field | Value |
| --- | --- |
| Original issue | https://github.com/Qiskit/qiskit/issues/7209 |
| Source repository | `Qiskit/qiskit` |
| Original author | @jakelishman |
| Reported Qiskit version(s) at the issue | `0.18.3` |
| Verified Qiskit version(s) containing the fix | `0.19.0` |
| Assessment | Confirmed bug |
| Upstream state at snapshot | closed (completed) |
| Created | 2021-11-02T12:27:31Z |
| Last upstream update | 2021-11-15T14:34:03Z |
| Closed | 2021-11-09T14:28:37Z |
| Retrieved | 2026-10-30T17:28:03+00:00 |

**Reported-version context:** Version(s) reported in the original issue environment; not a first-affected boundary.

**Assessment:** C3SXGate's definition implements SXdg.control(3), not its documented base operation SX.control(3).

**Resolution:** Merged decomposition fix #7230 is verified in qiskit-terra 0.19.0.

Reported versions are not an exhaustive affected range. A verified fixed
version is a published release containing the fix, not necessarily the
first fixed version across all maintenance branches. Historical fixed
release versions below 1.0 refer to `qiskit-terra`, not the old `qiskit`
metapackage. Reported versions retain their original distribution context.

## Fix and resolution evidence


### Verified fixed release: 0.19.0

- Distribution: `qiskit-terra`.
- Original fix: https://github.com/Qiskit/qiskit/pull/7230.
- Included fix/backport PR: https://github.com/Qiskit/qiskit/pull/7230.
- Merged: 2021-11-09T14:28:37Z.
- Fix commit: `49110f9c596fc509f189f38cfbdbb3100407bff2`.
- Published release: https://github.com/Qiskit/qiskit/releases/tag/0.19.0 (2021-12-06T19:43:40Z).
- Ancestry comparison: https://github.com/Qiskit/qiskit/compare/49110f9c596fc509f189f38cfbdbb3100407bff2...0.19.0.
- Verification: Fix merge commit is an ancestor of the published release tag.
- Verified at: 2026-10-30T17:28:03+00:00.

## Original issue post

The body below is reproduced verbatim from the original issue post as
returned by GitHub at retrieval time. It may include upstream edits,
mistakes, HTML, and externally hosted attachments. It is not a
reconstruction of the issue's initial, pre-edit revision.

Source: https://github.com/Qiskit/qiskit/issues/7209 by @jakelishman.

<details>
<summary>Full original issue text</summary>

<!-- ⚠️ If you do not respect this template, your issue will be closed -->
<!-- ⚠️ Make sure to browse the opened and closed issues -->

### Information

- **Qiskit Terra version**: 0.18.3
- **Python version**: any
- **Operating system**: any

### What is the current behavior?

The definition of `C3SXGate()` is currently equivalent to `SXdgGate.control(3)`, but its name and its base gate definition indicate it should be equivalent to `SXgate.control(3)`.


### Steps to reproduce the problem

```python
In [1]: from qiskit.circuit.library import SXGate, SXdgGate, C3SXGate
   ...: from qiskit.quantum_info import Operator
   ...: import numpy as np
   ...:
   ...: (
   ...:     np.linalg.norm(Operator(SXGate().control(3)) - Operator(C3SXGate())),
   ...:     np.linalg.norm(Operator(SXdgGate().control(3)) - Operator(C3SXGate())),
   ...: )
Out[1]: (1.9999999999999984, 6.088839805355096e-15)
```

### What is the expected behavior?

`C3SXGate` should be consistent with `SXGate().control(3)`.


### Suggested solutions

Swap the negatives of the angles in `C3SXGate.definition`.  There's a fair amount more to do as well to ensure consistency - checking the equivalence library, QASM definitions, etc.

</details>

## Issue discussion, including closing and resolving comments

All fetched issue comments are preserved below in upstream chronological
order, including any closing or resolving comments. Comments are
third-party statements, not automatically verified benchmark claims.

### Comment 960243576 by @wahaj

Posted: 2021-11-03T22:27:34Z. Updated: 2021-11-03T22:27:34Z.

Source: https://github.com/Qiskit/qiskit/issues/7209#issuecomment-960243576

<details>
<summary>Full comment by @wahaj</summary>

I have taken a look at it and it seems flipping the angles makes it work. I have tested the equivalence among these two comparing a circuit in which a C3SX gate was added with the SXGate with control, it passes the equivalence decomposition. What else is required for consistency? 

</details>

### Comment 960660000 by @jakelishman

Posted: 2021-11-04T11:14:19Z. Updated: 2021-11-04T11:14:19Z.

Source: https://github.com/Qiskit/qiskit/issues/7209#issuecomment-960660000

<details>
<summary>Full comment by @jakelishman</summary>

The test suite doesn't pass if all you do is flip the angles in the `C3SXGate` class, because the `C4XGate` class depends on it for its definition, and there's also a redefinition in the QASM 2 library file `qelib1.inc` (and a `c4x` in there too).  Everything needs to stay consistent if one gate changes.  There don't appear to be any defined equivalences in the equivalence library, so that part's not a problem.

However, I'm not even sure if the change is correct - I don't know if there's context as to why the `C3SXGate` disagrees with `SXGate.control(3)`; there might be a reason for the redefinition.  After all, this form of `C3SXGate` applied twice still does produce a `C3XGate`, so in a vacuum, it's not entirely wrong.

Perhaps @Cryoris knows more - the gate was added in #5668.

</details>

### Comment 961263441 by @wahaj

Posted: 2021-11-04T17:30:35Z. Updated: 2021-11-04T17:30:35Z.

Source: https://github.com/Qiskit/qiskit/issues/7209#issuecomment-961263441

<details>
<summary>Full comment by @wahaj</summary>

Well, maybe the problem isn't in the `C3SXGate` class, because it is defined using the decomposition that is theoretically correct. Since the `C4XGate` also works fine using it as a base, maybe the problem isn't in the `C3SXGate` class, but rather there may be something funky going on in the `control` method of the `SXGate` class, with problems popping up with more than 2 units of control. Since the `C4XGate` and the `XGate` with 4 control bits is equivalent, maybe the phase transition could be changed in the `SXGate` to accomodate that.

Any thoughts on this ?

</details>

### Comment 961299237 by @jakelishman

Posted: 2021-11-04T18:15:58Z. Updated: 2021-11-04T18:15:58Z.

Source: https://github.com/Qiskit/qiskit/issues/7209#issuecomment-961299237

<details>
<summary>Full comment by @jakelishman</summary>

The control method is fine - it just defers to the standard `Gate.control` decomposition, and you can just see in the tensor-product structure of the output matrix that it's correct in this simple case.  If you construct the controlled gate matrix with `np.kron`, it's clear:
```python
In [1]: import qiskit
   ...: import numpy as np
   ...:
   ...: np.set_printoptions(suppress=True)  # suppress very small values in prints
   ...:
   ...: sx = np.array(qiskit.circuit.library.SXGate())
   ...: control_state = np.array([0]*7 + [1])  # control on |111>
   ...: i3 = np.eye(8)
   ...: proj = np.outer(control_state.conj(), control_state)
   ...: np.kron(np.eye(2), i3 - proj) + np.kron(sx, proj)
Out[1]:
array([[1. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j ],
       [0. +0.j , 1. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j ],
       [0. +0.j , 0. +0.j , 1. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j ],
       [0. +0.j , 0. +0.j , 0. +0.j , 1. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j ],
       [0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 1. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j ],
       [0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 1. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j ],
       [0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 1. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j ],
       [0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0.5+0.5j, 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0.5-0.5j],
       [0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 1. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j ],
       [0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 1. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j ],
       [0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 1. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j ],
       [0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 1. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j ],
       [0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 1. +0.j , 0. +0.j , 0. +0.j , 0. +0.j ],
       [0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 1. +0.j , 0. +0.j , 0. +0.j ],
       [0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 1. +0.j , 0. +0.j ],
       [0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0.5-0.5j, 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0. +0.j , 0.5+0.5j]])

In [2]: np.array(qiskit.quantum_info.Operator(qiskit.circuit.library.C3SXGate()))
Out[2]:
array([[ 1. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ],
       [ 0. +0.j ,  1. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ],
       [ 0. +0.j ,  0. +0.j ,  1. -0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j , -0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ],
       [ 0. +0.j ,  0. +0.j ,  0. +0.j ,  1. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. -0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ],
       [ 0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  1. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j , -0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ],
       [ 0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  1. -0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ],
       [ 0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  1. -0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j , -0. +0.j ,  0. +0.j ],
       [ 0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0.5-0.5j,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0.5+0.5j],
       [ 0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  1. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ],
       [ 0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  1. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ],
       [ 0. +0.j ,  0. +0.j , -0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  1. -0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ],
       [ 0. +0.j ,  0. +0.j ,  0. +0.j ,  0. -0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  1. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ],
       [ 0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j , -0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  1. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ],
       [ 0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  1. -0.j ,  0. +0.j ,  0. +0.j ],
       [ 0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j , -0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  1. -0.j ,  0. +0.j ],
       [ 0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0.5+0.5j,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0. +0.j ,  0.5-0.5j]])
```

The problem is that `C3SXGate` is giving exactly the same matrix as `SXdgGate` with 3 controls, not `SXGate`.  This is a naming convention issue, to some degree - both `SXGate` and `SXdgGate` _could_ have been called SX, because applying either twice gets you an X, just like how either 1 or -1 is the square root of 1.  The issue is the inconsistency between the two.

Why do you say the current decomposition is theoretically correct?  It's producing the wrong result here, at least by the name of the class.

</details>

### Comment 961564465 by @wahaj

Posted: 2021-11-05T01:48:24Z. Updated: 2021-11-05T01:48:24Z.

Source: https://github.com/Qiskit/qiskit/issues/7209#issuecomment-961564465

<details>
<summary>Full comment by @wahaj</summary>

Well because it is defined according to the method described in [ Barenco et al., 1995.](https://arxiv.org/pdf/quant-ph/9503016.pdf) in 

> 7. n-bit networks. 

But looking closer, the decomposition is supposed to start and end with a _positive_ phase in the paper as opposed to starting and ending with the _negative_ phase (**pi/8**) I guess but you can have a look 

</details>

### Comment 961679023 by @Cryoris

Posted: 2021-11-05T07:26:53Z. Updated: 2021-11-05T07:26:53Z.

Source: https://github.com/Qiskit/qiskit/issues/7209#issuecomment-961679023

<details>
<summary>Full comment by @Cryoris</summary>

I think @wahaj is right, the decomposition in Qiskit has the wrong sign. The decomposition uses 
<img width="746" alt="image" src="https://user-images.githubusercontent.com/5978796/140473391-5c0a0be9-be97-41e8-a207-66fca52b43d2.png">

where `V` should be `H P(pi/8) H`, since then `V^4` equals the square root of X. Instead in the code it uses `P(-pi/8)`. 

If we fix that, we can also directly remove the deprecated `angle` keyword argument 🙂 

</details>

### Comment 961830823 by @jakelishman

Posted: 2021-11-05T11:48:03Z. Updated: 2021-11-05T11:48:03Z.

Source: https://github.com/Qiskit/qiskit/issues/7209#issuecomment-961830823

<details>
<summary>Full comment by @jakelishman</summary>

I actually found this as part of trying to remove the `angle` keyword!  Still, though - if we remove the `angle` keyword, we won't have an efficient representation for `C3SXGate().inverse()` any more (though we can always just put in a `C3SdgXGate` in theory).

I think we're actually on the same page here - flipping the angles is the same as the replacement for `V` that you're talking about, and that's what I meant by the decomposition being incorrect.

I think the decomposition of `C4XGate` may be wrong in a related manner - it produces the correct result, but since it depends on `C3SXGate` with an incorrect phase convention, its decomposition is likely wrong as well, but just in a way that happens to cancel out.  For example, if I do `Operator(C4XGate().definition)` on the current `main`, it produces the correct result.  However, if I swap the phases of `C3SXGate` over, like discussed, then `Operator(C4XGate().definition)` gives me the identity matrix.  We then also need to swap the phases in the `CU1Gate` instances of `C4XGate` to make it work.

I've PR'd a fix in #7230.

</details>

### Comment 961838264 by @Cryoris

Posted: 2021-11-05T12:01:48Z. Updated: 2021-11-05T12:01:48Z.

Source: https://github.com/Qiskit/qiskit/issues/7209#issuecomment-961838264

<details>
<summary>Full comment by @Cryoris</summary>

Good question for the inverse but maybe the default inverse is actually good enough since that should just invert every gate which should do nothing but inverting the angle.

</details>

### Comment 961842610 by @jakelishman

Posted: 2021-11-05T12:09:29Z. Updated: 2021-11-05T12:09:29Z.

Source: https://github.com/Qiskit/qiskit/issues/7209#issuecomment-961842610

<details>
<summary>Full comment by @jakelishman</summary>

We'll need to redefine its `inverse` method to dodge `ControlledGate`'s `inverse` which will mess everything up, but otherwise, yeah, it should work.  I suppose it'll invert the order of the gates as well, but that's no big deal.

</details>


## Closure and reopening events

- 2021-11-09T14:28:37Z: closed by @mergify[bot].

Closing an issue does not establish that a code fix was merged or released.

## Attribution and reuse

The original post and comments remain attributed to their upstream authors.
Their inclusion does not relicense them under this project's MIT license.
See [NOTICE](../../NOTICE). Machine-readable text and provenance are in
[source.json](source.json); curated version evidence is in
[the manifest](../manifest.json). Attachments are linked, not vendored.
