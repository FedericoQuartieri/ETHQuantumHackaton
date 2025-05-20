from utils import *

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
import numpy as np
from qiskit.quantum_info import Statevector, partial_trace, state_fidelity

def validate(qc1 : QuantumCircuit, qc2 : QuantumCircuit):
    # 2) Turn them into state-vectors
    sv1 = Statevector.from_instruction(qc1)
    sv2 = Statevector.from_instruction(qc2)

    # 3) Compute the overlap ⟨sv1|sv2⟩
    overlap = np.vdot(sv1.data, sv2.data)
    print("⟨sv1|sv2⟩ =", overlap)

    # 4) (Optionally) fidelity = |⟨sv1|sv2⟩|^2
    fidelity = abs(overlap)**2
    print("Fidelity =", fidelity)

    return fidelity

def validateAncilla(qc1,qc2):
    psi = Statevector.from_instruction(qc1)
    phi = Statevector.from_instruction(qc2)

    sv_psi = Statevector(psi)
    sv_phi = Statevector(phi)

    psi = np.array(psi, dtype=complex)
    phi = np.array(phi, dtype=complex)

    # Trace out qubit index 3 (the fourth qubit) → two 3-qubit density matrices
    #rho_psi_3 = partial_trace(sv_psi, [])
    rho_phi_3 = partial_trace(sv_phi, [3])

    # Compute the Uhlmann fidelity F(ρ,σ)
    F_012 = state_fidelity(psi, rho_phi_3)
    print("Fidelity over qubits 0-2:", F_012)


if __name__ == "__main__":
    programs = importQASM("../inputs")

    qc1 = circuit_to_qiskit(programs.get("1"))
    qc2 = circuit_to_qiskit(programs.get("1_improved"))
    print("Validate 1 <-> 1_improved...")
    validateAncilla(qc1, qc2)

    qc1 = circuit_to_qiskit(programs.get("3"))
    qc2 = circuit_to_qiskit(programs.get("3_improved"))
    print("Validate 3 <-> 3_improved...")
    validate(qc1, qc2)

