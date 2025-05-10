from pathlib import Path
from time import sleep
from typing import Any

from bloqade import qasm2
from bloqade.qasm2.parse.lowering import QASM2
from bloqade.qasm2.passes import QASM2Py

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

def importQASM() -> dict[str, Any]:
    # path to root is launched from
    project_root = Path.cwd().parent  

    # now build a path to .qasm files
    qasm_dir   = project_root / "assets/baseline"
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
    qasm = QASM2().emit_str(method)
    # parse into a Qiskit circuit
    return QuantumCircuit.from_qasm_str(qasm)