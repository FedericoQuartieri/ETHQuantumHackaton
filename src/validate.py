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


def validateNotExecute(qc1 : QuantumCircuit, qc2 : QuantumCircuit, ancilla = False):
    sv1 = Statevector.from_instruction(qc1)
    sv2 = Statevector.from_instruction(qc2)
    fidelity = 0

    if (ancilla):
        sv_psi = Statevector(sv1)
        sv_phi = Statevector(sv2)

        rho_phi_3 = partial_trace(sv_phi, [3])

        fidelity = state_fidelity(sv_psi, rho_phi_3)
    else:
        overlap = np.vdot(sv1.data, sv2.data)
        print("⟨sv1|sv2⟩ =", overlap)
        fidelity = abs(overlap)**2


    print("Fidelity =", fidelity)

    return fidelity



def validateExecute(qc1, qc2, ancilla=True, shots = 100000, first=True, n=2):
    backend = Aer.get_backend('qasm_simulator')
    qc1.measure_all()


    tqc1 = transpile(qc1, backend)
    result = backend.run(tqc1, shots=shots).result()
    q1_counts = result.get_counts()
    #print(q1_counts)
    plot_histogram(q1_counts)

    qc2.measure_all()
    tqc2 = transpile(qc2, backend)
    result = backend.run(tqc2, shots=shots).result()
    q2_parsed = result.get_counts()
    #print(q2_parsed)
    #show_circuit(qc1)
    #plot_histogram(q2_parsed)


    q2_counts = {}

    #remove ancilla
    if ancilla:
        for key, value in q2_parsed.items():
            # 1) ripulisco la stringa dai blank
            clean_key = key.replace(" ", "")
            
            # 2) trimming: se n<=0 non tolgo nulla,
            #    altrimenti tolgo primi n o ultimi n in base a first
            if n <= 0:
                trimmed = clean_key
            else:
                if first==False:
                    # rimuovo i primi n
                    trimmed = clean_key[n:]
                else:
                    # rimuovo gli ultimi n
                    trimmed = clean_key[:-n]

            
            # 4) sommo i conteggi
            q2_counts[trimmed] = q2_counts.get(trimmed, 0) + value
    else:
        q2_counts = q2_parsed


    accumulator = 0 

    for key in q1_counts:
        if key in q2_counts:
            diff = q1_counts[key] - q2_counts[key]
            accumulator += abs(diff)

    fidelity = 1 - accumulator / shots

    print("Fidelity =", fidelity)

    return fidelity



def validate(qc1, qc2, ancilla = False, execute = False, shots = 100000, first=True, n = 2):
    if execute: return validateExecute (qc1, qc2, ancilla=ancilla, shots = shots, first=first, n = n)
    else : return validateNotExecute (qc1, qc2, ancilla=ancilla)



if __name__ == "__main__":
    programs = importQASM("../inputs")

    qc1 = circuit_to_qiskit(programs.get("qft2"))
    qc2 = circuit_to_qiskit(programs.get("qft2_improved"))
    print(validate(qc1, qc2, ancilla=True, execute=True, shots = 100000, first=True, n = 3))

