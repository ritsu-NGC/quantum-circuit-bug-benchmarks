# Qiskit issue #17057: Two-qubit synthesis to ["cx", "rz", "sx", "x"] returns a wrong circuit (1 - F_avg ≈ 0.07) near the two-CX boundary

## Benchmark metadata

| Field | Value |
| --- | --- |
| Original issue | https://github.com/Qiskit/qiskit/issues/17057 |
| Source repository | `Qiskit/qiskit` |
| Original author | @love-os-architect |
| Reported Qiskit version(s) at the issue | `2.5.2` |
| Verified Qiskit version(s) containing the fix | `2.6.0` |
| Assessment | Confirmed bug |
| Upstream state at snapshot | closed (completed) |
| Created | 2026-09-26T13:00:04Z |
| Last upstream update | 2026-10-15T13:48:26Z |
| Closed | 2026-10-15T13:48:26Z |
| Retrieved | 2026-10-30T17:28:03+00:00 |

**Reported-version context:** Version(s) reported in the original issue environment; not a first-affected boundary.

**Assessment:** Two-qubit CX/ZSX synthesis near the two-CX boundary produces a circuit with approximately 0.07 average infidelity rather than the requested fidelity.

**Resolution:** Merged fix #17163; the stable backport #17226 is verified in 2.6.0.

Reported versions are not an exhaustive affected range. A verified fixed
version is a published release containing the fix, not necessarily the
first fixed version across all maintenance branches. Historical fixed
release versions below 1.0 refer to `qiskit-terra`, not the old `qiskit`
metapackage. Reported versions retain their original distribution context.

## Fix and resolution evidence


### Verified fixed release: 2.6.0

- Distribution: `qiskit`.
- Original fix: https://github.com/Qiskit/qiskit/pull/17163.
- Included fix/backport PR: https://github.com/Qiskit/qiskit/pull/17226.
- Merged: 2026-10-15T14:04:34Z.
- Fix commit: `fda383a901a4c1f0e99e5603ec5be8fa710b0167`.
- Published release: https://github.com/Qiskit/qiskit/releases/tag/2.6.0 (2026-10-16T12:04:54Z).
- Ancestry comparison: https://github.com/Qiskit/qiskit/compare/fda383a901a4c1f0e99e5603ec5be8fa710b0167...2.6.0.
- Verification: Fix merge commit is an ancestor of the published release tag.
- Verified at: 2026-10-30T17:28:03+00:00.

## Original issue post

The body below is reproduced verbatim from the original issue post as
returned by GitHub at retrieval time. It may include upstream edits,
mistakes, HTML, and externally hosted attachments. It is not a
reconstruction of the issue's initial, pre-edit revision.

Source: https://github.com/Qiskit/qiskit/issues/17057 by @love-os-architect.

<details>
<summary>Full original issue text</summary>

### Environment

Qiskit version: 2.5.2 (latest release on PyPI at the time of writing; reproduced in a fresh virtual environment with numpy 2.5.3, scipy 1.18.1, rustworkx 0.18.1)
Python version: 3.12.13
Operating system: Linux (WSL2, glibc 2.43)

### What is happening?

<html>
<body>
<!--StartFragment--><html><head></head><body><h1>Qiskit bug report -- text for each field of the GitHub form</h1>
<p>Open https://github.com/Qiskit/qiskit/issues/new/choose and choose <strong>Bug report</strong>.
Copy each block below into the field with the same name.</p>
<hr>
<h2>Title</h2>
<p>Two-qubit synthesis to <code>["cx", "rz", "sx", "x"]</code> returns a wrong circuit (1 - F_avg ≈ 0.07) near the two-CX boundary</p>
<h2>Environment</h2>
<ul>
<li><strong>Qiskit version</strong>: 2.5.2 (latest release on PyPI at the time of writing; reproduced in a fresh virtual environment with numpy 2.5.3, scipy 1.18.1, rustworkx 0.18.1)</li>
<li><strong>Python version</strong>: 3.12.13</li>
<li><strong>Operating system</strong>: Linux (WSL2, glibc 2.43)</li>
</ul>
<h2>What is happening?</h2>
<p>For the canonical two-qubit gate exp(i(0.6 XX + 0.3 YY + c ZZ)) with c = 3e-8, 1e-7 and 3e-7, <code>TwoQubitBasisDecomposer(CXGate(), euler_basis="ZSX")</code> returns a circuit whose unitary differs from the input with average gate infidelity <strong>6.99e-2</strong>. The circuit has 3 CX gates, so the error is not visible from the gate counts.</p>
<p>The same failure appears in plain <code>transpile()</code> of a <code>UnitaryGate</code> to <code>basis_gates=["cx", "rz", "sx", "x"]</code>, at <strong>every optimization level (0-3)</strong>: 3 CX at levels 0-1 and 2 CX at levels 2-3, with the same infidelity. It also appears when the core is dressed with fixed single-qubit layers on both sides.</p>
<p>Not affected in our tests:</p>
<ul>
<li>the same decomposer with its default Euler basis (<code>TwoQubitBasisDecomposer(CXGate())</code>): exact on the same inputs;</li>
<li>a CZ basis (<code>["cz", "rz", "sx", "x"]</code>), levels 1 and 3;</li>
<li>a two-qubit <code>GenericBackendV2</code> target with error data, levels 1 and 3;</li>
<li>the same gate given as <code>RXX</code>/<code>RYY</code>/<code>RZZ</code> instead of a <code>UnitaryGate</code>.</li>
</ul>
<p>Results are exact at c = 1e-8 (2 CX, within the documented approximation) and from c = 5e-7 upward.</p>
<h2>How can we reproduce the issue?</h2>
<pre><code class="language-python">from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import CXGate, UnitaryGate
from qiskit.quantum_info import Operator, average_gate_fidelity
from qiskit.synthesis import TwoQubitBasisDecomposer

core = QuantumCircuit(2)
core.rxx(-1.2, 0, 1)   # a = 0.6
core.ryy(-0.6, 0, 1)   # b = 0.3
core.rzz(-2e-7, 0, 1)  # c = 1e-7
u = Operator(core)

out = TwoQubitBasisDecomposer(CXGate(), euler_basis="ZSX")(u.data)
print("decomposer ZSX:", 1 - average_gate_fidelity(Operator(out), u))          # ~6.99e-02

out_default = TwoQubitBasisDecomposer(CXGate())(u.data)
print("decomposer default:", 1 - average_gate_fidelity(Operator(out_default), u))  # ~1e-16

qc = QuantumCircuit(2)
qc.append(UnitaryGate(u.data), [0, 1])
for level in range(4):
    t = transpile(qc, basis_gates=["cx", "rz", "sx", "x"], optimization_level=level)
    print("transpile level", level, ":", 1 - average_gate_fidelity(Operator(t), u))  # ~6.99e-02 at every level
</code></pre>
<p>Scan over c (1 - F_avg, number of 2-qubit gates), <code>UnitaryGate</code> input:</p>

c | decomposer ZSX | [cx,rz,sx,x] L0 / L1 | [cx,rz,sx,x] L2 / L3 | [cz,rz,sx,x] L1 / L3
-- | -- | -- | -- | --
1e-8 | 3e-16 (2) | 3e-16 (2) | 3e-16 (2) | 2e-16 (2)
3e-8 | 6.99e-2 (3) | 6.99e-2 (3) | 6.99e-2 (2) | 6e-16 (3)
1e-7 | 6.99e-2 (3) | 6.99e-2 (3) | 6.99e-2 (2) | 3e-16 (3)
3e-7 | 6.99e-2 (3) | 6.99e-2 (3) | 6.99e-2 (2) | 3e-16 (3)
1e-6 | 6e-16 (3) | 6e-16 (3) | 8e-13 (3 / 2) | 3e-16 (3)
1e-5 | 3e-16 (3) | 3e-16 (3) | 3e-16 (3) | 3e-16 (3)


<h2>What should happen?</h2>
<p>The synthesized circuit should match the input to within the decomposer's requested fidelity (1 - 1e-9 by default), as it does with the default Euler basis and with a CZ basis.</p>
<h2>Any suggestions?</h2>
<p>The infidelity is identical (6.987e-2) at every c in the band and with or without single-qubit dressing, which suggests one wrongly taken branch -- perhaps in the ZSX single-qubit synthesis of a local factor near a degenerate angle -- rather than accumulated rounding. This is a guess from the outside; we have not read the source.</p>
<p>For context: we found this while testing a downstream two-qubit synthesizer that delegated its CX-basis step to this decomposer; we now check the decomposer's output and fall back to the default Euler basis when it is off. A larger scan (four families of near-degenerate cores, 272 blocks) found 48 blocks with this 6.99e-2 error and no failures of the default-Euler decomposer.</p></body></html><!--EndFragment-->
</body>
</html>

### How can we reproduce the issue?

What should happen?

The synthesized circuit should match the input to within the decomposer's requested fidelity (1 - 1e-9 by default), as it does with the default Euler basis and with a CZ basis.

### What should happen?

Any suggestions?

The infidelity is identical (6.987e-2) at every c in the band and with or without single-qubit dressing, which suggests one wrongly taken branch -- perhaps in the ZSX single-qubit synthesis of a local factor near a degenerate angle -- rather than accumulated rounding. This is a guess from the outside; we have not read the source.

For context: we found this while testing a downstream two-qubit synthesizer that delegated its CX-basis step to this decomposer; we now check the decomposer's output and fall back to the default Euler basis when it is off. A larger scan (four families of near-degenerate cores, 272 blocks) found 48 blocks with this 6.99e-2 error and no failures of the default-Euler decomposer.

### Any suggestions?

_No response_

</details>

## Issue discussion, including closing and resolving comments

All fetched issue comments are preserved below in upstream chronological
order, including any closing or resolving comments. Comments are
third-party statements, not automatically verified benchmark claims.

### Comment 5846503673 by @love-os-architect

Posted: 2026-09-26T13:05:14Z. Updated: 2026-09-26T13:05:14Z.

Source: https://github.com/Qiskit/qiskit/issues/17057#issuecomment-5846503673

<details>
<summary>Full comment by @love-os-architect</summary>

Disclosure, per the contributing guidelines: I drafted the text of this report with the help of an AI assistant. I ran every reproduction myself (Qiskit 2.5.2, in a fresh virtual environment as well as my working one), and every number in the report comes from those runs. The short script under "How can we reproduce the issue?" is the quickest way to check it. I'm happy to run anything else that would help narrow it down.

</details>

### Comment 5848114481 by @rupasri118

Posted: 2026-09-26T16:59:17Z. Updated: 2026-09-26T16:59:17Z.

Source: https://github.com/Qiskit/qiskit/issues/17057#issuecomment-5848114481

<details>
<summary>Full comment by @rupasri118</summary>

I’d like to work on this issue. I’ll investigate the ZSX decomposition near the 2-CX/3-CX boundary and add a regression test to ensure the synthesized circuit matches the input unitary within the required fidelity.

</details>

### Comment 5914546859 by @jakelishman

Posted: 2026-09-30T15:36:50Z. Updated: 2026-09-30T15:36:50Z.

Source: https://github.com/Qiskit/qiskit/issues/17057#issuecomment-5914546859

<details>
<summary>Full comment by @jakelishman</summary>

Thanks for this report.  This does seem to be a real issue, and a serious error in compilation (though gates close to but not _on_ the 2-cx boundary are probably/hopefully rare; certainly they're rare in things like drawing from the Haar measure).  @ShellyGarion: when you're back from holiday, can you look into this?

It may well be the case that there's a typo in the code made during the translation from Python to Rust, and it's a problem that our test suite didn't catch it.

</details>

### Comment 5932391736 by @love-os-architect

Posted: 2026-10-01T13:25:00Z. Updated: 2026-10-01T13:25:00Z.

Source: https://github.com/Qiskit/qiskit/issues/17057#issuecomment-5932391736

<details>
<summary>Full comment by @love-os-architect</summary>

Following up on the translation-typo hypothesis: I bisected this, and it predates the Rust port.

- **Already present in pure Python:** Qiskit 0.45.3 and 1.0.2 (`_get_sx_vz_3cx_efficient_euler`) give the same 6.987e-2 at c=1e-7. The Rust port (1.1+) only shifted the affected band slightly (c=2e-7 is correct in 1.0.2, wrong from 1.1.2 on).
- **Cause:** near c=0 the ZXZ split of the middle unitary on qubit 0 is degenerate (θ = 2c), so `x12` = 3π + O(1e-17/c). Once that offset exceeds `atol=1e-10`, `x12` fails the π-multiple test and falls into the "non-optimal but doesn't seem to occur" branch, which emits only Rx(`x12`) and drops rz(θ1).
- **Check:** in the reported example θ1 = 0.6, and a missing Rz(0.6) on one qubit gives 1 − F_avg = 0.069866, i.e. exactly the reported 6.987e-2. The error is not always 0.07: it depends on θ1 (worst seen: 0.36).
- **Candidate fix:** in `get_sx_vz_3cx_efficient_euler` (`crates/synthesis/src/two_qubit_decompose/basis_decomposer.rs`), emit `RZ(euler_q0[1][1])` on qubit 0 before the `x12` rotation:

```rust
  if x12_is_non_zero && !x12_is_pi_mult {
      gates.push((StandardGate::RZ.into(), smallvec![euler_q0[1][1]], smallvec![0]));
  }
  // then the existing `if x12_is_half_pi { ... } else if x12_is_non_zero && !x12_is_pi_mult { ... }`
```

  I tested this on a Python port of the 0.45 function, fed with the KAK pieces from 2.5.2's `decomp3_supercontrolled` (not on a rebuilt Rust crate):
  - all c in 1e-9 … 0.1: error ≤ 3.3e-16;
  - 300 Haar-random targets: no regressions;
  - 300 random near-boundary targets: 0 failures, against 122 in 2.5.2.

  The `x12 = π/2` branch was never reached in these tests.
- **Workaround:** `pulse_optimize=False` gives the exact result at every c tested.

   As in the original report: I used an AI assistant for analysis and drafting; all numbers were run and checked locally.

</details>

### Comment 5995310821 by @love-os-architect

Posted: 2026-10-05T13:20:59Z. Updated: 2026-10-05T13:20:59Z.

Source: https://github.com/Qiskit/qiskit/issues/17057#issuecomment-5995310821

<details>
<summary>Full comment by @love-os-architect</summary>

<html>
<body>
<!--StartFragment--><html><head></head><body><h3>Follow-up: the same failure through <code>transpile(..., backend=&lt;cx device&gt;)</code> at optimization levels 1 and 3</h3>
<p>A correction to my original report first: I wrote that a backend with error data did not show the failure. That backend was a <strong>cz</strong> backend (<code>GenericBackendV2</code> with <code>cz, rz, sx, x</code>). With a <strong>cx</strong> device Target the failure does occur, through a plain <code>transpile(qc, backend=..., optimization_level=3)</code>.</p>
<p><strong>Environment:</strong> qiskit 2.5.2 (latest on PyPI), qiskit-ibm-runtime 0.49.0, Python 3.12.13, Linux (WSL2).</p>
<p><strong>Input:</strong> the fixed dressed core of the original reproduction, <code>u(PRE) · exp(i(0.6 XX + 0.3 YY + c ZZ)) · u(POST)</code>, as one <code>UnitaryGate</code> on qubits [0, 1]. The compiled circuit is checked on its active physical qubits with the initial and final layout taken into account (1 − process fidelity, global phase ignored).</p>

c | FakeAuckland L1 | FakeAuckland L3 | FakeHanoiV2 L1 | FakeHanoiV2 L3 | FakeTorino L1 | FakeTorino L3
-- | -- | -- | -- | -- | -- | --
1e-8 | 2.2e-16 (2 CX) | 2.2e-16 (2) | 2.2e-16 (2) | 2.2e-16 (2) | 0 (2 CZ) | 0 (2)
3e-8 | 8.7e-2 (3) | 8.7e-2 (2) | 8.7e-2 (3) | 8.7e-2 (2) | 2.2e-16 (3) | 0 (3)
1e-7 | 8.7e-2 (3) | 8.7e-2 (2) | 8.7e-2 (3) | 8.7e-2 (2) | 0 (3) | 0 (3)
3e-7 | 8.7e-2 (3) | 8.7e-2 (2) | 8.7e-2 (3) | 8.7e-2 (2) | 0 (3) | 0 (3)
1e-6 | 6.7e-16 (3) | 1.0e-12 (2) | 6.7e-16 (3) | 1.0e-12 (2) | 0 (3) | 4.4e-16 (3)
1e-5 | 6.7e-16 (3) | 0 (3) | 6.7e-16 (3) | 6.7e-16 (3) | 0 (3) | 0 (3)


<p><strong>How this fits the analysis above:</strong></p>
<ul>
<li>1 − process fidelity 8.7e-2 is 1 − F_avg = 0.069866, exactly the value of a missing Rz(0.6) on one qubit.</li>
<li>20 random single-qubit dressings of the same core at c = 1e-7 (seeded): 20 of 20 wrong on FakeAuckland and FakeHanoiV2 at both levels, <strong>all at the same value</strong>; FakeTorino 0 of 20. The error is set by the core, not by the dressing, as expected if rz(θ1) of the middle unitary is dropped.</li>
<li>In a larger test with random cores (near-boundary unitaries in 4- and 6-qubit circuits), level 3 with the FakeAuckland, FakeHanoiV2, FakeAlgiers and FakeGeneva Targets returned a wrong circuit for 28 of 40 circuits on each device, with output-state infidelity up to 0.34. That test passed <code>approximation_degree=1.0</code> explicitly. This range is consistent with the θ1-dependence above (worst seen 0.36). The cz devices (FakeTorino, FakeKingston) were exact.</li>
</ul>
<p><strong>Why this matters:</strong> users who compile explicit two-qubit unitaries (for example from numerical optimisation) for cx devices with the default preset pipeline get a silently wrong circuit. At level 3 the wrong circuit is also the shorter one (2 CX instead of 3), so it would be preferred. As far as I can see, the <code>pulse_optimize=False</code> workaround is not reachable through <code>transpile()</code>, so there is no workaround in the default pipeline.</p>
<p>I have not tested the candidate fix on this path.</p>
<p>Reproduction script (Qiskit only):</p>
&lt;details&gt;&lt;summary&gt;repro_qiskit_17057_target.py&lt;/summary&gt;
<pre><code class="language-python">"""repro_qiskit_17057_target.py -- does Qiskit issue #17057 also reach transpile() with a real cx device Target?

repro_qiskit_zsx_2q_v2.py (the reproduction attached to #17057) found wrong circuits from
transpile(basis_gates=[cx, rz, sx, x]) for near-boundary two-qubit unitaries, and none with a cz backend that has
error data. This script asks the open question: what happens with a cx device's Target (FakeAuckland, FakeHanoiV2),
as in `transpile(qc, backend=..., optimization_level=3)`? FakeTorino (cz) is the control.

Input: the same fixed dressed core as repro_qiskit_zsx_2q_v2.py,
    u(PRE) . exp(i(0.6 XX + 0.3 YY + c ZZ)) . u(POST),  c in 1e-8 .. 1e-5,
given as one UnitaryGate on qubits [0, 1]; plus 20 random dressings at c = 1e-7 (seeded).

Check: the compiled circuit's operator on its active physical qubits is restricted to the input subspace (logical
qubits at the initial layout, every other active qubit in |0&gt;) and output subspace (final layout, others in |0&gt;);
reported is 1 - process fidelity against the input unitary (global phase ignored), plus any leakage. Nothing here
uses PSF-Zero.
Usage:
    python -u repro_qiskit_17057_target.py 2&gt;&amp;1 | tee repro_qiskit_17057_target.txt
"""
import itertools
import platform

import numpy as np
import qiskit
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import UnitaryGate
from qiskit.quantum_info import Operator, random_unitary

A, B = 0.6, 0.3
CS = [1e-8, 3e-8, 1e-7, 3e-7, 1e-6, 1e-5]
PRE = [(0.7, 0.2, -1.1), (1.9, -0.4, 0.3)]
POST = [(2.3, 1.0, 0.5), (0.4, -2.2, 1.7)]
WRONG = 1e-6


def dressed(c, pre=None, post=None):
    """The fixed dressed core (or a dressing given as 2x2 unitaries) as a 4x4 matrix, wrapped in a UnitaryGate."""
    core = QuantumCircuit(2)
    core.rxx(-2 * A, 0, 1)
    core.ryy(-2 * B, 0, 1)
    core.rzz(-2 * c, 0, 1)
    qc = QuantumCircuit(2)
    for q in range(2):
        if pre is None:
            qc.u(*PRE[q], q)
        else:
            qc.append(UnitaryGate(pre[q]), [q])
    qc.compose(core, inplace=True)
    for q in range(2):
        if post is None:
            qc.u(*POST[q], q)
        else:
            qc.append(UnitaryGate(post[q]), [q])
    u = Operator(qc).data
    out = QuantumCircuit(2)
    out.append(UnitaryGate(u), [0, 1])
    return out, u


def logical_error(tqc, u):
    """(1 - process fidelity, leakage) of the compiled circuit against the 4x4 unitary u."""
    active = sorted({tqc.find_bit(q).index for ins in tqc.data for q in ins.qubits
                     if ins.operation.name not in ("barrier", "delay", "measure")})
    lay = tqc.layout
    init = list(lay.initial_index_layout(filter_ancillas=True)[:2])
    fin = list(lay.final_index_layout(filter_ancillas=True)[:2])
    active = sorted(set(active) | set(init) | set(fin))
    pos = {p: j for j, p in enumerate(active)}
    red = QuantumCircuit(len(active), global_phase=tqc.global_phase)
    for ins in tqc.data:
        if ins.operation.name in ("barrier", "delay", "measure"):
            continue
        red.append(ins.operation, [pos[tqc.find_bit(q).index] for q in ins.qubits])
    v = Operator(red).data
    m = len(active)

    def index(bits_at):  # little-endian basis index with the given active qubits set
        return sum(1 &lt;&lt; pos[p] for p, b in bits_at if b)

    blk = np.zeros((4, 4), dtype=complex)
    for i, (b0, b1) in enumerate(itertools.product((0, 1), repeat=2)):
        col = index([(init[0], b0), (init[1], b1)])
        for j, (c0, c1) in enumerate(itertools.product((0, 1), repeat=2)):
            row = index([(fin[0], c0), (fin[1], c1)])
            # Qiskit little-endian: logical index = bit(q0) + 2 bit(q1)
            blk[c0 + 2 * c1, b0 + 2 * b1] = v[row, col]
    leak = float(1 - np.linalg.norm(blk, "fro") ** 2 / 4)
    fid = abs(np.trace(u.conj().T @ blk) / 4) ** 2
    return float(1 - fid), leak, m


def main():
    from qiskit_ibm_runtime import fake_provider
    import qiskit_ibm_runtime
    print(f"qiskit {qiskit.__version__} | qiskit-ibm-runtime {qiskit_ibm_runtime.__version__} | "
          f"python {platform.python_version()} | {platform.platform()}")
    backends = [fake_provider.FakeAuckland(), fake_provider.FakeHanoiV2(), fake_provider.FakeTorino()]
    cells = [(b, lvl) for b in backends for lvl in (1, 3)]
    head = " | ".join(f"{b.name[:13]:&gt;13s} L{lvl}" for b, lvl in cells)
    print(f"\n--- fixed dressed core, 1 - process fidelity (cx count) ---\n{'c':&gt;7s} | {head}")
    bad = []
    for c in CS:
        qc, u = dressed(c)
        row = []
        for b, lvl in cells:
            tqc = transpile(qc, backend=b, optimization_level=lvl, seed_transpiler=0)
            err, leak, _ = logical_error(tqc, u)
            n2 = sum(1 for ins in tqc.data if len(ins.qubits) == 2)
            row.append(f"{err:9.1e} ({n2})")
            if err &gt; WRONG or leak &gt; WRONG:
                bad.append((c, b.name, lvl, err))
        print(f"{c:7.0e} | " + " | ".join(f"{x:&gt;16s}" for x in row))

    print("\n--- 20 random dressings at c = 1e-7: circuits with 1 - F &gt; 1e-6 (max) ---")
    rng = np.random.default_rng(17057)
    seeds = [[int(s) for s in rng.integers(2**31, size=4)] for _ in range(20)]
    for b, lvl in cells:
        errs = []
        for s in seeds:
            qc, u = dressed(1e-7, pre=[random_unitary(2, seed=s[0]).data, random_unitary(2, seed=s[1]).data],
                            post=[random_unitary(2, seed=s[2]).data, random_unitary(2, seed=s[3]).data])
            tqc = transpile(qc, backend=b, optimization_level=lvl, seed_transpiler=0)
            errs.append(logical_error(tqc, u)[0])
        print(f"  {b.name:14s} L{lvl}: {sum(e &gt; WRONG for e in errs):2d} of 20 wrong (max {max(errs):.1e})")

    print("\nwrong (fixed core):", bad if bad else "none")


if __name__ == "__main__":
    main()
</code></pre>
&lt;/details&gt;
<p>As before: I used an AI assistant for analysis and drafting; all numbers were run and checked locally.</p></body></html><!--EndFragment-->
</body>
</html>

</details>

### Comment 5995397305 by @jakelishman

Posted: 2026-10-05T13:25:53Z. Updated: 2026-10-05T13:25:53Z.

Source: https://github.com/Qiskit/qiskit/issues/17057#issuecomment-5995397305

<details>
<summary>Full comment by @jakelishman</summary>

Please stop the LLM spam now.  The original issue was useful.  Sending thousands of further words of unfiltered LLM output is not.



</details>

### Comment 6193642411 by @ShellyGarion

Posted: 2026-10-15T13:48:26Z. Updated: 2026-10-15T13:48:26Z.

Source: https://github.com/Qiskit/qiskit/issues/17057#issuecomment-6193642411

<details>
<summary>Full comment by @ShellyGarion</summary>

closed by #17163 

</details>


## Closure and reopening events

- 2026-10-15T13:48:26Z: closed by @ShellyGarion.

Closing an issue does not establish that a code fix was merged or released.

## Attribution and reuse

The original post and comments remain attributed to their upstream authors.
Their inclusion does not relicense them under this project's MIT license.
See [NOTICE](../../NOTICE). Machine-readable text and provenance are in
[source.json](source.json); curated version evidence is in
[the manifest](../manifest.json). Attachments are linked, not vendored.
