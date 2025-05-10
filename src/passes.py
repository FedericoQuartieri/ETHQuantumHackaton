from bloqade import qasm2
from bloqade.qasm2.passes import UOpToParallel

import warnings
warnings.filterwarnings("ignore")

from bloqade.qasm2.rewrite.native_gates import RydbergGateSetRewriteRule
from kirin.rewrite import Walk

def RydbergRewrite(circuit):
    """
    Applies rewrites in-place on the circuit
    @returns nothing
    """
    Walk(RydbergGateSetRewriteRule(circuit.dialects)).rewrite(circuit.code)

def NativeParallelisationPass(circuit):
    """
    Applies rewrites in-place on the circuit
    @returns nothing
    """
    UOpToParallel(circuit.dialects)(circuit)
