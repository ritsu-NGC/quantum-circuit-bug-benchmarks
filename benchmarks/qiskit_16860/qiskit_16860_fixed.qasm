OPENQASM 2.0;
include "qelib1.inc";
gate rzx(param0) q0,q1 { h q1; cx q0,q1; rz(param0) q1; cx q0,q1; h q1; }
gate gate_PauliEvolution(param0) q0,q1 { rzx(2.0) q0,q1; }
qreg q[3];
gate_PauliEvolution(1.0) q[2],q[0];
