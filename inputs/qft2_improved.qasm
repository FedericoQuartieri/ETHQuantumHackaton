// Generated from Cirq v1.4.1

OPENQASM 2.0;
include "qelib1.inc";

qreg q[8];

h q[3];
rz(pi*0.25) q[4];
rz(pi*0.125) q[5];
rz(pi*0.0625) q[6];
rz(pi*0.03125) q[7];

cx q[3],q[2];
barrier q[2],q[3];

cx q[3],q[0];
cx q[2],q[1];
barrier q[0],q[1],q[2],q[3];

cx q[3],q[4];
cx q[2],q[5];
cx q[1],q[6];
cx q[0],q[7];
barrier q[0],q[1],q[2],q[3],q[4],q[5],q[6],q[7];


rz(-pi*0.25) q[4];
rz(-pi*0.125) q[5];
rz(-pi*0.0625) q[6];
rz(-pi*0.03125) q[7];

cx q[3],q[4];
cx q[2],q[5];
cx q[1],q[6];
cx q[0],q[7];
barrier q[0],q[1],q[2],q[3],q[4],q[5],q[6],q[7];

rz(pi*0.4375) q[3];