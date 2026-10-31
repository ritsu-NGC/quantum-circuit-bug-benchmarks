# Qiskit issue #16411: OptimizeAnnotated (_canonicalize_modifiers) changes the unitary for a negative fractional PowerModifier

## Benchmark metadata

| Field | Value |
| --- | --- |
| Original issue | https://github.com/Qiskit/qiskit/issues/16411 |
| Source repository | `Qiskit/qiskit` |
| Original author | @Timeless-hep |
| Reported Qiskit version(s) at the issue | `2.4.1` |
| Verified Qiskit version(s) containing the fix | Not verified |
| Assessment | Disputed report / expected behavior under discussion |
| Upstream state at snapshot | open |
| Created | 2026-06-11T08:25:40Z |
| Last upstream update | 2026-06-16T12:08:34Z |
| Closed | Not closed |
| Retrieved | 2026-10-30T17:28:03+00:00 |

**Reported-version context:** Version(s) reported in the original issue environment; not a first-affected boundary.

**Assessment:** Negative fractional matrix powers involve branch-cut semantics. The reported canonicalization can differ from the requested principal matrix power; upstream discusses the intended semantics rather than accepting the proposed rewrite as a settled fix.

**Resolution:** Issue remains open. Proposed #16438 closed without merging. No fixed release is verified.

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

Source: https://github.com/Qiskit/qiskit/issues/16411 by @Timeless-hep.

<details>
<summary>Full original issue text</summary>

### Environment

- **Qiskit version**: 2.4.1
- **Python version**: 3.13.13
- **Operating system**: macOS


### What is happening?

`_canonicalize_modifiers` rewrites a single `PowerModifier(-0.5)` into `[InverseModifier(), PowerModifier(0.5)]`, i.e. it computes `(A^-1)^0.5` instead of the requested `A^(-0.5)`. For an operator with an eigenvalue on the negative real axis (e.g. `HGate`, eigenvalue `-1`), the principal matrix-power branch makes these two **unequal**, so `OptimizeAnnotated` silently changes the circuit unitary. The two results are exact complex conjugates of each other.

### How can we reproduce the issue?

```python
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.annotated_operation import AnnotatedOperation, PowerModifier
from qiskit.circuit.library import HGate
from qiskit.quantum_info import Operator
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import OptimizeAnnotated

qc = QuantumCircuit(1)
qc.append(AnnotatedOperation(HGate(), [PowerModifier(-0.5)]), [0])
out = PassManager([OptimizeAnnotated()]).run(qc)

print("input  Operator (H^-0.5):")
print(Operator(qc).data)
print("output Operator ((H^-1)^0.5):")
print(Operator(out).data)
print("equiv:", Operator(qc).equiv(Operator(out)))
```
Output：

```
input  Operator (H^-0.5):
[[0.85355339-0.14644661j 0.35355339+0.35355339j]
 [0.35355339+0.35355339j 0.14644661-0.85355339j]]
output Operator ((H^-1)^0.5):
[[0.85355339+0.14644661j 0.35355339-0.35355339j]
 [0.35355339-0.35355339j 0.14644661+0.85355339j]]
equiv: False
```

### What should happen?

The optimized circuit must be `Operator`-equivalent to the input; `equiv` should be `True`.

### Any suggestions?

The factorization pushes the inverse into the **base** (`A -> A^-1`, then raise to `+0.5`). Under the principal branch, `A^(-p) == (A^p)^(-1)` always holds, but `A^(-p) == (A^-1)^p` does **not** (it fails wherever an eigenvalue sits on the branch cut). Verifiable:

```python
from qiskit.quantum_info import Operator
from qiskit.circuit.library import HGate
H = Operator(HGate())
print("A^(-0.5) == (A^0.5)^(-1) :", H.power(-0.5).equiv(H.power(0.5).power(-1)))  # True
print("A^(-0.5) == (A^-1)^0.5   :", H.power(-0.5).equiv(H.power(-1).power(0.5)))  # False
```

So a fix is to emit the **positive power first, then the inverse** (modifier order `[PowerModifier(p), InverseModifier()]`), or to not split negative fractional powers at all.

</details>

## Issue discussion, including closing and resolving comments

All fetched issue comments are preserved below in upstream chronological
order, including any closing or resolving comments. Comments are
third-party statements, not automatically verified benchmark claims.

### Comment 4678830609 by @jakelishman

Posted: 2026-06-11T08:51:27Z. Updated: 2026-06-11T08:51:51Z.

Source: https://github.com/Qiskit/qiskit/issues/16411#issuecomment-4678830609

<details>
<summary>Full comment by @jakelishman</summary>

This arguably isn't a bug. The matrix form has degenerate solutions: both _are_ solutions and the problem is assuming that the numerics will reliable fall on any given side of the branch cut.

The problem isn't the inverse, it's the fractional power - whenever those are involved, there's a whole bunch of questions. With those logic we could also argue that we shouldn't be able to simplify $(A^2)^{0
.5} = A$, because for things like rotation gates the square can cause an overturn and the subsequent division might fall on another side of the branch cut.

</details>

### Comment 4678896316 by @Timeless-hep

Posted: 2026-06-11T08:59:59Z. Updated: 2026-06-11T12:20:40Z.

Source: https://github.com/Qiskit/qiskit/issues/16411#issuecomment-4678896316

<details>
<summary>Full comment by @Timeless-hep</summary>

Thanks for your reply. I agree that fractional matrix powers require a branch choice. My concern is that Qiskit already makes that choice observable through AnnotatedOperation.to_matrix() and Operator.power(). But the problem comes from the following optimization. Before the pass, PowerModifier(-0.5) evaluates as A.power(-0.5); after the pass it evaluates as A.power(-1).power(0.5), and these are not equivalent. The discrepancy is caused by the canonicalization rewrite, not merely by comparing two independent numerical evaluations of the same expression. If PowerModifier is intentionally multivalued and optimization may select another root, that semantic relaxation should arguably be documented; otherwise OptimizeAnnotated is not preserving the operation represented by its input.

</details>

### Comment 4710577526 by @dmeliksetian

Posted: 2026-06-15T17:33:37Z. Updated: 2026-06-15T17:33:37Z.

Source: https://github.com/Qiskit/qiskit/issues/16411#issuecomment-4710577526

<details>
<summary>Full comment by @dmeliksetian</summary>

I'm working on a fix for this. The root cause is in `_canonicalize_modifiers` in `qiskit/circuit/annotated_operation.py` — the canonical order should be `[PowerModifier(p), InverseModifier()]` (realizing `(A^p)^{-1}`) rather than `[InverseModifier(), PowerModifier(p)]` (realizing `(A^{-1})^p`). Will open a PR shortly.

</details>

### Comment 4710580868 by @dmeliksetian

Posted: 2026-06-15T17:34:03Z. Updated: 2026-06-15T17:34:03Z.

Source: https://github.com/Qiskit/qiskit/issues/16411#issuecomment-4710580868

<details>
<summary>Full comment by @dmeliksetian</summary>

I'm working on a fix for this. The root cause is in \`_canonicalize_modifiers\` in \`qiskit/circuit/annotated_operation.py\` — the canonical order should be \`[PowerModifier(p), InverseModifier()]\` (realizing \`(A^p)^{-1}\`) rather than \`[InverseModifier(), PowerModifier(p)]\` (realizing \`(A^{-1})^p\`). Will open a PR shortly."

</details>

### Comment 4710886184 by @jakelishman

Posted: 2026-06-15T18:05:55Z. Updated: 2026-06-15T18:05:55Z.

Source: https://github.com/Qiskit/qiskit/issues/16411#issuecomment-4710886184

<details>
<summary>Full comment by @jakelishman</summary>

YujinSong-hep: yeah, I get where you're coming from.  I'm mostly finding it very unpleasant to accept the follow-on conclusion that `X.power(2).power(0.5)` can't be "optimised" to `X`, but I'm tending more and more to agree that that's _not_ a valid optimisation without knowing specific details of `X`, because of the branch-cut discontinuity.

dmeliksetian: There was clearly on-going discussion here about whether the semantics of the issue _should_ be "fixed" or not.  Please don't just set LLMs on "auto respond" to Qiskit issues; it's not helpful and your LLM is clearly just repeating points from the top comment without having read any of the discussion.  (Having LLMs open PRs without human oversight is also a violation of the contributing policy, should that occur.)

</details>

### Comment 4711102328 by @dmeliksetian

Posted: 2026-06-15T18:29:54Z. Updated: 2026-06-15T18:37:23Z.

Source: https://github.com/Qiskit/qiskit/issues/16411#issuecomment-4711102328

<details>
<summary>Full comment by @dmeliksetian</summary>

@jakelishman To clarify on the PR: it changes the canonical ordering in _canonicalize_modifiers for any modifier sequence whose total power is negative with magnitude other than 1 — emitting [PowerModifier(|p|), InverseModifier()] (realizing (A^{|p|})^{-1}) instead of the previous [InverseModifier(), PowerModifier(|p|)] (realizing (A^{-1})^{|p|}). The power-multiplication behavior (e.g. PowerModifier(2) + PowerModifier(0.5) collapsing to the identity) is untouched, so the X.power(2).power(0.5) → X question is orthogonal to this PR.

Also, to address the concern directly: this was not an automated LLM response. I used Claude Code as a development tool with active oversight throughout — the fix, the tests, and the PR were all reviewed and understood by me before being posted. The AI disclosure in the PR body is there precisely because the contributing policy asks for it, not because the process was unsupervised.

If you think the whole PowerModifier splitting behavior should be reconsidered now, I can close the PR.

</details>

### Comment 4715657275 by @alexanderivrii

Posted: 2026-06-16T06:33:13Z. Updated: 2026-06-16T06:33:13Z.

Source: https://github.com/Qiskit/qiskit/issues/16411#issuecomment-4715657275

<details>
<summary>Full comment by @alexanderivrii</summary>

I now also believe that `_canonicalize_modifiers` is not fully correct in the presence of fractional powers. At the time I wrote the code, I was under the impression that fractional powers are inherently multi-valued, so a user who writes $A^{1/2}$ is willing to accept either of the two roots as the output. 

@dmeliksetian, I don't understand your fix: we would now rewrite both $(A^2)^{-1}$ and $(A^{-1})^2$ as the former rather than the latter (instead of the other way around), but in either case one of the simplifications would be incorrect.

An alternative approach would be not to simplify certain expressions, which means that `_canonicalize_modifiers` might end up with something like ``A.power(0.5).inverse().power(0.3).inverse().power(0.1)``, without being able to combine the powers or the inverses. Though It would be nice to clearly understand and document which reductions are correct, and to apply this reductions (such as replacing ``X.power(2).power(0.5)`` by ``X`` if we agree that this is fully correct, taking principal roots into account). I do hope that for the case where we have inverses, controls, and only *integer* powers, the reduction in `_canonicalize_modifiers` is valid.

Note that there could be other places in code might make assumptions either that we can have at most one type of each modifier after canonicalization or that the order of modifiers does not matter, in particular two places where we should look are ``AnnotatedSynthesisDefault`` and ``OptimizeAnnotated``.

I am now curious how other computer algebra systems handle this sort of issues; looking at the documentation for Mathematica's [PowerExpand](https://reference.wolfram.com/language/ref/PowerExpand.html), they explicitly state that "it in general disregards all issues of branches of multivalued functions, so may not preserve the numerical values of expressions".

</details>

### Comment 4718101734 by @dmeliksetian

Posted: 2026-06-16T11:10:51Z. Updated: 2026-06-16T11:10:51Z.

Source: https://github.com/Qiskit/qiskit/issues/16411#issuecomment-4718101734

<details>
<summary>Full comment by @dmeliksetian</summary>

@alexanderivrii Our fix specifically addresses the ordering of InverseModifier and PowerModifier in the output of _canonicalize_modifiers. The current code emits [InverseModifier(), PowerModifier(|p|)], which computes (A⁻¹)^p. We change it to emit [PowerModifier(|p|), InverseModifier()], which computes (A^p)⁻¹. These are not always equal — they differ when eigenvalues of A lie on the branch cut of the principal matrix logarithm (the negative real axis), as demonstrated by HGate with eigenvalue -1.
The identity (A^p)⁻¹ = A^{-p} holds unconditionally. The proof is straightforward: writing A = V D V⁻¹, the matrix power is A^p = V · diag(λᵢ^p) · V⁻¹, and inverting gives V · diag((λᵢ^p)⁻¹) · V⁻¹ = V · diag(λᵢ^{-p}) · V⁻¹, which is exactly A^{-p} by definition. The critical point is that this step never calls log again — it only takes the scalar reciprocal of the already-computed value λᵢ^p, which is ordinary division with no branch cut involved. By contrast, (A⁻¹)^p requires evaluating exp(p · log(λᵢ⁻¹)), and when λᵢ is real and negative the principal branch assigns the same argument iπ to both λᵢ and λᵢ⁻¹, so negating the exponent and negating the input produce exp(-p·iπ) and exp(p·iπ) respectively — complex conjugates for non-integer p, not equal.
We agree with the broader observation that _canonicalize_modifiers has additional correctness issues beyond what our PR touches — in particular the composition of fractional powers (A^a)^b = A^{ab} does not hold in general under the principal branch, and the comment claiming "all modifiers commute" is incorrect for fractional powers. Those are separate problems that deserve their own discussion and fix.
One approach that would make the semantics unambiguous is to enforce at the API level that each modifier type appears at most once, and in a fixed canonical order: at most one PowerModifier, at most one InverseModifier, at most one ControlModifier, always in the order [PowerModifier, InverseModifier, ControlModifier]. Under this constraint the meaning of a modifier list is always C(( A^|p| )^{-1}) — raise to a positive power, then invert, then control — which is branch-cut safe by the identity above. Any attempt to construct a modifier list that would require composing two fractional powers, or interleaving inverses and fractional powers, would be rejected or left unsimplified rather than silently producing a wrong result. This would also simplify downstream code in AnnotatedSynthesisDefault and OptimizeAnnotated that currently has to handle arbitrary modifier sequences.

</details>

### Comment 4718368662 by @alexanderivrii

Posted: 2026-06-16T11:45:24Z. Updated: 2026-06-16T11:45:24Z.

Source: https://github.com/Qiskit/qiskit/issues/16411#issuecomment-4718368662

<details>
<summary>Full comment by @alexanderivrii</summary>

Thanks for the detailed reply. My point is that since we have identified a problem with canonicalizing modifiers in the presence of fractional powers, we should think of a full solution that handles all cases, rather than half-solutions that do not.

Experimenting with the original issue and your PR #16438, consider the following circuits:
```python

qc = QuantumCircuit(1)
qc.append(AnnotatedOperation(HGate(), [PowerModifier(-0.5)]), [0])
out = PassManager([OptimizeAnnotated()]).run(qc)
print("circuit1: equiv:", Operator(qc).equiv(Operator(out)))


qc = QuantumCircuit(1)
qc.append(AnnotatedOperation(HGate(), [PowerModifier(0.5), InverseModifier()]), [0])
out = PassManager([OptimizeAnnotated()]).run(qc)
print("circui2: equiv:", Operator(qc).equiv(Operator(out)))


qc = QuantumCircuit(1)
qc.append(AnnotatedOperation(HGate(), [InverseModifier(), PowerModifier(0.5)]), [0])
out = PassManager([OptimizeAnnotated()]).run(qc)
print("circuit3: equiv:", Operator(qc).equiv(Operator(out)))
```

The main branch outputs:
```
circuit1: equiv: False
circui2: equiv: False
circuit3: equiv: True
```
and your PR outputs:
```
circuit1: equiv: True
circui2: equiv: True
circuit3: equiv: False
```
so neither are fully correct. At the moment, I do not see an approach that correctly combines all powers and all inverses in all cases, but I would be happy to be proven wrong.

I also don't understand the following comment from your PR summary:
```
Additionally, the guard power != 1 incorrectly fired for power == -1 (pure inverse), which would have appended a spurious PowerModifier(1).
```
Can you give me an example where the current behavior is wrong or produces `PowerModifier(1)`?

</details>

### Comment 4718559567 by @dmeliksetian

Posted: 2026-06-16T12:08:34Z. Updated: 2026-06-16T12:08:34Z.

Source: https://github.com/Qiskit/qiskit/issues/16411#issuecomment-4718559567

<details>
<summary>Full comment by @dmeliksetian</summary>

Thanks for testing all three circuits — that's the right way to evaluate this. You're correct that our PR trades one broken case for another: we fix circuit1 and circuit2 but break circuit3. Closing the PR.

Also correcting a mistake in the PR description: the claim that the original power != 1 guard would produce a spurious PowerModifier(1) for power == -1 is wrong. In the original code, power is already negated before that check, so power == 1 at that point and the guard correctly fires. That was an error in the PR summary, not a real bug in the original code.

The broader point stands: there's no simple reordering fix that handles all three circuits correctly, because _canonicalize_modifiers collapses modifier sequences by multiplying powers together, losing information about the intended evaluation order. A complete solution would need to either preserve that ordering or restrict which sequences are valid to construct — roughly along the lines of your suggestion about leaving certain expressions unsimplified.


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
