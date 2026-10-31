# Qiskit issue #5453: Control of the diagonal gate not working properly

## Benchmark metadata

| Field | Value |
| --- | --- |
| Original issue | https://github.com/Qiskit/qiskit/issues/5453 |
| Source repository | `Qiskit/qiskit` |
| Original author | @ljubabu |
| Reported Qiskit version(s) at the issue | `0.16.1` |
| Verified Qiskit version(s) containing the fix | `0.17.0` |
| Assessment | Confirmed bug |
| Upstream state at snapshot | closed (completed) |
| Created | 2020-12-01T12:11:04Z |
| Last upstream update | 2021-01-19T17:10:31Z |
| Closed | 2021-01-19T17:10:31Z |
| Retrieved | 2026-10-30T17:28:03+00:00 |

**Reported-version context:** Version(s) reported in the original issue environment; not a first-affected boundary.

**Assessment:** Diagonal synthesis loses a global phase that becomes relative when controlled, producing a different statevector than equivalent circuits.

**Resolution:** Merged fix #5474 is verified in qiskit-terra 0.17.0. An earlier maintenance-branch fix is not asserted.

Reported versions are not an exhaustive affected range. A verified fixed
version is a published release containing the fix, not necessarily the
first fixed version across all maintenance branches. Historical fixed
release versions below 1.0 refer to `qiskit-terra`, not the old `qiskit`
metapackage. Reported versions retain their original distribution context.

## Fix and resolution evidence


### Verified fixed release: 0.17.0

- Distribution: `qiskit-terra`.
- Original fix: https://github.com/Qiskit/qiskit/pull/5474.
- Included fix/backport PR: https://github.com/Qiskit/qiskit/pull/5474.
- Merged: 2021-01-19T17:10:31Z.
- Fix commit: `e98d4567c07a1827f0e6b78fa1caf0e668c486df`.
- Published release: https://github.com/Qiskit/qiskit/releases/tag/0.17.0 (2021-04-01T15:39:11Z).
- Ancestry comparison: https://github.com/Qiskit/qiskit/compare/e98d4567c07a1827f0e6b78fa1caf0e668c486df...0.17.0.
- Verification: Fix merge commit is an ancestor of the published release tag.
- Verified at: 2026-10-30T17:28:03+00:00.

## Original issue post

The body below is reproduced verbatim from the original issue post as
returned by GitHub at retrieval time. It may include upstream edits,
mistakes, HTML, and externally hosted attachments. It is not a
reconstruction of the issue's initial, pre-edit revision.

Source: https://github.com/Qiskit/qiskit/issues/5453 by @ljubabu.

<details>
<summary>Full original issue text</summary>

<!-- ⚠️ If you do not respect this template, your issue will be closed -->
<!-- ⚠️ Make sure to browse the opened and closed issues -->

### Information

- **Qiskit Terra 0.16.1**:
- **Python version 3.7.3**:
- **Win 10**:

### What is the current behavior?
Converting the attached diagonal gate to a circuit and then applying the control method does not produce expected result. 


### Steps to reproduce the problem
The code example is given in form of 3 separate version of the same problem. First two, i.e. VER-I ands VER-II, are giving the same correct results, while in case of VER-III, where controlled diagonal gate is used, output is incorrect.  

```
REG_I = QuantumRegister(2)
REG_II = QuantumRegister(1)
CIRC = QuantumCircuit(REG_I,REG_II)
CIRC_1A=QuantumCircuit(REG_I)
CIRC_1B=QuantumCircuit(REG_I)
PARAM1A=[1,1,1,1]
PARAM1B=[1,1,1,1]
PARAM=[1,1,1,1,1,1,1,1]

## VER - I ##
CIRC.h([0,1,2])
CIRC.u1(3.14/2,REG_I)
CIRC.h(2)
```
```
## VER - II ##
CIRC.h([0,1,2])

CIRC.u1(3.14/2,REG_I)
CIRC.diagonal(PARAM,[0,1,2])

CIRC.h(2)
```
```
## VER - III ##
CIRC.h([0,1,2])
CIRC.u1(3.14/2,REG_I)

CIRC_1A.diagonal(PARAM1A,[0,1])
GATEC1A  =CIRC_1A.to_gate(label='A1')
CGATEC1A=GATEC1A.control(1,ctrl_state='0') 
CIRC.append(CGATEC1A,[2,0,1])
CIRC_1B.diagonal(PARAM1B,[0,1])
GATEC1B  =CIRC_1B.to_gate(label='B1')
CGATEC1B=GATEC1B.control(1,ctrl_state='1') 
CIRC.append(CGATEC1B,[2,0,1])

CIRC.h(2)
```

### What is the expected behavior?

For the VER-I and VER-II correct statevector is obtained,

```
[ 5.00000000e-01-3.06161700e-17j  3.98163355e-04+4.99999841e-01j
  3.98163355e-04+4.99999841e-01j -4.99999366e-01+7.96326458e-04j
  0.00000000e+00+0.00000000e+00j  0.00000000e+00+0.00000000e+00j
  0.00000000e+00+0.00000000e+00j  0.00000000e+00+0.00000000e+00j]
```
while in case of the VER-III wrong results are being produced, i.e.

```
[ 0.35369413-0.35341259j  0.35369413+0.35341259j  0.35369413+0.35341259j
 -0.35313082+0.35397545j  0.        +0.j          0.        +0.j
  0.        +0.j          0.        +0.j        ]
```

### Suggested solutions




</details>

## Issue discussion, including closing and resolving comments

All fetched issue comments are preserved below in upstream chronological
order, including any closing or resolving comments. Comments are
third-party statements, not automatically verified benchmark claims.

### Comment 737163877 by @Cryoris

Posted: 2020-12-02T11:13:21Z. Updated: 2020-12-02T11:13:21Z.

Source: https://github.com/Qiskit/qiskit/issues/5453#issuecomment-737163877

<details>
<summary>Full comment by @Cryoris</summary>

How are `CIRC_1A` and `CIRC_1B` initialized? Are they empty circuits? Could you maybe post a smaller minimal-working example, then it would be a little easier to understand where exactly things are going wrong 🙂 

</details>

### Comment 737862887 by @ljubabu

Posted: 2020-12-03T10:48:44Z. Updated: 2020-12-03T10:51:11Z.

Source: https://github.com/Qiskit/qiskit/issues/5453#issuecomment-737862887

<details>
<summary>Full comment by @ljubabu</summary>

@Cryoris  Thanks for the help. I simplified the test code in which only identity as diagonal gate is applied. Even for this simple case controlled method of the diagonal gate produces wrong results. 

</details>

### Comment 739599584 by @georgios-ts

Posted: 2020-12-07T00:42:59Z. Updated: 2020-12-07T00:42:59Z.

Source: https://github.com/Qiskit/qiskit/issues/5453#issuecomment-739599584

<details>
<summary>Full comment by @georgios-ts</summary>

@ljubabu If you look carefully, the two statevectors are equivalent up to a global phase `pi / 4`.  So there must be a global phase that is not tracked somewhere in the transpilation process. My guess is that if you execute your circuit with `optimization_level=0` or `basis_gates=['u', 'cx']` the vectors will be the same.

</details>

### Comment 744554698 by @ljubabu

Posted: 2020-12-14T16:27:43Z. Updated: 2020-12-14T16:27:43Z.

Source: https://github.com/Qiskit/qiskit/issues/5453#issuecomment-744554698

<details>
<summary>Full comment by @ljubabu</summary>

@Cryoris Sorry for late response. Thanks for the help. You are right regarding the global phase and for the introducing the optimization level in execution method remark. However, when I change the diagonal parameters to slightly complicated form
 ```
PARAM1A=[1,1,1j,1j]
PARAM1B=[1,1,-1j,-1j]
PARAM=[1,1,1j,1j,1,1,-1j,-1j]
 ```
in order to check whether proposed method is working, again wrong results are obtained. For the VER I and II correct statevector is obtained,
 ```
[ 5.00000000e-01-3.06161700e-17j  3.98163355e-04+4.99999841e-01j
 -6.72718651e-18-3.06260542e-17j  3.05934778e-17-8.19713403e-18j
 -1.79202035e-17+3.06161700e-17j -3.06293809e-17+6.70280603e-18j
 -4.99999841e-01+3.98163355e-04j -7.96326458e-04-4.99999366e-01j]
```

while in case of the VER-III wrong results are being produced, i.e.

 ```
[ 3.53553391e-01-1.62588398e-17j  2.81544009e-04+3.53553278e-01j
  2.81544009e-04+3.53553278e-01j -3.53552942e-01+5.63087839e-04j
 -3.31456373e-17-3.53553391e-01j  3.53553278e-01-2.81544009e-04j
 -3.53553278e-01+2.81544009e-04j -5.63087839e-04-3.53552942e-01j]
 ```
In both cases following statement for the execute is used:
 `
CIRC_job1 = execute(CIRC, backend1,optimization_level=0).result().get_statevector(CIRC)
`
Thank you.


</details>

### Comment 744594511 by @georgios-ts

Posted: 2020-12-14T17:32:49Z. Updated: 2020-12-14T17:32:49Z.

Source: https://github.com/Qiskit/qiskit/issues/5453#issuecomment-744594511

<details>
<summary>Full comment by @georgios-ts</summary>

@ljubabu You are right. `Diagonal` gate constructs a circuit that is equivalent up to a global phase (and does not track it) but this becomes a relative phase when you add control.

</details>


## Closure and reopening events

- 2021-01-19T17:10:31Z: closed by @mergify[bot].

Closing an issue does not establish that a code fix was merged or released.

## Attribution and reuse

The original post and comments remain attributed to their upstream authors.
Their inclusion does not relicense them under this project's MIT license.
See [NOTICE](../../NOTICE). Machine-readable text and provenance are in
[source.json](source.json); curated version evidence is in
[the manifest](../manifest.json). Attachments are linked, not vendored.
