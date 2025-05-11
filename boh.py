from utils import *
from validate import validate

import numpy as np
from qiskit import QuantumCircuit, transpile

qc = QuantumCircuit(3)
qc.h(2)
qc.cx(1,2)
qc.u(0, 5*np.pi/4, np.pi/2, 2)
qc.cx(0,2)
qc.u(0, 7*np.pi/4, np.pi/2, 2)
qc.h(1)
qc.cx(0,1)
qc.u(0, 11*np.pi/8, np.pi/2, 1)
qc.cx(0,1)
qc.u(0, 13*np.pi/8, np.pi/2, 1)
qc.h(0)

# then transpile as before
transpiled = transpile(
    qc,
    basis_gates=['rz','sx','cx','h','u'],
    coupling_map=[[0,1],[1,2]],
    optimization_level=3
)
print(transpiled.draw(output='text'))


def linear_qft_k(k: int) -> QuantumCircuit:
    """Return k-qubit QFT in the 'picture d' linear-NN form."""
    circ = QuantumCircuit(k)
    for tgt in range(k-1, -1, -1):          # bottom→top
        circ.h(tgt)
        for ctl in range(tgt-1, -1, -1):
            angle = np.pi / 2**(tgt-ctl)
            circ.cx(ctl, tgt)
            circ.rz(angle, tgt)
            circ.cx(ctl, tgt)
        circ.barrier()
    # transpile to linear chain 0-1-…-k-1
    line = [[i, i+1] for i in range(k-1)]
    return transpile(
        circ,
        coupling_map=line,
        basis_gates=['rz', 'sx', 'cx', 'h'],
        optimization_level=3
    )

opt_d = linear_qft_k(5)
show_circuit(opt_d)

# programs = importQASM()
# qc1 = circuit_to_qiskit(programs.get("1"))
# validate(qc, qc1)
