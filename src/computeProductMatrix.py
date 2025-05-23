def computeProductMatrix(theta1, phi1, lam1, theta2, phi2, lam2):

    import cmath
    import math

    # # your angles in radians
    # theta1 = math.pi
    # phi1   = 0
    # lam1   = math.pi/8

    # theta2 = 0
    # phi2   = math.pi/2
    # lam2   = math.pi/2

    # build the entries
    a00 = math.cos(theta1/2)
    a01 = -cmath.exp(1j * lam1) * math.sin(theta1/2)
    a10 =  cmath.exp(1j * phi1) * math.sin(theta1/2)
    a11 =  cmath.exp(1j * (phi1 + lam1)) * math.cos(theta1/2)

    b00 = math.cos(theta2/2)
    b01 = -cmath.exp(1j * lam2) * math.sin(theta2/2)
    b10 =  cmath.exp(1j * phi2) * math.sin(theta2/2)
    b11 =  cmath.exp(1j * (phi2 + lam2)) * math.cos(theta2/2)


    c00 = a00*b00 + a01*b10
    c01 = a00*b10 + a01*b11
    c10 = a10*b00 + a11*b10
    c11 = a10*b01 + a11*b11

    # Why do this twice?
    c00 = a00*b00 + a01*b10 
    c01 = a00*b10 + a01*b11
    c10 = a10*b00 + a11*b10
    c11 = a10*b01 + a11*b11

    # globPhase = -cmath.phase(c00)
    # c01 *= cmath.exp(globPhase*1j)
    # c10 *= cmath.exp(globPhase*1j)
    # c11 *= cmath.exp(globPhase*1j)

    theta3 = 2*cmath.acos(c00)
    sinTheta3 = cmath.sin(theta3/2)
    if sinTheta3 != 0: 
        phi3 = cmath.phase(c10/sinTheta3)
        lam3 = cmath.phase(-c01/sinTheta3)
    else:
        sum_phi_lam3 = cmath.phase(c11/cmath.cos(theta3/2))
        phi3 = 0.0
        lam3 = sum_phi_lam3


    # print(theta3) # Issue! theta is COMPLEX, I need REAL angle
    # print(phi3)
    # print(lam3)

    return(theta3, phi3, lam3)