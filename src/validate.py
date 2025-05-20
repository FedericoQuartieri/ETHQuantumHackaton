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



def parseResult(counts):
    new_counts = {}
    for key, value in counts.items():
        # Rimuove spazi e calcola metà lunghezza
        clean_key = key.replace(" ", "")
        half_len = len(clean_key) // 2
        trimmed_key = clean_key[:half_len]
        new_counts[trimmed_key] = new_counts.get(trimmed_key, 0) + value
    return new_counts

def validate(qc1 : QuantumCircuit, qc2 : QuantumCircuit, ancilla = False):
    sv1 = Statevector.from_instruction(qc1)
    sv2 = Statevector.from_instruction(qc2)
    fidelity = 0

    if (ancilla):
        sv_psi = Statevector(psi)
        sv_phi = Statevector(phi)

        rho_psi_3 = partial_trace(sv_psi, [3])
        rho_phi_3 = partial_trace(sv_phi, [3])

        fidelity = state_fidelity(rho_psi_3, rho_phi_3)
    else:
        overlap = np.vdot(sv1.data, sv2.data)
        print("⟨sv1|sv2⟩ =", overlap)
        fidelity = abs(overlap)**2


    print("Fidelity =", fidelity)

    return fidelity



# def validateAncilla(qc1,qc2):
#     psi = Statevector.from_instruction(qc1)
#     phi = Statevector.from_instruction(qc2)

#     sv_psi = Statevector(psi)
#     sv_phi = Statevector(phi)

#     psi = np.array(psi, dtype=complex)
#     phi = np.array(phi, dtype=complex)

#     # Trace out qubit index 3 (the fourth qubit) → two 3-qubit density matrices
#     rho_psi_3 = partial_trace(sv_psi, [3])
#     rho_phi_3 = partial_trace(sv_phi, [3])

#     # Compute the Uhlmann fidelity F(ρ,σ)
#     fid = state_fidelity(rho_psi_3, rho_phi_3)
#     print("Fidelity over qubits 0-2:", F_012)




def validateExecute(qc1, qc2, ancilla=True, shots = 100000):
    backend = Aer.get_backend('qasm_simulator')
    qc1.measure_all()


    tqc1 = transpile(qc1, backend)
    result = backend.run(tqc1, shots=shots).result()
    q1_counts = parseResult(result.get_counts())
    print(q1_counts)
    plot_histogram(q1_counts)

    qc2.measure_all()
    tqc2 = transpile(qc2, backend)
    result = backend.run(tqc2, shots=shots).result()
    q2_parsed = parseResult(result.get_counts())
    print(q2_parsed)
    plot_histogram(q2_parsed)


    q2_counts = {}

    #remove ancilla
    if (ancilla):

        for key, value in q2_parsed.items():
            # Remove spaces and get clean bitstring
            clean_key = key.replace(" ", "")
            # Remove first bit
            trimmed = clean_key[1:]
            # Optional: group in blocks of 4 for readability
            formatted = ' '.join([trimmed[i:i+4] for i in range(0, len(trimmed), 4)])
            # Sum counts if the new key already exists
            q2_counts[formatted] = q2_counts.get(formatted, 0) + value
    else:
        q2_counts = q2_parsed


    accumulator = 0 

    for key in q1_counts:
        if key in q2_counts:
            diff = q1_counts[key] - q2_counts[key]
            accumulator += abs(diff)


    print(accumulator)


    fidelity = 1 - accumulator / shots

    print("Fidelity =", fidelity)

    return fidelity



def validate(qc1, qc2, ancilla = False, execute = False, shots = 100000):
    if execute: return validateExecute (qc1, qc2, ancilla=ancilla, shots = shots)
    else : return validate (qc1, qc2, ancilla=ancilla)



if __name__ == "__main__":
    programs = importQASM("../inputs")

    qc1 = circuit_to_qiskit(programs.get("1"))
    qc2 = circuit_to_qiskit(programs.get("1_improved"))
    print(validate(qc1, qc2, ancilla=True, execute=True, shots = 100000))



