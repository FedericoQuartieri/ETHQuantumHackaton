// Generated from Cirq v1.4.1

OPENQASM 2.0;
include "qelib1.inc";

qreg q[5];

h q[0];
rz(pi*0.25) q[1];
rz(pi*0.125) q[2];
rz(pi*0.0625) q[3];
rz(pi*0.03125) q[4];

cx q[0],q[4];
cx q[0],q[3];
cx q[0],q[2];
cx q[0],q[1];

rz(-pi*0.25) q[1];
rz(-pi*0.125) q[2];
rz(-pi*0.0625) q[3];
rz(-pi*0.03125) q[4];

cx q[0],q[1];
cx q[0],q[2];
cx q[0],q[3];
cx q[0],q[4];

rz(pi*0.4375) q[0];