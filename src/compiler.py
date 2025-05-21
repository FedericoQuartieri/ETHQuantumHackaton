import utils
from utils import sep_print
import sys, os

import passes
import metrics
from validate import validate
from kirin.ir.method import Method

from bloqade.qasm2.emit import QASM2 as QASM2Target # the QASM2 target
from bloqade.qasm2.parse import pprint # the QASM2 pretty printer

prettyDebug = False  # if true print the QASM-style circuits at each optimization step
printSSA = False    # if true prints the raw IR of kirin
printMetrics = False
doPause = False     # if true pauses until input at each step

doRydberg = True    # if true translates gates to the native set using the native rewrite pass
doNativeParallelisation = True  # if true applies the parallelisation with native UOpToParallelise

doOurPasses = True         # if true apply our passes also outside the merge
doOurPasses_merge = True    # if true apply the merge pass

validateExecute = True
executeShots = 100000

def main():
    if len(sys.argv) < 3:
        print("Usage: py compiler.py <input_folder> <output_folder>")
        print("The program will optimize all circuits in .qasm files in the input folder, then output the optimized version in the output folder.")
        exit(-1)

    input_folder = sys.argv[1]
    output_folder = sys.argv[2]

    if not output_folder.endswith("/"):
        output_folder += "/"

    programs = utils.importQASM(input_folder)
    for name, circuit in programs.items():
        #if not "2" in name: continue

        optimize_qasm(circuit, output_folder, name+".qasm")
        if name.endswith("_improved"):
            orgName = name.split("_")[0]
            qcOrg = utils.circuit_to_qiskit(programs[orgName])
            qcImprov = utils.circuit_to_qiskit(circuit)
            print(f"Validating {name} against its original version...")
            if orgName == "1":
                validate(qcOrg, qcImprov, ancilla=True, execute=validateExecute, shots=executeShots)
            else: 
                validate(qcOrg, qcImprov, ancilla=False, execute=validateExecute, shots=executeShots)
        print()
    

def optimize_qasm(circuit: Method, output_folder, output_name):
    # `programs` holds each file’s lowered IR under its filename-stem.

    # 1 is good
    # 2 is bad also with NOTHING (even just with RydbergRewrite)
    # 3 is bad with UToOpParallelise (commenting  nativeParallelise and with our passes brings to 1 fidelity)
    # 4 is perfect
    # 4_improved is perfect 

    ###################################
    # The following flags govern the execution flow.

    targetParallel = QASM2Target(allow_parallel=True)
    targetSequential = QASM2Target(allow_parallel=False)

    if prettyDebug:
        sep_print("Non-translated qasm:\n")
        pprint(targetParallel.emit(circuit))

    ###########################################################################

    qc_initial = utils.circuit_to_qiskit(circuit)

    if doRydberg:
        passes.RydbergRewrite(circuit)
        if printMetrics: 
            sep_print("Metrics after RydbergRewrite: ")
            metrics.print_gate_counts(targetParallel.emit(circuit))

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
        if printMetrics: 
            sep_print("Metrics before MERGE: ")
            metrics.print_gate_counts(targetParallel.emit(circuit))

        print("Merging ConsecutiveU")
        passes.MergeConsecutiveU(circuit.dialects)(circuit)

        if printMetrics: 
            sep_print("Metrics after MERGE: ")
            metrics.print_gate_counts(targetParallel.emit(circuit))
    if printSSA:
        print("circuit after MERGE: ")
        circuit.print()
        print()
    if doPause:
        input("Continue...")


    if prettyDebug:
        sep_print("Unparallelized QASMTarget:", sleepTimeSec=1)
        pprint(targetParallel.emit(circuit))

    # Now apply parallelization with native UOpToParallelise
    if doNativeParallelisation:
        passes.NativeParallelisationPass(circuit)
        if printMetrics: 
            sep_print("Metrics after nativeParallelise: ")          # gate count (parallel and standard) is output at each pass 
            metrics.print_gate_counts(targetParallel.emit(circuit))

    if prettyDebug:
        sep_print("NativeParallelised circuit: ", sleepTimeSec=2)
        pprint(targetSequential.emit(circuit))

    
    if printSSA:
        circuit.print()
    
    if printMetrics: 
        print("Final metrics: ")
        metrics.print_gate_counts(targetParallel.emit(circuit))

    # Next output validation metrics
    qc_final = utils.circuit_to_qiskit(circuit)

    validate(qc_initial, qc_final, ancilla=False, execute=validateExecute, shots=executeShots)

    filepath = output_folder + output_name   # Output file to qasm
    print("Exporting to QASM... ", filepath)
    with open(filepath, "w") as out:
        out.write(targetSequential.emit_str(circuit))
    

if __name__ == "__main__":
    main()
