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

# LynxFoudnation ; BIP ; E4 ; CRS4

# Find some parallelisable structures

# TODO: Many Analysis passes (find parallelisable structures: one pass per structure)
#       Rewrite pass to substitute the structure with the parallel version

# TODO: Pass that substitutes localGate on > 1/2 qubits with 1 global + 1 local inverse on < 1/2 qubits 

# TODO: !!! Merge successive U3 (sum the angles?? Prob not) (Do the math here)

# TODO: CNOT Ladder to log (use ancilla qubits)
from dataclasses import field, dataclass
import math

from kirin.passes import Pass, Fold

from kirin.rewrite.abc import RewriteRule, RewriteResult
from kirin.rewrite import (
    WrapConst, Walk, 
    Chain, ConstantFold, 
    Fixpoint, DeadCodeElimination, 
    CommonSubexpressionElimination
)
from bloqade.qasm2.rewrite import RaiseRegisterRule

from kirin import ir
from kirin.analysis import const
from bloqade.qasm2.dialects import core, uop
from kirin.dialects import py as pyDialect

@dataclass
class Remove2PiGates(Pass):

    def unsafe_run(self, method: ir.Method):
        print("Running unsafe run 2PIGAtes")
        # result = Walk(RaiseRegisterRule()).rewrite(method.code)

        result = Walk(Chain(
                        Simplify2PiConst()
                        )).rewrite(method.code)#.join(result)

        frame, _ = const.Propagate(self.dialects).run_analysis(method)
        result = Walk(WrapConst(frame)).rewrite(method.code)# .join(result)
        result = Walk(FindAndSimplifyUGates()).rewrite(method.code).join(result)

        # result = Fixpoint(Walk(ConstantFold())).rewrite(method.code).join(result)
        
        rule = Chain(
            ConstantFold(),
            DeadCodeElimination(),
            CommonSubexpressionElimination(),
        )
        result = Fixpoint(Walk(rule)).rewrite(method.code).join(result)
        
        return result

@dataclass
class Simplify2PiConst(RewriteRule):
    eps: float = 1e-10
    def mod(self, a, b):
        if a < b:
            b -= self.eps
        return (a // b) * b
    
    def rewrite_Statement(self, node: ir.Statement) -> RewriteResult:
        if not isinstance(node, pyDialect.Constant):
            return RewriteResult()
        if abs(node.value.unwrap()) < 2*math.pi - self.eps:
            return RewriteResult()
        
        #Not done on 6.28318530717958

        used_in_U = False
        uses = node.result.uses
        for use in uses:
            if isinstance(use.stmt, uop.UGate):
                used_in_U = True
                break

        if used_in_U:        
            newVal = node.value.unwrap() - self.mod(node.value.unwrap(), 2*math.pi)
            if newVal < 1e-10:
                newVal = 0.0
            print(f"From {node.value.unwrap()} to {newVal}")
            newStmt = pyDialect.Constant(newVal)
            print(newStmt.print_str())
            node.replace_by(newStmt)
            return RewriteResult(has_done_something=True)
        
        return RewriteResult()

class FindAndSimplifyUGates(RewriteRule):
    def rewrite_Statement(self, node: ir.Statement) -> RewriteResult:
        if not isinstance(node, uop.UGate):
            return RewriteResult()
        
        # we know node is UGate 
        theta = node.theta.hints["const"].data
        phi = node.phi.hints["const"].data
        lam = node.lam.hints["const"].data

        if theta != 0 or phi != 0 or lam != 0:
            return RewriteResult()
        
        node.delete()
        return RewriteResult(has_done_something=True)


