'''PyNMR, J.Maxwell 2020
'''
import numpy as np
from scipy import optimize
from lmfit import Model
from app.deuteron_fits import DFits


def area_signal_analysis(freq_list, phase, basesweep, wings, poly, sum_range):
    """Perform standard area subtraction analysis, including baseline subtraction, poly fit and subtraction and are sum in range

    Arguments:
        freq_list: frequency list
        phase: raw phase signal
        basesweep: baseline signal
        wings: list of 4 numbers 0 to 1 defining fit wings
        poly: polynomial function to use for polyfit subtraction
        sum_range: list of 2 numbers 0 to 1 defining sum range

    Returns:
        curves used, area
    """

    result = {}
    result['basesub'] = standard_baseline(phase, basesweep)
    result['polyfit'], result['fitsub'] = poly_fit_sub(result['basesub'], freq_list, wings, poly)
    result['final_curve'], result['area'] = signal_sum_range(result['fitsub'], sum_range)

    return result


def peak_fit_signal_analysis(freq_list, phase, basesweep, wings, poly, params):
    """Perform deuteron peak fit analysis, including baseline subtraction, poly fit and peak fit

    Arguments:
        freq_list: frequency list
        phase: raw phase signal
        basesweep: baseline signal
        wings: list of 4 numbers 0 to 1 defining fit wings
        range: list of 2 numbers 0 to 1 defining sum range
        poly: polynomial function to use
        params: d fit param dictionary

    Returns:
        curve used, polarization
    """
    result = {}
    result['basesub'] = standard_baseline(phase, basesweep)
    result['polyfit'], result['fitsub'] = poly_fit_sub(result['basesub'], freq_list, wings, poly)
    result['fit'], result['pol'], result['cc'] = d_fit(result['fitsub'], freq_list, params)

    return result


def standard_baseline(phase, basesweep):  # pass event.phase and base_event.basesweep
    return phase - basesweep


def poly_fit_sub(basesub, freq_list, wings, poly): # pass event.: basesub, freq_list, wings and poly method
    """
    wings: 4 numbers determining fit wings from 0 to 1
    poly: polynomial function as method
    """
    pi = [0.01, 0.8, 0.01, 0.001, 0.00001, 0.00001, 0.00001, 0.00001, 0.00001]

    sweep = basesub
    freqs = freq_list
    bounds = [x * len(sweep) for x in wings]
    data = [z for x, z in enumerate(zip(freqs, sweep)) if (bounds[0] < x < bounds[1] or bounds[2] < x < bounds[3])]
    #print(data)
    X = np.array([x for x, y in data])
    Y = np.array([y for x, y in data])
    try:
        pf, pcov = optimize.curve_fit(poly, X, Y, p0=pi)
        pstd = np.sqrt(np.diag(pcov))
    except RuntimeError:
        pf = [0,0,0,0,0,0,0,0,0,0]
        print("RuntimeError!")
        pass
    fit = poly(freqs, *pf)
    sub = sweep - fit

    area = sub.sum()

    residuals = Y - poly(X, *pf)
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((Y - np.mean(Y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot else 0
    return fit, sub

def poly2(x, *p):
    return p[0] + p[1] * x + p[2] * np.power(x, 2)

def poly3(x, *p):
    return p[0] + p[1] * x + p[2] * np.power(x, 2) + p[3] * np.power(x, 3)

def poly4(x, *p):
    return p[0] + p[1] * x + p[2] * np.power(x, 2) + p[3] * np.power(x, 3) + p[4] * np.power(x, 4)


def signal_sum_range(fitsub, sum_range):
    """Perform standard polyfit baseline subtraction

    Arguments:
        fitsub: polyfit subtracted signal
        sum_range: 2 numbers between 0 and 1 giving range to sum between

    Returns:
        curve used, area
    """

    sweep = fitsub
    bounds = [x * len(sweep) for x in sum_range]
    #print(sweep)
    data = [(x, y) if bounds[0] < x < bounds[1] else (x, 0) for x, y in enumerate(sweep)]
    Y = np.array([y for x, y in data])
    area = Y.sum()
    #pol = area * event.cc
    return Y, area


def d_fit(fitsub, freq_list, params):
    """Perform Dueteron fit and calculate polarization

    Arguments:
        fitsub: poly subtracted signal
        freq_list: frequency list
        params: fit parameters

    Returns:
        fit, resulting r asymmetry (instead of area) and polarization
    """

    sweep = fitsub
    freqs = freq_list
    print("Starting D fit")

    #labels = [e.text() for e in self.param_label]
    #values = [float(e.text()) for e in self.param_edit]
    #self.params = dict(zip(labels, values))

    res = DFits(freqs, sweep, params)

    r = res.result.params['r'].value
    fit = res.result.best_fit
    if res.result.success:  # if successful, set these params for next time
        params = res.result.params.valuesdict()

    pol = (r * r - 1) / (r * r + r + 1)
    area = fit.sum()
    cc = pol / area
    text = '\n'
    i = 0
    for name, param in res.result.params.items():
        i += 1
        print(f"{name} {param.value:.3f}\t")
        text = text + f"{name}: {param.value:.3f}\t"
        if i == 4:
            text = text + "\n"
    #self.message.setText(f"Polarization: {pol * 100:.4f}%, Area:  {area:.4f}, CC:  {cc:.4f}\n {text}")
    print("Finished D fit")
    return fit, pol, cc
