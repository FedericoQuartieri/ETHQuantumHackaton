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

output_name = "2"
prettyDebug = False
printSSA = False
doPause = False

doOurPasses = True

target = QASM2Target(allow_parallel=True)
program_ast = target.emit(programs[output_name])

if prettyDebug:
    sep_print("Non-translated qasm:\n")
    pprint(program_ast)

###########################################################################

from kirin.ir.method import Method

circuit: Method = programs[output_name]

# if printSSA:
#     circuit.print()
# pprint(target.emit(circuit))

if doOurPasses:
    print("Doing Remove2PiGates Pass...")
    passes.Remove2PiGates(circuit.dialects)(circuit)
# if printSSA:
#     circuit.print()

if doPause:
    input("Continue...")

passes.RydbergRewrite(circuit)

if printSSA:
    print("After Rydberg: ")
    circuit.print()
if doOurPasses:
    print("Doing Remove2PiGates Pass after RydbergRewrite...")
    passes.Remove2PiGates(circuit.dialects)(circuit)
if printSSA:
    circuit.print()
if doPause:
    input("Continue...")

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
if printSSA:
    circuit.print()

ans = input("Print SSA? ")
if ans == "y":
    circuit.print()

""""
Hi, I tried to reinstall a python env with 3.12 and reinstalled the packages and it seems to be in a better state
When I run pyqrack I get this 
IMPORTANT: Did you remember to install OpenCL, if your Qrack version was built with OpenCL?

Since running pip install with other pyqrack packages was problematic, I'm thinking of installing OpenCL, how can I do that so the current
"""



if __name__ == "__main__":
    pass