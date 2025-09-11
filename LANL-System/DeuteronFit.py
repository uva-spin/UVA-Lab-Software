import scipy.optimize as optimize
import numpy as np
import matplotlib.pyplot as plt
import lmfit as lm


def fit(ND3, data, init_params, plot=False):
    freqs = data[:, 0]
    y = data[:, 1]
    params = lm.Parameters()
    params.add('A', value=init_params['A'])
    params.add('G', value=init_params['G'])
    params.add('P', value=init_params['P'])
    params.add('wQ', value=init_params['wQ'])
    params.add('wL', value=init_params['wL'])
    params.add('eta', value=init_params['eta'])
    params.add('xi', value=init_params['xi'])
    result = lm.minimize(ND3, params.valuesdict(), args=(freqs, y), method='nelder')
    return result


def ND3(params, freqs, y):
    '''Deuteron lineshape function without fitting
    
    Args:
        freqs: array of frequency points (X axis)
        y: array of data points (Y axis)
        params: dictionary of parameters
        A: amplitude parameter
        G: scaling parameter  
        P: polarization parameter (0 to 1)
        wQ: quadrupole frequency
        wL: Larmor frequency
        eta: asymmetry parameter
        xi: false asymmetry parameter
        
    Returns:
        array of lineshape values
    '''
    A = params['A']
    G = params['G']
    P = params['P']
    wQ = params['wQ']
    wL = params['wL']
    eta = params['eta']
    xi = params['xi']

    def Iplus(P, Q, R):
        '''Returns: II'''
        r = (np.sqrt(4-3*P**(2))+P)/(2-2*P)
        r3QR = np.power(r, -3 * Q * R)
        NN = r * (r + r3QR) + 1
        II = r * (r - r3QR) / NN
        return II
    
    def Iminus(P, Q, R):
        '''Returns: II'''
        r = (np.sqrt(4-3*P**(2))+P)/(2-2*P)
        r3QR = np.power(r, 3 * Q * R)
        NN = r * (r + r3QR) + 1
        II = (r * r3QR - 1) / NN
        return II
    
    def Integrals(R, A, eps, Y2, etac2p):
        ''' Returns: ans1, ans2, ans3, ans4'''
        Y = np.sqrt(Y2)
        Yx2 = 2 * Y
        z2 = 1 - eps * R - etac2p
        A2 = A * A
        q4 = z2 * z2 + A2
        q2 = np.sqrt(q4)
        qq = np.sqrt(q2)

        cosa = z2 / q2
        cosa_2 = 1 / np.sqrt(2) * np.sqrt(1 + cosa)
        sina_2 = 1 / np.sqrt(2) * np.sqrt(1 - cosa)

        fTmp = Y2 + q2
        fVal = Yx2 * qq * cosa_2

        La = 0.5 * sina_2 * np.log((fTmp + fVal) / (fTmp - fVal))
        Ta = cosa_2 * (np.pi / 2 + np.arctan((Y2 - q2) / (Yx2 * qq * sina_2)))
        Arg = (Y2 * (Y2 - 2 * z2) + q4)

        ans1 = (Ta + La) / (2 * qq * A)
        ans2 = (Ta - La) * qq / (2 * A)
        ans3 = z2 * (ans2) + (2 * A2 + q4) * (ans1) + (Y / Arg) * (Y2 * z2 + 2 * A2 - q4)
        ans4 = ((Y / Arg) * (Y2 - z2) + z2 * (ans1) + (ans2)) / (4 * A2)

        return ans1, ans2, ans3, ans4
    
    def FandDerivs(R, A, eps, eta):
        '''Returns FF'''
        if eta < 0.001:
            Y2 = 3
            I1, I2, I3, I4 = Integrals(R, A, eps, Y2, 0)
            FF = I1 * A
        else:
            Y2 = 3
            I1, I2, I3, I4 = Integrals(R, A, eps, Y2, 0)
            FF = 0
            eRm1 = 1 - eps * R
            dphi = 1

            for i in (0, 1):
                c2p = np.cos(np.pi * dphi * i)
                ec2p = eta * c2p
                Y2 = 3 - ec2p
                Y = np.sqrt(Y2)
                z2 = eRm1 - ec2p

                I1, I2, I3, I4 = Integrals(R, A, eps, Y2, 0)

                fac = 0.5 * np.sqrt(3) / Y
                FF += fac * I1 * A

            order = 5
            for N in [np.power(2, n) for n in range(2, order + 1)]:
                dphi = 1 / N

                for i in range(N - 1, 0, -2):
                    c2p = np.cos(np.pi * dphi * i)
                    ec2p = eta * c2p

                    Y2 = 3 - ec2p
                    Y = np.sqrt(Y2)
                    z2 = eRm1 - ec2p

                    I1, I2, I3, I4 = Integrals(R, A, eps, Y2, ec2p)

                    fac = np.sqrt(3) / Y
                    FF += fac * I1 * A

            FF = dphi * FF

        return FF
    
    result = []
    for w in freqs:
        R = (w - wL) / (3 * wQ)

        Ip = Iplus(P, wQ / wL, R)
        Im = Iminus(P, wQ / wL, R)

        Fm = FandDerivs(R, A, -1, eta)
        Fp = FandDerivs(R, A, 1, eta)

        Fm /= wQ
        Fp /= wQ

        F = G * (Im * Fm + Ip * Fp)  # Lineshape

        fAsym = 1 + 0.5 * xi * (1 + R)  # False Asymmetry xi
        bg = 0  # background

        y = fAsym * F + bg  # total
        result.append(y)
    
    return np.array(result)
