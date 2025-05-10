from bloqade import qasm2
from bloqade.qasm2.parse.lowering import QASM2
from bloqade.qasm2.passes import QASM2Py
from bloqade.qasm2.emit import QASM2 # the QASM2 target
from bloqade.qasm2.parse import pprint # the QASM2 pretty printer

from pathlib import Path

# path to wherever Jupyter is launched from
project_root = Path.cwd()  

# now build a path to .qasm files
qasm_dir   = project_root / "baseline"
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

# `programs` now holds each file’s lowered IR under its filename-stem.

target = QASM2(allow_parallel=True)
program_ast = target.emit(programs["0.4"])
pprint(program_ast)

input()

###########################################################################

import warnings
warnings.filterwarnings("ignore")

from bloqade.qasm2.rewrite.native_gates import RydbergGateSetRewriteRule
from kirin.rewrite import Walk


circuit = programs["0.4"]

Walk(RydbergGateSetRewriteRule(circuit.dialects)).rewrite(circuit.code);

if __name__ == "__main__":
    pass