OPENQASM 2.0;
include "qelib1.inc";
qreg var_0[3];
cz var_0[1], var_0[0];
U(1.5707963267949, 3.14159265358979, 3.14159265358979) var_0[1];
cz var_0[2], var_0[1];
U(1.5707963267949, -0.0, -0.0) var_0[1];
