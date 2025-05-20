from pathlib import Path
from time import sleep
from typing import Any
##import matplotlib.pyplot as plt


from bloqade import qasm2
from bloqade.qasm2.parse.lowering import QASM2
from bloqade.qasm2.emit import QASM2 as QASM2Target # the QASM2 target
from bloqade.qasm2.passes import QASM2Py
from bloqade.qasm2.emit import QASM2 as QASM2Target # the QASM2 target

from kirin import ir
from qiskit import QuantumCircuit

def sep_print(msg, sleepTimeSec: int = 0):
    """
    Prints a long ##### line separator
    """
    print("#" * 35)
    print(msg)
    if sleepTimeSec > 0:
        sleep(sleepTimeSec)

def importQASM(input_dir) -> dict[str, Any]:
    # path to root is launched from
    exec_root = Path.cwd()  

    # now build a path to .qasm files
    qasm_dir   = exec_root / input_dir
    qasm_file_paths = sorted(qasm_dir.glob("*.qasm"))

    print(qasm_dir)
    if not qasm_file_paths:
        raise FileNotFoundError(f"No .qasm files found in {qasm_dir}")

    # parse & lower each one
    programs = {}
    for path in qasm_file_paths:
        prog = QASM2(qasm2.main).loadfile(file=path)

        """
        reinterpret into Bloqade's parallelization-friendly intermediate representation. 
        Similar behaviour could have been obtained by just using qasm2.extended above
        """
        QASM2Py(prog.dialects)(prog)
        prog = prog.similar(qasm2.extended)

        programs[Path(path).stem] = prog
        print(f"→ {path} parsed & lowered: {prog}")

    return programs

# helper to go from Method → Qiskit
def circuit_to_qiskit(method: ir.Method) -> QuantumCircuit:
    # emit OpenQASM2 text
    qasm = QASM2Target(allow_parallel=False).emit_str(method)

    # parse into a Qiskit circuit
    return QuantumCircuit.from_qasm_str(qasm)


def QiskitDrawNotebook(qc):
    fig = qc.draw(output="mpl", fold=120, scale=0.7)
    display(fig)


# def show_circuit(circ):
#     # disegna il circuito e ottieni la figura
#     fig = circ.draw(output='mpl', scale=1.0)

#     # prova a massimizzare, ma non rompere se non c'è finestra GUI
#     try:
#         mgr = plt.get_current_fig_manager()
#         mgr.window.showMaximized()
#     except Exception:
#         pass

#     # mostra la figura
#     plt.show()
