# Qiskit issue #12948: Transpile Optimization Level 2 and 3 Give Incorrect Circuits

## Benchmark metadata

| Field | Value |
| --- | --- |
| Original issue | https://github.com/Qiskit/qiskit/issues/12948 |
| Source repository | `Qiskit/qiskit` |
| Original author | @alvinquantum |
| Reported Qiskit version(s) at the issue | `1.1.1` |
| Verified Qiskit version(s) containing the fix | `1.2.0` |
| Assessment | Confirmed bug |
| Upstream state at snapshot | closed (completed) |
| Created | 2024-08-12T21:04:58Z |
| Last upstream update | 2025-07-18T12:24:17Z |
| Closed | 2025-07-18T12:24:17Z |
| Retrieved | 2026-10-30T17:28:03+00:00 |

**Reported-version context:** Version(s) reported in the original issue environment; not a first-affected boundary.

**Assessment:** Transpiled state preparation at optimization levels 2/3 gives approximately 0.387 fidelity instead of 1.

**Resolution:** Maintainer and reporter confirm the new StatePreparation synthesis from #12178 fixes this in 1.2.0rc1. Stable 1.2.0 is ancestry-verified. Closure in 2025 is not used as the fix date.

Reported versions are not an exhaustive affected range. A verified fixed
version is a published release containing the fix, not necessarily the
first fixed version across all maintenance branches. Historical fixed
release versions below 1.0 refer to `qiskit-terra`, not the old `qiskit`
metapackage. Reported versions retain their original distribution context.

## Fix and resolution evidence

- https://github.com/Qiskit/qiskit/issues/12948#issuecomment-2286215359
- https://github.com/Qiskit/qiskit/issues/12948#issuecomment-2286806289

### Verified fixed release: 1.2.0

- Distribution: `qiskit`.
- Original fix: https://github.com/Qiskit/qiskit/pull/12178.
- Included fix/backport PR: https://github.com/Qiskit/qiskit/pull/12178.
- Merged: 2024-05-08T09:47:23Z.
- Fix commit: `8b94fc36df05a9f5b2150e7a8ac1c36dca3286d1`.
- Published release: https://github.com/Qiskit/qiskit/releases/tag/1.2.0 (2024-08-15T20:41:15Z).
- Ancestry comparison: https://github.com/Qiskit/qiskit/compare/8b94fc36df05a9f5b2150e7a8ac1c36dca3286d1...1.2.0.
- Verification: Fix merge commit is an ancestor of the published release tag.
- Verified at: 2026-10-30T17:28:03+00:00.

## Original issue post

The body below is reproduced verbatim from the original issue post as
returned by GitHub at retrieval time. It may include upstream edits,
mistakes, HTML, and externally hosted attachments. It is not a
reconstruction of the issue's initial, pre-edit revision.

Source: https://github.com/Qiskit/qiskit/issues/12948 by @alvinquantum.

<details>
<summary>Full original issue text</summary>

### Environment

- **Qiskit 1.1.1**: 
- **Python 3.12.4**: 
- **Windows 10**: 


### What is happening?

I think Transpile with optimization level 2 and level 3 is bugged; transpile with optimization level 0 or 1 is correct. In the given example, I create a circuit that prepares the target state. The generated circuits' output has unit fidelity with the target state when transpiled with optimization 0 and 1 but 0.387 fidelity with 2 and 3.

### How can we reproduce the issue?

```
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
import numpy as np
from qiskit_aer import AerSimulator

def get_fidelity(state1, state2):
    return abs(state1.conjugate().T @ state2) ** 2

def execute(circ, opt_level):
    sim = AerSimulator()
    basis_gates = ["rx", "ry", "rz", "h", "cx"]
    circuit_tanspile = transpile(circ, basis_gates=basis_gates, optimization_level=opt_level)
    circuit_tanspile.save_statevector(label="end")
    result = sim.run(circuit_tanspile).result()
    return result.data(0)["end"].data

if __name__ == "__main__":
    target=np.array([0j, (0.485587205735524-0.2600812815664197j), 
          0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 
          0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 
          0j, 0j, 0j, (-0.11865767727626089-0.28041030727622457j), 
          0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 
          (0.24996770614905434+0.1064494710662403j), 0j, 0j, 0j, 0j,
            0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, (0.0015310580114530382-0.34901642700045116j), 
            0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j,
              0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, (-0.023640084620894435-0.5198551844366773j),
                0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 
                0j, 0j, 0j, 0j, 0j, 0j, (-0.021650924801843517-0.3085455190622454j), 0j, 0j,
                  0j, 0j, 0j, 0j, (0.20089824207135182-0.03722342551126882j), 
                  0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j, 0j])
    
    print(target.conjugate().T@ target) # Unit vector

    circuit = QuantumCircuit(7)
    circuit.prepare_state(Statevector(target))

    # 0 optimization level
    state0 = execute(circuit, 0)
    print(f"optimization 0: {get_fidelity(state0, target)}") #outputs 1

    # 1 optimization level
    state1 = execute(circuit, 1)
    print(f"optimization 1: {get_fidelity(state1, target)}") #outputs 1

    # 2 optimization level
    state2 = execute(circuit, 2)
    print(f"optimization 2: {get_fidelity(state2, target)}") #outputs 0.38665764499036803

    # 3 optimization level
    state3 = execute(circuit, 3)
    print(f"optimization 3: {get_fidelity(state3, target)}") #outputs 0.38665764499036803
```

### What should happen?

All the fidelities should be 1.

### Any suggestions?

_No response_

</details>

## Issue discussion, including closing and resolving comments

All fetched issue comments are preserved below in upstream chronological
order, including any closing or resolving comments. Comments are
third-party statements, not automatically verified benchmark claims.

### Comment 2285006726 by @mtreinish

Posted: 2024-08-12T22:27:05Z. Updated: 2024-08-12T22:27:05Z.

Source: https://github.com/Qiskit/qiskit/issues/12948#issuecomment-2285006726

<details>
<summary>Full comment by @mtreinish</summary>

I took a quick look at this and I think what is happening is at levels 2 and 3 we're running running the passes to unroll 3q or more gates in the lead up to doing logical optimizations. As part of this the `Isometry` object (which is used internally for `StatePreparation`) is decomposed by `HighLevelSynthesis` into several intermediate gate objects defined solely for the isometry module. I added the callback to each pass to print the number of ops after each pass runs. The state of the op count in the at this point is:

`{'multiplex1_reverse_dg': 1, 'multiplex1_dg': 1, 'multiplex2_reverse_dg': 21, 'multiplex2_dg': 6, 'multiplex2_reverse_reverse_reverse_dg': 35, 'cx': 114, 'multiplex2_reverse_reverse_dg': 35, 'multiplex2_reverse_reverse_reverse_reverse_dg': 21, 'multiplex2_reverse_reverse_reverse_reverse_reverse_dg': 7, 'multiplex2_reverse_reverse_reverse_reverse_reverse_reverse_dg': 1}`

as these are all 2q objects high level synthesis stops at this point so follow-on passes can potentially work with them. Although this is mostly for layout/routing which isn't run because you don't have a connectivity constraint set. Then a second decomposition is run on this during the translation stage to lower these to the target gates outlined in `basis_gates`. This decomposition ends up being different than what level 1 ends up with because the unroll 3q or more step is skipped and high level synthesis does the full decomposition in a single step. The gate counts end up being from the 2 different approaches:

Level 2: `{'cx': 212, 'ry': 127, 'rz': 127}`
Level 1: `{'rz': 127, 'ry': 127, 'cx': 240}`

Looking closely at the output for level2 (and it'll be the same for 3 since the init stages are identical) we go from 114 cx gates after `HighLevelSynthesis` to 86 cx gates after `CommutativeCancellation` runs. I think this points to an issue in the `Isometry` class's partial decomposition output. Either those intermediate gate matrices are setup such that the commutation analysis thinks things commute erroneously or there is some other structural issue causing cnots to be cancelled when it's not otherwise valid. I didn't have a chance to dive into what commutation analysis and commutative cancellation think is going on though, so this is just a guess based on looking at the gate counts and the circuit visualization after `CommutativeCancellation` executes.

That being said I think the simplest fix though would be to update the isometry class to not have so many layers of nesting in it's definition. I expect if we fully decompose the isometry object to all standard gates `CommutativeCancellation` wouldn't incorrectly cancel gates as it's not dependent on these one off objects to be fully correct anymore and is running on a better tested code path. But this is still kind of a guess at this point.

</details>

### Comment 2286215359 by @alexanderivrii

Posted: 2024-08-13T13:05:43Z. Updated: 2024-08-13T13:05:43Z.

Source: https://github.com/Qiskit/qiskit/issues/12948#issuecomment-2286215359

<details>
<summary>Full comment by @alexanderivrii</summary>

FWIW, the problem is not present in 1.2.0rc1, thanks to #12178, which changed the default synthesis function for `StatePreparation`. With this version the fidelity is `1` for all optimization levels. Furthermore, from what I can see, that PR completely remove the old (and as we now know buggy) code. So the simplest solution would be upgrading to the latest Qiskit version.  

</details>

### Comment 2286806289 by @alvinquantum

Posted: 2024-08-13T17:53:18Z. Updated: 2024-08-13T17:53:53Z.

Source: https://github.com/Qiskit/qiskit/issues/12948#issuecomment-2286806289

<details>
<summary>Full comment by @alvinquantum</summary>

Thanks @alexanderivrii. For my situation at least, it seems that 1.2.0rc1 resolves the transpile issues.

</details>

### Comment 3089317035 by @jakelishman

Posted: 2025-07-18T12:24:17Z. Updated: 2025-07-18T12:24:17Z.

Source: https://github.com/Qiskit/qiskit/issues/12948#issuecomment-3089317035

<details>
<summary>Full comment by @jakelishman</summary>

This appears to have been fixed in Qiskit 1.2 - I'll close this as "complete" for now.

</details>


## Closure and reopening events

- 2025-07-18T12:24:17Z: closed by @jakelishman.

Closing an issue does not establish that a code fix was merged or released.

## Attribution and reuse

The original post and comments remain attributed to their upstream authors.
Their inclusion does not relicense them under this project's MIT license.
See [NOTICE](../../NOTICE). Machine-readable text and provenance are in
[source.json](source.json); curated version evidence is in
[the manifest](../manifest.json). Attachments are linked, not vendored.
