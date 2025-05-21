// toffoli_qft_style.qasm
OPENQASM 2.0;
include "qelib1.inc";

qreg q[3];

h q[2];
cx q[2],q[0];
cx q[2], q[1];
u(0, 5/4*pi, pi/2) q[0];
u(0, 11/8*pi, pi/2) q[1];
cx q[2], q[1];
cx q[2],q[0];
h q[1];
u(0, 7/4*pi, pi/2) q[2];
cx q[0], q[1];
u(0, 13/8*pi, pi/2) q[2];
u(0, 5/4*pi, pi/2) q[1];
cx q[0], q[1];
h q[0];
u(0, 7/4*pi, pi/2) q[1];