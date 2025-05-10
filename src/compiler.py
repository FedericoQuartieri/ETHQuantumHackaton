import utils
from utils import sep_print

import passes
import metrics

from bloqade import qasm2
from bloqade.qasm2.parse.lowering import QASM2
from bloqade.qasm2.passes import QASM2Py
from bloqade.qasm2.emit import QASM2 as QASM2Target # the QASM2 target
from bloqade.qasm2.parse import pprint # the QASM2 pretty printer

programs = utils.importQASM()
# `programs` now holds each file’s lowered IR under its filename-stem.

output_name = "1"
prettyDebug = False

target = QASM2Target(allow_parallel=True)
program_ast = target.emit(programs[output_name])

if prettyDebug:
    sep_print("Non-translated qasm:\n")
    pprint(program_ast)

###########################################################################

circuit = programs[output_name]

passes.RydbergRewrite(circuit)

if prettyDebug:
    sep_print("Unparallelized QASMTarget:", sleepTimeSec=1)
    pprint(target.emit(circuit))

# Now apply parallelization
passes.NativeParallelisationPass(circuit)

if prettyDebug:
    sep_print("NativeParallelised circuit: ", sleepTimeSec=2)
    pprint(target.emit(circuit))

# Next output metrics

metrics.print_gate_counts(target.emit(circuit))

qc = utils.circuit_to_qiskit(circuit)

fig = qc.draw(output="mpl", fold=120, scale=0.7)
# display(fig)   # in a Jupyter notebook

if __name__ == "__main__":
    pass