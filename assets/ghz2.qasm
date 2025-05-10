OPENQASM 2.0;
include "qelib1.inc";
qreg q[4];
h q[0];
CX q[0], q[2];
CX q[0], q[1];
CX q[2], q[3];

