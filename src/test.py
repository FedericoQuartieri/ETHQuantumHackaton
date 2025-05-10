from utils import *
from bloqade import qasm2
from kirin.dialects import ilist
import math

def ghz_log_depth(n: int):
    n_qubits = int(2**n)

    @qasm2.extended
    def layer_of_cx(i_layer: int, qreg: qasm2.QReg):
        # count layer and deploy CNOT gates accordingly
        step = n_qubits // (2**i_layer)
        for j in range(0, n_qubits, step):
            qasm2.cx(ctrl=qreg[j], qarg=qreg[j + step // 2])

    @qasm2.extended
    def ghz_log_depth_program():

        q = qasm2.qreg(n_qubits)
        # add starting Hadamard and build layers
        qasm2.h(q[0])
        for i in range(n):
            layer_of_cx(i_layer=i, qreg=q)

    return ghz_log_depth_program




def ghz_log_simd(n: int):
    n_qubits = int(2**n)

    @qasm2.extended
    def layer(i_layer: int, qreg: qasm2.QReg):
        step = n_qubits // (2**i_layer)

        def get_qubit(x: int):
            return qreg[x]

        ctrl_qubits = ilist.map(fn=get_qubit, collection=range(0, n_qubits, step))
        targ_qubits = ilist.map(
            fn=get_qubit, collection=ilist.range(step // 2, n_qubits, step)
        )

        # Ry(-pi/2)
        qasm2.parallel.u(qargs=targ_qubits, theta=-math.pi / 2, phi=0.0, lam=0.0)

        # CZ gates
        qasm2.parallel.cz(ctrls=ctrl_qubits, qargs=targ_qubits)

        # Ry(pi/2)
        qasm2.parallel.u(qargs=targ_qubits, theta=math.pi / 2, phi=0.0, lam=0.0)

    @qasm2.extended
    def ghz_log_depth_program():

        q = qasm2.qreg(n_qubits)

        qasm2.u3(qarg=q[0], theta=math.pi / 2, phi=0.0, lam=math.pi)
        for i in range(n):
            layer(i_layer=i, qreg=q)

    return ghz_log_depth_program


circ = circuit_to_qiskit(ghz_log_simd(2))
show_circuit(circ)

#ast = target.emit(ghz_log_simd(2))
#pprint(ast)