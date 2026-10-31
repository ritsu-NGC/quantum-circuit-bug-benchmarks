# Qiskit issue #14265: `StatePrepartion` generates the wrong unitary when `inverse=True`

## Benchmark metadata

| Field | Value |
| --- | --- |
| Original issue | https://github.com/Qiskit/qiskit/issues/14265 |
| Source repository | `Qiskit/qiskit` |
| Original author | @diemilio |
| Reported Qiskit version(s) at the issue | `2.0` |
| Verified Qiskit version(s) containing the fix | Not verified |
| Assessment | Disputed report / expected behavior under discussion |
| Upstream state at snapshot | open |
| Created | 2025-04-29T15:36:39Z |
| Last upstream update | 2025-05-02T15:10:17Z |
| Closed | Not closed |
| Retrieved | 2026-10-30T17:28:03+00:00 |

**Reported-version context:** Version(s) reported in the original issue environment; not a first-affected boundary.

**Assessment:** The initial wrong-inverse claim is qualified by the author and maintainer: StatePreparation only promises |0> -> |psi>, not a unique full-space unitary. String and vector inputs may validly choose different unitary extensions. Do not treat |+> vs |-> on inverse input |0> alone as a confirmed circuit-semantics bug.

**Resolution:** Issue remains open with discussion of consistency/documentation. No numerical fixed version is applicable or verified for the original claim.

Reported versions are not an exhaustive affected range. A verified fixed
version is a published release containing the fix, not necessarily the
first fixed version across all maintenance branches. Historical fixed
release versions below 1.0 refer to `qiskit-terra`, not the old `qiskit`
metapackage. Reported versions retain their original distribution context.

## Fix and resolution evidence

- https://github.com/Qiskit/qiskit/issues/14265#issuecomment-2844831103
- https://github.com/Qiskit/qiskit/issues/14265#issuecomment-2844856579

## Original issue post

The body below is reproduced verbatim from the original issue post as
returned by GitHub at retrieval time. It may include upstream edits,
mistakes, HTML, and externally hosted attachments. It is not a
reconstruction of the issue's initial, pre-edit revision.

Source: https://github.com/Qiskit/qiskit/issues/14265 by @diemilio.

<details>
<summary>Full original issue text</summary>

### Environment

- **Qiskit version**: 2.0
- **Python version**: 3.11.9
- **Operating system**: MacOS


### What is happening?

The [`StatePreparation`](https://docs.quantum.ibm.com/api/qiskit/qiskit.circuit.library.StatePreparation) function generates the wrong unitary (and therefore the wrong statevector) when the `params` parameter is of type `Statevector`/`list` and the `inverse` parameter is set to `True`.

### How can we reproduce the issue?

The following code generates statevector $|-\rangle$ when it should generate $|+\rangle$:

```python
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import StatePreparation
from qiskit.quantum_info import Statevector

ψ = Statevector.from_label('+')

qc = QuantumCircuit(1)
qc.append(StatePreparation(ψ, inverse=True),[0])

print(Statevector(qc))
```

output: `Statevector([ 0.70710678+0.j, -0.70710678+0.j], dims=(2,))`


If one alternatively passes a string to `StatePreparation`, the correct statevector is generated:

```python
qc2 = QuantumCircuit(1)
qc2.append(StatePreparation('+', inverse=True),[0])

print(Statevector(qc2))
```

output: `Statevector([ 0.70710678+0.j, 0.70710678+0.j], dims=(2,))`

### What should happen?

The `inverse` of StatePreparation should generate a circuit with a matrix that corresponds to the conjugate transpose of the non-inverted version

### Any suggestions?

This issue seems to stem from how the inverse of the `Isometry` instruction is being [generated](https://github.com/Qiskit/qiskit/blob/c6f38dced02017a3478acdae3df992f71e20e019/qiskit/circuit/library/generalized_gates/isometry.py#L121).

</details>

## Issue discussion, including closing and resolving comments

All fetched issue comments are preserved below in upstream chronological
order, including any closing or resolving comments. Comments are
third-party statements, not automatically verified benchmark claims.

### Comment 2844831103 by @diemilio

Posted: 2025-05-01T13:17:00Z. Updated: 2025-05-01T13:17:00Z.

Source: https://github.com/Qiskit/qiskit/issues/14265#issuecomment-2844831103

<details>
<summary>Full comment by @diemilio</summary>

Thinking more carefully about this, there isn't a bug with the `Isometry` process of generating the unitary. 

There is however an inconsistency between how the unitary is generated if one uses  `params` of type `str` vs. using `list`/`Statevector`. This is because when using `str`, the `Statepreparation` function "shortcuts" the Isometry process and relies on using gates (like `XGate`, `HGate`, etc.), which are not equivalent with the unitaries generated when using an Isometry.

For example, this line of code I have above:

```python
qc2.append(StatePreparation('+', inverse=True),[0])
```

`Statepreparation` uses an $H$ gate, but the isometry would generate the equivalent of an $X H$ operation.

Not sure if this is something that requires fixing, but there is definitely differences in what the function generates depending on the the type of parameter used.

</details>

### Comment 2844856579 by @jakelishman

Posted: 2025-05-01T13:33:56Z. Updated: 2025-05-01T13:36:45Z.

Source: https://github.com/Qiskit/qiskit/issues/14265#issuecomment-2844856579

<details>
<summary>Full comment by @jakelishman</summary>

Thanks for the report and looking into it.  Restating your point, `StatePreparation("+")` is only required to produce the mapping ${\lvert0\rangle}\to{\lvert+\rangle}$, and consequently `StatePreparation("+").inverse()` only has a well-defined action ${\lvert{+}\rangle}\to{\lvert0\rangle}$, so its action on $\lvert0\rangle$ is only constrained to produce an equal superposition $\bigl({\lvert0\rangle} + e^{i\theta}{\lvert1\rangle}\bigr)/\sqrt2$ by unitarity, but there's freedom in $\theta$.

I suspect that reasonably, we can't do much about the discrepancy between string and array input states without trashing the performance of the string form, which is likely no good for the primary use-case of the class.  Do you think a documentation-only change explicitly calling out this would be a suitable resolution?

</details>

### Comment 2845056988 by @diemilio

Posted: 2025-05-01T15:22:07Z. Updated: 2025-05-01T15:23:14Z.

Source: https://github.com/Qiskit/qiskit/issues/14265#issuecomment-2845056988

<details>
<summary>Full comment by @diemilio</summary>

Personally, I like the idea of keeping things consistent rather than adding notes to the documentation, which can lead to confusion.

Since there are only 5 `str` options, the fix would be relatively straightforward, but I understand if you believe this degrades the performance too much. I'll spell out the changes below in case you think this is a reasonable fix. It would be required to add 1 extra gate in 4 particular cases.

Under `def _define_from_label(self)`:

```python
        for qubit, param in enumerate(reversed(self.params)):
            if param == "1":
                initialize_circuit.append(ZGate(), [q[qubit]])  # add Z gate
                initialize_circuit.append(XGate(), [q[qubit]])
            elif param == "+":
                initialize_circuit.append(ZGate(), [q[qubit]])  # add Z gate
                initialize_circuit.append(HGate(), [q[qubit]])
            elif param == "-":
                initialize_circuit.append(XGate(), [q[qubit]])
                initialize_circuit.append(HGate(), [q[qubit]])
            elif param == "r":  # |+i>
                initialize_circuit.append(SGate(), [q[qubit]])  # add S gate
                initialize_circuit.append(HGate(), [q[qubit]])
                initialize_circuit.append(SGate(), [q[qubit]])
            elif param == "l":  # |-i>
                initialize_circuit.append(SdgGate(), [q[qubit]])  # add Sdg gate
                initialize_circuit.append(HGate(), [q[qubit]])
                initialize_circuit.append(SdgGate(), [q[qubit]])
```

</details>

### Comment 2845095185 by @jakelishman

Posted: 2025-05-01T15:41:41Z. Updated: 2025-05-01T15:41:41Z.

Source: https://github.com/Qiskit/qiskit/issues/14265#issuecomment-2845095185

<details>
<summary>Full comment by @jakelishman</summary>

How certain are we that the particular decomposition of `Isometry` will _always_ be consistent with the definitions you've got there?  I can certainly imagine a situation where initialisation to `"+" * 8` causes the recursive decomposition of the matrix to use $H$ on some qubits and $ZH$ on others, just due to round-offs being different as it peels off the qubits.  It would also be sensitive to the numerics of `Isometry` changing (which is very likely to happen as we move more stuff to Rust).

Fwiw, I wouldn't be worried about performance with your suggestion - my concern there is just in us deliberately introducing unnecessary gates under an assumption that the array-based decomposition in `Isometry` will always spit out those particular derivations.  I was concerned about performance in a situation where we handle the string form by first generating the statevector and then decomposing that; it'd guarantee consistency, but stop the method from scaling.

</details>

### Comment 2845102141 by @jakelishman

Posted: 2025-05-01T15:45:17Z. Updated: 2025-05-01T15:45:17Z.

Source: https://github.com/Qiskit/qiskit/issues/14265#issuecomment-2845102141

<details>
<summary>Full comment by @jakelishman</summary>

Oh, in writing that out, maybe here's an alternative approach: we leave the circuit generation largely as-is, but just insert a little bit of logic to prevent the addition of a $Z$ rotation while the input qubit is known to be in the $\lvert 0\rangle$ state?  At worst, we could just have the isometry-based decomposition stay exactly as it is, but then copy the operations into a circuit throwing away initial $Z$ rotations.

</details>

### Comment 2845240830 by @diemilio

Posted: 2025-05-01T16:54:26Z. Updated: 2025-05-01T17:06:06Z.

Source: https://github.com/Qiskit/qiskit/issues/14265#issuecomment-2845240830

<details>
<summary>Full comment by @diemilio</summary>

Sorry @jakelishman, not sure I follow your suggestion about adding logic when the input qubit is $|0\rangle$. My understanding is that, in the single qubit case, when one wants to generate state $\alpha |0\rangle + \beta|1\rangle,$ the isometry constructs a matrix of the form: 

$$ U = [[ \alpha,  -\beta^* ], [ \beta, \alpha^* ]]. $$

So, for example, for state $|+\rangle,$ this will correspond to:

$$ U = [[1,  -1], [1, 1]]. $$

which differs from a Hadamard gate (which is what is used when the `'+'` string is used):

$$ H = [[1,  1], [1, -1]]. $$

This means the unitaries (independent of what the input state is) are different, mainly because of what is assigned to the second column is not equivalent. In the case of the "left" and "right" states, the difference is not just a phase of $-1$ because of the conjugation of variables that happens in the second column. 

I see your point about guaranteeing that the isometry decomposition for larger systems will match to the unitary generated by the circuits I suggested. In general, you are right, this doesn't work.

So, not quite sure what the right solution is; maybe your suggestion of just adding these details to the documentation is the best way to go about it.

</details>

### Comment 2845286563 by @jakelishman

Posted: 2025-05-01T17:13:43Z. Updated: 2025-05-01T17:13:43Z.

Source: https://github.com/Qiskit/qiskit/issues/14265#issuecomment-2845286563

<details>
<summary>Full comment by @jakelishman</summary>

The action of $\text{StatePreparation}[{\lvert\psi\rangle}]$ is only defined up to ${\lvert0\rangle}\to{\lvert\psi\rangle}$, and the action on the rest of Hilbert space that's orthogonal to that single input is left undefined.  So for 1q $\alpha{\lvert0\rangle} + \beta{\lvert1\rangle}$, the only constraint on the matrix in the computational basis is that the top row is $(\alpha\quad\beta)$ and the bottom row is orthogonal to it.  I really don't know the details of the `Isometry` class, so correct me if I'm wrong, but I don't think it actually creates a 2x2 matrix here; I think it just takes the 1q vector.  Either way, the point is that while `Isometry` is required to be reproducible, it's not required to produce any particular unitary, even in the 1q case, because you can apply a relative phase to its action on $\lvert1\rangle$ and it still satisfies the contract.

For my other point, more simply, what I mean is: how about in `StatePreparation` we just take the circuit that `Isometry` gives us, then remove any $S$, $S^\dagger$ or $Z$ gates that are the initial gates on a qubit?  It doesn't change the action on the single input state that we're contracted to match exactly, and in the case of separable Pauli-eigenvector input states (such as can be specified by the string form), assuming `Isometry` doesn't introduce spurious entanglement, it should in practice produce the same result as the string form, I think?

</details>

### Comment 2847165860 by @diemilio

Posted: 2025-05-02T13:09:03Z. Updated: 2025-05-02T15:10:16Z.

Source: https://github.com/Qiskit/qiskit/issues/14265#issuecomment-2847165860

<details>
<summary>Full comment by @diemilio</summary>

Regarding the first point; Yes. I am sorry, I didn't mean that the `Isometry` literately generates a matrix (I am actually unsure of the details). I was just trying to make the point that, since the discrepancy arises when taking the `inverse`, the difference can be identified by looking at the gate's unitary (by for example running `Operator(StatePreparation(ψ))`). In any case, I get your point about the relative phase; it can be anything else.

For the second point, I think I understand except I am not quite sure how the logic will work, but I guess that's the work that has to go into the fix the issue.

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
