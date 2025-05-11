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

if __name__ == "__main__":
    programs = utils.importQASM()
    # `programs` holds each file’s lowered IR under its filename-stem.

    # 1 is good
    # 2 is bad also with NOTHING (even just with RydbergRewrite)
    # 3 is bad with UToOpParallelise (commenting  nativeParallelise and with our passes brings to 1 fidelity)
    # 4 is perfect
    # 4_improved is perfect 
    output_name = "1"    # name of the circuit to be compiled-optimized       

    ###################################
    # The following flags govern the execution flow.

    prettyDebug = False  # if true print the QASM-style circuits at each optimization step
    printSSA = False    # if true prints the raw IR of kirin
    doPause = False     # if true pauses until input at each step

    doRydberg = True    # if true translates gates to the native set using the native rewrite pass
    doNativeParallelisation = True  # if true applies the parallelisation with native UOpToParallelise

    doOurPasses = False         # if true apply our passes also outside the merge
    doOurPasses_merge = True    # if true apply the merge pass

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

    # Our first pass: remove 2pi rotations and useless U gates
    if doOurPasses:
        print("Doing Remove2PiGates Pass after RydbergRewrite...")
        passes.Remove2PiGates(circuit.dialects)(circuit)
    if printSSA:
        circuit.print()
    if doPause:
        input("Continue...")

    # Our second and bigger pass: merge U gates wherever possible to reduce their total count
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

    # Now apply parallelization with native UOpToParallelise
    if doNativeParallelisation:
        passes.NativeParallelisationPass(circuit)
        print("Metrics after nativeParallelise: ")          # gate count (parallel and standard) is output at each pass 
        metrics.print_gate_counts(target.emit(circuit))

    if prettyDebug:
        sep_print("NativeParallelised circuit: ", sleepTimeSec=2)
        pprint(QASM2Target(allow_parallel=False).emit(circuit))

    
    if printSSA:
        circuit.print()

    # Next output validation metrics
    qc_final = utils.circuit_to_qiskit(circuit)

    fidelity = validate(qc_initial, qc_final)

    filepath = f"../out_compiler/{output_name}.qasm"                # Output file to qasm
    print("Exporting to QASM... ", filepath)
    with open(filepath, "w") as out:
        out.write(target.emit_str(circuit))
        