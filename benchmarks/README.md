# Benchmark index

This snapshot contains 26 reports from `Qiskit/qiskit`.

Fixed versions below are verified containing releases, not necessarily
the first fixed release on every branch. See each README for provenance,
complete original text, all issue comments, and verification evidence.
Not every retained report is a confirmed circuit bug.

| Benchmark | Original issue title | Reported version(s) | Verified fixed version(s) | Assessment |
| --- | --- | --- | --- | --- |
| [qiskit_17057](qiskit_17057/README.md) | Two-qubit synthesis to ["cx", "rz", "sx", "x"] returns a wrong circuit (1 - F_avg ≈ 0.07) near the two-CX boundary | `2.5.2` | `2.6.0` | Confirmed bug |
| [qiskit_16919](qiskit_16919/README.md) | Qiskit generates invalid qasm3 for circuits with MCX/MCZ gates | `2.5.2` | `2.6.0` | Confirmed bug |
| [qiskit_16860](qiskit_16860/README.md) | `FindCommutingPauliEvolutions` ignores gate qargs and changes asymmetric Pauli evolutions | `2.5.2`, `2.6.0.dev0+b6f798f` | Not verified | Confirmed bug |
| [qiskit_16856](qiskit_16856/README.md) | `FindCommutingPauliEvolutions` silently drops duplicate Pauli summands on the same qubit pair | `2.5.2`, `2.6.0.dev0+b6f798f` | `2.6.0` | Confirmed bug |
| [qiskit_16594](qiskit_16594/README.md) | CommutativeCancellation cancels an sxdg·sxdg pair that equals X, giving wrong results at optimization_level ≥ 2 | `2.5.0` | `2.5.1` | Confirmed bug |
| [qiskit_16524](qiskit_16524/README.md) | PhaseOracleGate (All 1s) | Not specified | `2.5.1`, `2.6.0` | Confirmed bug |
| [qiskit_16456](qiskit_16456/README.md) | `Commuting2qBlock` loses parameters from parametric gates | Not specified | `2.6.0` | Confirmed bug |
| [qiskit_16411](qiskit_16411/README.md) | OptimizeAnnotated (_canonicalize_modifiers) changes the unitary for a negative fractional PowerModifier | `2.4.1` | Not verified | Disputed report / expected behavior under discussion |
| [qiskit_16377](qiskit_16377/README.md) | `CommutativeCancellation` incorrectly adds spurious global phase to P/U1 gates accumulating to 2π | `2.4.1` | `2.5.0` | Confirmed bug |
| [qiskit_16164](qiskit_16164/README.md) | CommutationChecker yields false positives for CRZ and SWAP resulting in silent miscompilation | `2.4.1` | `2.4.2`, `2.5.0` | Confirmed bug |
| [qiskit_16161](qiskit_16161/README.md) | CommutativeOptimization silently corrupts direction-sensitive XXPlusYYGate by incorrectly treating it as a symmetric gate | `2.4.1` | `2.5.0` | Confirmed bug |
| [qiskit_16168](qiskit_16168/README.md) | MultiplierGate(1, 1).decompose() fails because its definition has the wrong number of qubits | `2.4.1` | `2.4.2`, `2.5.0` | Confirmed bug |
| [qiskit_14356](qiskit_14356/README.md) | HoareOptimizer incorrectly optimizes unitary gates | `2.0.0` | Not verified | Confirmed bug |
| [qiskit_14265](qiskit_14265/README.md) | `StatePrepartion` generates the wrong unitary when `inverse=True` | `2.0` | Not verified | Disputed report / expected behavior under discussion |
| [qiskit_13547](qiskit_13547/README.md) | Incorrect transpilation with RY gate with a small angle | `1.3.0`, `2.0.0.dev0+841cb29`, `1.2.4` | `2.0.0` | Confirmed bug |
| [qiskit_12948](qiskit_12948/README.md) | Transpile Optimization Level 2 and 3 Give Incorrect Circuits | `1.1.1` | `1.2.0` | Confirmed bug |
| [qiskit_12694](qiskit_12694/README.md) | Wrong export/import of OpenQASM2 with custom Unitary | `1.1.0` | Not verified | Mixed report: confirmed and disputed/expected aspects |
| [qiskit_11954](qiskit_11954/README.md) | qasm3 returns wrong results with pauli evolution gate | Not specified | `1.2.0` | Confirmed bug |
| [qiskit_9805](qiskit_9805/README.md) | `QuantumCircuit.qasm` cannot handle nested gates with different parameters | `0.24.0.dev0+3005806` | `0.24.0` | Confirmed bug |
| [qiskit_9327](qiskit_9327/README.md) | Approximate quantum compiler (AQC) returns a wrong circuit when the unitary has a determinant −1 | `0.22.3` | `0.23.0` | Confirmed bug |
| [qiskit_5666](qiskit_5666/README.md) | classical_function creates wrong circuits for some cases | Not specified | `0.17.0` | Mixed report: confirmed and disputed/expected aspects |
| [qiskit_5453](qiskit_5453/README.md) | Control of the diagonal gate not working properly | `0.16.1` | `0.17.0` | Confirmed bug |
| [qiskit_6134](qiskit_6134/README.md) | Controlled HamiltonianGate seems to be wrong | Not specified | `0.18.0` | Confirmed bug |
| [qiskit_7209](qiskit_7209/README.md) | `C3SXGate` inconsistent with `SXGate` | `0.18.3` | `0.19.0` | Confirmed bug |
| [qiskit_3433](qiskit_3433/README.md) | Incorrect transpilation of phase-gadgets with small angles on optimisation level 2 and 3 | `0.10.0` | Not verified | Confirmed bug |
| [qiskit_86](qiskit_86/README.md) | Bug in cu3 implementation | `0.3.5` | Not applicable | Explained upstream as not a bug |

Curated metadata: [manifest.json](manifest.json).
