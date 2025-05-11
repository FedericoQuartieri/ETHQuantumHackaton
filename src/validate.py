from utils import *

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
import numpy as np

def validate(qc1, qc2):
    # 2) Turn them into state-vectors
    sv1 = Statevector.from_instruction(qc1)
    sv2 = Statevector.from_instruction(qc2)
    show_circuit(qc1)
    show_circuit(qc2)

    # 3) Compute the overlap ⟨sv1|sv2⟩
    overlap = np.vdot(sv1.data, sv2.data)
    print("⟨sv1|sv2⟩ =", overlap)

    # 4) (Optionally) fidelity = |⟨sv1|sv2⟩|^2
    fidelity = abs(overlap)**2
    print("Fidelity =", fidelity)




programs = importQASM()
#qc1 = circuit_to_qiskit(programs.get("7"))
qc2 = circuit_to_qiskit(programs.get("4_improved"))
show_circuit(qc2)
#validate(qc1, qc2)
