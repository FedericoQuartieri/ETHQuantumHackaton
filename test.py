#!/usr/bin/env python3
"""
Visualizza in Matplotlib il circuito generato da una funzione Bloqade-extended.
"""

import math
from bloqade import qasm2
from bloqade.qasm2.emit import QASM2
from qiskit import QuantumCircuit
import matplotlib.pyplot as plt

# 1) Definisci qui la tua routine estesa
@qasm2.extended
def ghz_log_depth(n: int):
    q = qasm2.qreg(n)
    # ... (implementazione del circuito log-depth GHZ) ...
    # per esempio:
    for i in range(1, n):
        qasm2.parallel.cx(ctrls=[q[0]], qargs=[q[i]])
    return q

def draw_extended(func, arg, scale=1.0, output_png=None):
    # 2) Emetti il QASM2 esteso
    emitter = QASM2()
    ast = emitter.emit(func(arg))

    # 3) Serializza in stringa
    from bloqade.qasm2.parse import pprint
    import io
    buf = io.StringIO()
    pprint(ast, stream=buf)
    qasm_str = buf.getvalue()

    # 4) Costruisci il QuantumCircuit da stringa QASM
    qc = QuantumCircuit.from_qasm_str(qasm_str)

    # 5) Disegna con Matplotlib
    fig = qc.draw(output='mpl', scale=scale)
    plt.show()

    # 6) (Opzionale) salva su file
    if output_png:
        fig.savefig(output_png, bbox_inches='tight')
        print(f"Saved extended circuit diagram to {output_png}")
    plt.close(fig)

if __name__ == "__main__":
    # Esempio di uso:
    draw_extended(ghz_log_depth, 3, scale=1.2, output_png="ghz_ext.png")
