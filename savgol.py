#TEST1
#diccionarios de python
import pandas as pd
import numpy as np
from scipy.signal import savgol_filter

#funcion
def savitzky_golay_filtering(timeseries, wnds=[11, 7], orders=[2, 4], debug=True):
    interp_ts = pd.Series(timeseries)
    interp_ts = interp_ts.interpolate(method='linear', limit=14)
    smooth_ts = interp_ts
    wnd, order = wnds[0], orders[0]
    F = 1e8
    W = None
    it = 0
    while True:
        smoother_ts = savgol_filter(smooth_ts, window_length=wnd, polyorder=order)
        diff = smoother_ts - interp_ts
        sign = diff > 0
        if W is None:
            W = 1 - np.abs(diff) / np.max(np.abs(diff)) * sign
            wnd, order = wnds[1], orders[1]
        fitting_score = np.sum(np.abs(diff) * W)
        print it, ' : ', fitting_score
        if fitting_score > F:
            break
        else:
            F = fitting_score
            it += 1
        smooth_ts = smoother_ts * sign + interp_ts * (1 - sign)
    if debug:
        return smooth_ts, interp_ts
    return smooth_ts