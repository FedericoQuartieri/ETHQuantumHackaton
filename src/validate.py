from utils import *

from qiskit import transpile


from qiskit.visualization import plot_histogram

from qiskit_aer import Aer
from qiskit_ibm_runtime import QiskitRuntimeService


from qiskit import QuantumCircuit
from qiskit_ibm_runtime import SamplerV2 as Sampler
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
    rho_psi_3 = partial_trace(sv_psi, [3])
    rho_phi_3 = partial_trace(sv_phi, [3])

    # Compute the Uhlmann fidelity F(ρ,σ)
    F_012 = state_fidelity(rho_psi_3, rho_phi_3)
    print("Fidelity over qubits 0-2:", F_012)



def parseResult(counts):
    new_counts = {}
    for key, value in counts.items():
        # Rimuove spazi e calcola metà lunghezza
        clean_key = key.replace(" ", "")
        half_len = len(clean_key) // 2
        trimmed_key = clean_key[:half_len]
        new_counts[trimmed_key] = new_counts.get(trimmed_key, 0) + value
    return new_counts

def validateAncillaExecute(qc1, qc2):
    shots = 100000
    backend = Aer.get_backend('qasm_simulator')
    qc1.measure_all()


    tqc1 = transpile(qc1, backend)
    result = backend.run(tqc1, shots=shots).result()
    q1_counts = parseResult(result.get_counts())
    #print(q1_counts)
    plot_histogram(q1_counts)

    qc2.measure_all()
    tqc2 = transpile(qc2, backend)
    result = backend.run(tqc2, shots=shots).result()
    q2_parsed = parseResult(result.get_counts())
    #print(q2_parsed)
    plot_histogram(q2_parsed)


    #remove ancilla
    q2_counts = {}
    for key, value in q2_parsed.items():
        # Remove spaces and get clean bitstring
        clean_key = key.replace(" ", "")
        # Remove first bit
        trimmed = clean_key[1:]
        # Optional: group in blocks of 4 for readability
        formatted = ' '.join([trimmed[i:i+4] for i in range(0, len(trimmed), 4)])
        # Sum counts if the new key already exists
        q2_counts[formatted] = q2_counts.get(formatted, 0) + value


    accumulator = 0 

    for key in q1_counts:
        if key in q2_counts:
            diff = q1_counts[key] - q2_counts[key]
            accumulator += abs(diff)


    fidelity = 1 - accumulator / shots

    print("Fidelity =", fidelity)

    return fidelity




if __name__ == "__main__":
    programs = importQASM("../inputs")

    # qc1 = circuit_to_qiskit(programs.get("4"))
    # qc2 = circuit_to_qiskit(programs.get("4_improved"))
    # validate(qc1, qc2)

    qc1 = circuit_to_qiskit(programs.get("1"))
    qc2 = circuit_to_qiskit(programs.get("1_improved"))
    print(validateAncillaExecute(qc1, qc2))



    # validateAncilla(qc1, qc2)



