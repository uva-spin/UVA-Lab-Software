def riemman_sum(signal, signal_fraction):
    """
    Perform Riemann sum of the signal
    """
    x_fraction = int(signal_fraction * len(signal))
    data =  signal[x_fraction:len(signal)-x_fraction]
    return data.sum()

