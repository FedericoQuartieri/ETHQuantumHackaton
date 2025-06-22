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

# TODO: CNOT Ladder to log (use ancilla qubits => HARD)

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
from bloqade.qasm2.dialects import core, uop, parallel
from kirin.dialects import py as pyDialect

from computeProductMatrix import computeProductMatrix

@dataclass
class Remove2PiGates(Pass):

    def unsafe_run(self, method: ir.Method):
        result = Walk(Simplify2PiConst()).rewrite(method.code)

        frame, _ = const.Propagate(self.dialects).run_analysis(method)
        result = Walk(WrapConst(frame)).rewrite(method.code).join(result)
        result = Walk(FindAndSimplifyUGates()).rewrite(method.code).join(result)
        
        rule = Chain(
            ConstantFold(),
            DeadCodeElimination(),
            CommonSubexpressionElimination(),
        )
        result = Fixpoint(Walk(rule)).rewrite(method.code).join(result)
        
        return result

@dataclass
class Simplify2PiConst(RewriteRule):
    eps: float = 1e-11 # IMPORTANT! Not all constants are 100% accurate on 2pi
    def mod(self, a, b):
        if a < b:
            b -= self.eps
        return (a // b) * b
    
    def rewrite_Statement(self, node: ir.Statement) -> RewriteResult:
        if not isinstance(node, pyDialect.Constant):
            return RewriteResult()
        
        periodicity = 2*math.pi
        # Search for uses as theta
        for use in node.result.uses:
            stmt = use.stmt
            if isinstance(stmt, uop.UGate):
                if(stmt.theta == node.result):
                    periodicity = 4*math.pi

        if abs(node.value.unwrap()) < periodicity-self.eps:
            return RewriteResult()

        used_in_U = False
        uses = node.result.uses
        for use in uses:
            if isinstance(use.stmt, uop.UGate):
                used_in_U = True
                break

        if used_in_U:        
            newVal = node.value.unwrap() - self.mod(node.value.unwrap(), periodicity)
            if newVal < 1e-10:
                newVal = 0.0
            # print(f"From {node.value.unwrap()} to {newVal}")
            newStmt = pyDialect.Constant(newVal)
            # print(newStmt.print_str())
            node.replace_by(newStmt)
            return RewriteResult(has_done_something=True)
        
        return RewriteResult()

@dataclass
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

@dataclass
class MergeConsecutiveU(Pass):
    def unsafe_run(self, method: ir.Method):
        print("Running unsafe run MergeConsecutiveU")

        result = Fixpoint(Walk(CommonSubexpressionElimination())).rewrite(method.code)

        loop_res = RewriteResult(has_done_something=True)
        while loop_res.has_done_something:
            frame, _ = const.Propagate(self.dialects).run_analysis(method)
            Walk(WrapConst(frame)).rewrite(method.code)#.join(result)
            loop_res = Walk(UniteU3()).rewrite(method.code)
            
        result = Walk(Simplify2PiConst()).rewrite(method.code)#.join(result)
        frame, _ = const.Propagate(self.dialects).run_analysis(method)
        result = Walk(WrapConst(frame)).rewrite(method.code)# .join(result)
        result = Walk(FindAndSimplifyUGates()).rewrite(method.code).join(result)

        rule = Chain(
            ConstantFold(),
            DeadCodeElimination(),
            CommonSubexpressionElimination(),
        )
        result = Fixpoint(Walk(rule)).rewrite(method.code).join(result)
        return result
    
    
@dataclass
class UniteU3(RewriteRule):
    def rewrite_Statement(self, node: ir.Statement) -> RewriteResult:
        if not isinstance(node, uop.UGate):
            return RewriteResult()

        # scan for the very next U on the same qubit
        in_q = node.args[0]
        scan = node.next_stmt
        partner = None
        while scan:
            if in_q in scan.args:
                if isinstance(scan, uop.UGate):
                    partner = scan
                break
            scan = scan.next_stmt
        if partner is None:
            return RewriteResult()

        # pull out the old angles
        θ1,φ1,λ1 = (node.theta.hints["const"].data,
                    node.phi.  hints["const"].data,
                    node.lam.  hints["const"].data)
        θ2,φ2,λ2 = (partner.theta.hints["const"].data,
                    partner.phi.  hints["const"].data,
                    partner.lam.  hints["const"].data)

        # compute the fused triple
        newθ, newφ, newλ = computeProductMatrix(θ1,φ1,λ1, θ2,φ2,λ2)

        # — now do one atomic replacement —
        # 1) build the new Constant stmts
        cθ = pyDialect.Constant(newθ.real)
        cφ = pyDialect.Constant(newφ)
        cλ = pyDialect.Constant(newλ)
        # 2) insert them BEFORE the old node so they dominate it
        cθ.insert_before(node)
        cφ.insert_before(node)
        cλ.insert_before(node)
        # 3) build your merged UGate
        merged = uop.UGate(in_q, cθ.result, cφ.result, cλ.result)
        # 4) splice it in, nuking the old node
        node.replace_by(merged)
        # 5) delete the partner
        partner.delete()

        return RewriteResult(has_done_something=True)