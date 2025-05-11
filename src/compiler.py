import utils
from utils import sep_print

import passes
import metrics
from validate import validate
from kirin.ir.method import Method

from bloqade import qasm2
from bloqade.qasm2.parse.lowering import QASM2
from bloqade.qasm2.passes import QASM2Py
from bloqade.qasm2.emit import QASM2 as QASM2Target # the QASM2 target
from bloqade.qasm2.parse import pprint # the QASM2 pretty printer

programs = utils.importQASM()
# `programs` now holds each file’s lowered IR under its filename-stem.

output_name = "4_improved"           
# 1 is good
# 2 is bad also with NOTHING (even just with RydbergRewrite)
# 3 is bad with UToOpParallelise (commenting  nativeParallelise and with our passes brings to 1 fidelity)
# 4 is perfect
# 4_improved is perfect 

prettyDebug = False
printSSA = False
doPause = False

doRydberg = True
doNativeParallelisation = True

doOurPasses = False
doOurPasses_merge = True

target = QASM2Target(allow_parallel=True)
program_ast = target.emit(programs[output_name])

if prettyDebug:
    sep_print("Non-translated qasm:\n")
    pprint(program_ast)

###########################################################################


circuit: Method = programs[output_name]

qc_initial = utils.circuit_to_qiskit(circuit)

if doRydberg:
    passes.RydbergRewrite(circuit)

print("Metrics after RydbergRewrite: ")
metrics.print_gate_counts(target.emit(circuit))

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


if doOurPasses_merge:
    print("Metrics before MERGE: ")
    metrics.print_gate_counts(target.emit(circuit))

    print("Merging ConsecutiveU")
    passes.MergeConsecutiveU(circuit.dialects)(circuit)

    print("Metrics after MERGE: ")
    metrics.print_gate_counts(target.emit(circuit))
if printSSA:
    print("circuit after MERGE: ")
    circuit.print()
    print()
if doPause:
    input("Continue...")


if prettyDebug:
    sep_print("Unparallelized QASMTarget:", sleepTimeSec=1)
    pprint(target.emit(circuit))

# Now apply parallelization
if doNativeParallelisation:
    passes.NativeParallelisationPass(circuit)
    print("Metrics after nativeParallelise: ")
    metrics.print_gate_counts(target.emit(circuit))

if prettyDebug:
    sep_print("NativeParallelised circuit: ", sleepTimeSec=2)
    pprint(QASM2Target(allow_parallel=False).emit(circuit))

# Next output metrics


if printSSA:
    circuit.print()

qc_final = utils.circuit_to_qiskit(circuit)

fidelity = validate(qc_initial, qc_final)

if fidelity > 0.8 or True:
    filepath = f"../out_compiler/{output_name}.qasm" 
    print("Fidelity high enough. Exporting to QASM ", filepath)
    with open(filepath, "w") as out:
        out.write(QASM2Target(allow_parallel=False).emit_str(circuit))
else:
    print("Fidelity TOO LOW! Not exporting QASM")
    

if __name__ == "__main__":
    pass