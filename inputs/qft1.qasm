// Generated from Cirq v1.4.1

OPENQASM 2.0;
include "qelib1.inc";

qreg q[5];

h q[0];
cu1(pi/2)  q[1], q[0];
cu1(pi/4)  q[2], q[0];
cu1(pi/8)  q[3], q[0];
cu1(pi/16) q[4], q[0];