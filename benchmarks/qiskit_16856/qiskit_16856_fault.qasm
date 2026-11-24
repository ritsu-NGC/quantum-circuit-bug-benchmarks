OPENQASM 2.0;
include "qelib1.inc";
gate gate_PauliEvolution(param0) q0,q1 { rzz(0.8) q0,q1; }
qreg q[2];
gate_PauliEvolution(1.0) q[0],q[1];