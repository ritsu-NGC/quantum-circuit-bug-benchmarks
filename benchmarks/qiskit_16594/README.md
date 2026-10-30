# Qiskit issue #16594: CommutativeCancellation cancels an sxdg·sxdg pair that equals X, giving wrong results at optimization_level ≥ 2

## Benchmark metadata

| Field | Value |
| --- | --- |
| Original issue | https://github.com/Qiskit/qiskit/issues/16594 |
| Source repository | `Qiskit/qiskit` |
| Original author | @cleitonaugusto |
| Reported Qiskit version(s) at the issue | `2.5.0` |
| Verified Qiskit version(s) containing the fix | `2.5.1` |
| Assessment | Confirmed bug |
| Upstream state at snapshot | closed (completed) |
| Created | 2026-07-16T18:50:51Z |
| Last upstream update | 2026-07-20T09:56:41Z |
| Closed | 2026-07-20T09:56:41Z |
| Retrieved | 2026-10-30T17:28:03+00:00 |

**Reported-version context:** Version(s) reported in the original issue environment; not a first-affected boundary.

**Assessment:** CommutativeCancellation drops negative X-rotation sums. Two SXdg gates must produce X or remain in the circuit, not disappear.

**Resolution:** Merged fix #16599 and its backport are verified in 2.5.1.

Reported versions are not an exhaustive affected range. A verified fixed
version is a published release containing the fix, not necessarily the
first fixed version across all maintenance branches. Historical fixed
release versions below 1.0 refer to `qiskit-terra`, not the old `qiskit`
metapackage. Reported versions retain their original distribution context.

## Fix and resolution evidence


### Verified fixed release: 2.5.1

- Distribution: `qiskit`.
- Original fix: https://github.com/Qiskit/qiskit/pull/16599.
- Included fix/backport PR: https://github.com/Qiskit/qiskit/pull/16615.
- Merged: 2026-07-20T11:08:21Z.
- Fix commit: `7b6cb24ccf297fc6c97b6e109e6d474def3404e6`.
- Published release: https://github.com/Qiskit/qiskit/releases/tag/2.5.1 (2026-07-23T17:09:41Z).
- Ancestry comparison: https://github.com/Qiskit/qiskit/compare/7b6cb24ccf297fc6c97b6e109e6d474def3404e6...2.5.1.
- Verification: Fix merge commit is an ancestor of the published release tag.
- Verified at: 2026-10-30T17:28:03+00:00.

## Original issue post

The body below is reproduced verbatim from the original issue post as
returned by GitHub at retrieval time. It may include upstream edits,
mistakes, HTML, and externally hosted attachments. It is not a
reconstruction of the issue's initial, pre-edit revision.

Source: https://github.com/Qiskit/qiskit/issues/16594 by @cleitonaugusto.

<details>
<summary>Full original issue text</summary>

### Environment

- **Qiskit version**: 2.5.0
- **Python version**: 3.10
- **Operating system**: Ubuntu

### What is happening

I was cross-checking a few simulators against each other and one circuit kept coming out different after transpiling. I traced it to `CommutativeCancellation`. It cancels two `sxdg` gates on the same qubit when there's a gate on another qubit between them, but `sxdg·sxdg` isn't identity, it's `X`. So the transpiled circuit computes something different from the input.

It happens at `optimization_level` 2 and 3 (where the pass runs). O0 and O1 are fine.

### How can we reproduce the issue

With just the pass:

```python
from qiskit import QuantumCircuit
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import CommutativeCancellation
from qiskit.quantum_info import Operator

qc = QuantumCircuit(2)
qc.sxdg(1)
qc.sx(0)
qc.sxdg(1)

out = PassManager([CommutativeCancellation()]).run(qc)
print(out)                                # only sx(0) is left
print(Operator(qc).equiv(Operator(out)))  # False
```

And through the full transpiler, so you can see the measurement result change:

```python
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

qc = QuantumCircuit(2, 2)
qc.sxdg(1); qc.sx(0); qc.sxdg(1)
qc.measure([0, 1], [0, 1])

sim = AerSimulator()
for opt in (1, 3):
    t = transpile(qc, basis_gates=["rz", "sx", "x", "cx"], optimization_level=opt)
    print(opt, sim.run(t, shots=2000).result().get_counts())
# O1: qubit 1 is always 1  (correct, since sxdg·sxdg = X)
# O3: qubit 1 is always 0  (wrong)
```

### What should happen

The pair should fold to `X` (or be left alone), not vanish.

Looks like the cause is in the pass itself: `_x_rotations` includes `sx` and `sxdg` (line 69 of `commutative_cancellation.py`) and two `sxdg` get treated as an inverse pair. They aren't — two `sxdg` make `Rx(-π)`, which is `X` up to a global phase, not identity. The adjacent case (two `sxdg` with nothing in between) is folded correctly; the problem only shows up when a gate on another qubit sits between them.

I found this with a differential fuzzer I've been building ([cforge-fuzz](https://github.com/cleitonaugusto/CleitonForge)). Happy to share more minimal cases if that helps.


</details>

## Issue discussion, including closing and resolving comments

All fetched issue comments are preserved below in upstream chronological
order, including any closing or resolving comments. Comments are
third-party statements, not automatically verified benchmark claims.

### Comment 4995867326 by @jakelishman

Posted: 2026-07-16T19:37:12Z. Updated: 2026-07-16T19:37:12Z.

Source: https://github.com/Qiskit/qiskit/issues/16594#issuecomment-4995867326

<details>
<summary>Full comment by @jakelishman</summary>

Thanks for the report, we can get this fixed.  The actual root cause is quite different (all this code is in Rust), and commutative cancellation _is_ calculating the necessary rotation angle correctly, it just fails to correctly synthesise that into gates when the combined X rotation is a negative odd multiple of $\pi/2$ and `sx` appears to be a supported gate.

</details>

### Comment 4997966557 by @cleitonaugusto

Posted: 2026-07-17T01:01:41Z. Updated: 2026-07-17T01:02:59Z.

Source: https://github.com/Qiskit/qiskit/issues/16594#issuecomment-4997966557

<details>
<summary>Full comment by @cleitonaugusto</summary>

Thanks for the quick triage, and for correcting me on the cause. I was reading the Python and guessed wrong.

I looked at it a bit more. Two things that might matter for the fix.

It's not only the odd multiples. Forcing an exact combined rotation with a pair of `rx(θ/2)` gates:

```python
import numpy as np
from qiskit import QuantumCircuit
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import CommutativeCancellation
from qiskit.quantum_info import Operator

for k in range(-8, 9):
    if k == 0:
        continue
    theta = k * np.pi / 2
    qc = QuantumCircuit(2)
    qc.rx(theta / 2, 1)
    qc.sx(0)
    qc.rx(theta / 2, 1)
    out = PassManager([CommutativeCancellation()]).run(qc)
    emitted = [i.operation.name for i in out.data if out.find_bit(i.qubits[0]).index == 1]
    equiv = Operator(qc).equiv(Operator(out))
    print(f"{k:+3d} * pi/2   emitted: {' '.join(emitted) or '(nothing)':<12} equiv: {equiv}")
```

On 2.5.0:

```
 -8 * pi/2   emitted: (nothing)    equiv: True
 -7 * pi/2   emitted: (nothing)    equiv: False
 -6 * pi/2   emitted: (nothing)    equiv: False
 -5 * pi/2   emitted: (nothing)    equiv: False
 -4 * pi/2   emitted: (nothing)    equiv: True
 -3 * pi/2   emitted: (nothing)    equiv: False
 -2 * pi/2   emitted: (nothing)    equiv: False
 -1 * pi/2   emitted: (nothing)    equiv: False
 +1 * pi/2   emitted: sx           equiv: True
 +2 * pi/2   emitted: sx sx        equiv: True
 +3 * pi/2   emitted: sx sx sx     equiv: True
 +4 * pi/2   emitted: (nothing)    equiv: True
 +5 * pi/2   emitted: sx           equiv: True
 +6 * pi/2   emitted: sx sx        equiv: True
 +7 * pi/2   emitted: sx sx sx     equiv: True
 +8 * pi/2   emitted: (nothing)    equiv: True
```

So -π and -3π break too (k = -2 and -6), not just the odd ones. -2π and -4π only pass because emitting nothing is correct there anyway. The condition looks more like "negative multiple of π/2 that is not a multiple of 2π". A fix that only covers the odd cases would leave those two broken.

It's also not specific to `sxdg`. There is no `sx` or `sxdg` on that qubit above, only `rx`. So the 3-gate case I posted originally is one instance of something wider.

One more thing, but this is a guess. The positive side reduces correctly, +5·π/2 comes back as a single `sx`. The negative side emits nothing at every angle. That would fit a signed remainder feeding a range that ends up empty when it's negative. I can't see the Rust from here, and I already got the cause wrong once, so I'm not going to claim it.

The same script on 2.4.0 is clean at all 16 angles. It emits `rx` and never takes the `sx` path. Maybe useful for bounding the regression.


</details>

### Comment 4999294016 by @cleitonaugusto

Posted: 2026-07-17T05:28:15Z. Updated: 2026-07-17T05:28:15Z.

Source: https://github.com/Qiskit/qiskit/issues/16594#issuecomment-4999294016

<details>
<summary>Full comment by @cleitonaugusto</summary>

One correction to my original report, sorry. I said the problem only shows up when there is a gate on another qubit sitting between the two sxdg. That is wrong. It happens on a single qubit with nothing else in the circuit at all:

```python
from qiskit import QuantumCircuit
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import CommutativeCancellation
from qiskit.quantum_info import Operator

qc = QuantumCircuit(1)
qc.sxdg(0)
qc.sxdg(0)
qc.sx(0)

out = PassManager([CommutativeCancellation()]).run(qc)
print(out.count_ops())                     # OrderedDict()  everything is gone
print(Operator(qc).equiv(Operator(out)))   # False
```

That combines to -pi/2, so one `sxdg` should be left.

I went through every sx/sxdg sequence up to length 5 on one qubit. 22 of the 62 break, none at length 1 or 2, then 3 of 8 at length 3, 4 of 16 at length 4, and 15 of 32 at length 5.

The ones that break all mix `sx` and `sxdg` and add up to something negative. A run of just one kind comes out fine, so `sxdg sxdg sxdg` is correct at -3pi/2, but `sx sxdg sxdg sxdg sxdg` drops everything at the same -3pi/2. Two gates are always fine too, `sxdg sxdg` comes back as `rx` and is correct.

I'm mentioning it because my description would point a fix at the interleaved case, and the single qubit one would still be there afterwards.


</details>

### Comment 4999799585 by @jakelishman

Posted: 2026-07-17T06:43:06Z. Updated: 2026-07-17T06:43:06Z.

Source: https://github.com/Qiskit/qiskit/issues/16594#issuecomment-4999799585

<details>
<summary>Full comment by @jakelishman</summary>

Yeah, I was just simplifying to target your particular example rather than dumping out every reason - there's quite a bit of faulty logic all around the X resynthesis, and some of it is compounded by the strange logic surrounding how the pass calculates the "supported instructions" if you don't explicitly specify them.

</details>

### Comment 5004848704 by @cleitonaugusto

Posted: 2026-07-17T15:31:36Z. Updated: 2026-07-17T15:31:36Z.

Source: https://github.com/Qiskit/qiskit/issues/16594#issuecomment-5004848704

<details>
<summary>Full comment by @cleitonaugusto</summary>

I think I found the line. In `crates/transpiler/src/passes/commutation_cancellation.rs`, the sx synthesis branch:

```rust
let num_sx = (total_angle / FRAC_PI_2).round();
total_phase -= FRAC_PI_4 * num_sx;
for _ in 0..(num_sx as i64) % 4 {
    dag.insert_1q_on_incoming_qubit((StandardGate::SX, &[]), cancel_set[0]);
}
```

For a negative rotation `num_sx` is negative, and `%` keeps the sign of the dividend, so `-1 % 4` is `-1`, not `3`. That makes the loop `0..-1`, which is an empty range in Rust, so no `sx` is emitted and the rotation is dropped.

`num_sx.rem_euclid(4)` gives `0..3` for either sign. It is exact here because `SX` to the 4th is the identity, so reducing the count mod 4 does not change the operator, and the phase correction on the line above already uses the true `num_sx`, so it stays right.

That also matches why only the mixed case broke. `sx_supported` is true when the circuit contains an `sx`, so a pure `sxdg` run has no `sx`, takes the `rx` path instead, and was always fine.


</details>

### Comment 5005927516 by @jakelishman

Posted: 2026-07-17T17:46:36Z. Updated: 2026-07-17T17:46:36Z.

Source: https://github.com/Qiskit/qiskit/issues/16594#issuecomment-5005927516

<details>
<summary>Full comment by @jakelishman</summary>

Yes - there's a PR (two, actually) linked above your comment that changes that line.  There's actually larger inefficiencies in that pass, and the resynthesis logic is quite suboptimal, but that line is the backportable change, and we have a new commutation analysis in a completely separate pass that will (hopefully) supersede this whole logic in the future.

</details>


## Closure and reopening events

- 2026-07-20T09:56:41Z: closed by @alexanderivrii.

Closing an issue does not establish that a code fix was merged or released.

## Attribution and reuse

The original post and comments remain attributed to their upstream authors.
Their inclusion does not relicense them under this project's MIT license.
See [NOTICE](../../NOTICE). Machine-readable text and provenance are in
[source.json](source.json); curated version evidence is in
[the manifest](../manifest.json). Attachments are linked, not vendored.
