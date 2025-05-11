import qiskit.circuit.library as qLib

theta = 1
phi = 2
lam = 3.14

u3 = qLib.U3Gate(theta, phi, lam)

decomp = u3.decompositions

for d in decomp:
    print(d, type(d))

"""


parallel CZ: 3
parallel U: 18
other U: 224
other CZ: 30


"""