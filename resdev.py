import eseries as es
from engineering_notation import EngNumber

"""
This module helps to select resistor values for voltage dividers

In the simplest case, the devider is made up of two resistors. R1 and R2, where
one R1 terminal is connected to Vin and the node between R1 and R2 is Vout.

"""
def resdiv_r1(Vin, Vout, R2):
    """
    Calculate the exact value of R1 with R2 given.
    """
    return R2 * (Vin/Vout - 1)

def resdiv_r2(Vin, Vout, R1):
    """
    Calculate the exact value of R1 with R2 given.
    """
    return R1 / (Vin/Vout - 1)

def resdev_vout(Vin, R1, R2):
    """
    Calculate Vout with given R1, R2 and Vin
    """
    return Vin * R2 / (R1 + R2)

def r1_p_r2(R1, R2):
    """
    Calculate the Resistance of a parallel connection
    """
    return R1 * R2 / (R1 + R2)

def resdev_rout(R1, R2):
    """
    Calculate the output resistance of the voltage devider
    """
    return r1_p_r2(R1, R2)

def calc_rp(R, Rp):
    """
    Calculate a parallel resistor to match R (R = Rp//Rx)
    """
    if R >= Rp : return None
    return R * Rp / (Rp - R)

def resdev_r1_r2(Vin, Vout, Rout_min = 1, Rout_max = 10, eser = es.E24):
    """
    Returns the best matchin resistor pair of (R1, R2) with a given output
    resistance range and E-Series
    """
    best_match_r2 = None
    best_match_r1 = None
    vdiv_err_best = Vin

    for r2 in es.erange(eser, Rout_min, Rout_max):
        r1 = es.find_nearest(eser, resdiv_r1(Vin, Vout, r2))
        rout = resdev_rout(r1, r2)
        if rout < Rout_min : continue
        if rout > Rout_max : break
        vdiv_err = abs(resdev_vout(Vin, r1, r2) - Vout)
        if vdiv_err < vdiv_err_best:
            vdiv_err_best = vdiv_err
            best_match_r1 = r1
            best_match_r2 = r2
            if vdiv_err_best == 0.0 : break

    return (best_match_r1, best_match_r2)

def resdev_r1_2r2(Vin, Vout, Rout_min = 1, Rout_max = 10, eser = es.E24):
    """
    Returns the best matching resistor combination of (R1, R2_1, R2_2)
    with a given output resistance range and E-Series.
    R2_1 and R2_2 are connected in parallel.
    """
    best_match_r2_1 = None
    best_match_r2_2 = None
    best_match_r1 = None
    vdiv_err_best = Vin

    for r2_1 in es.erange(eser, Rout_min, Rout_max * 2):
        if r2_1 == Rout_min or r2_1 == Rout_max : continue
        for r2_2 in es.erange(eser, calc_rp(Rout_min, r2_1), r2_1 * 1000):
            r2 = r2_1 * r2_2 / (r2_1 + r2_2)
            r1 = es.find_nearest(eser, resdiv_r1(Vin, Vout, r2))
            rout = resdev_rout(r1, r2)
            if rout < Rout_min : continue
            if rout > Rout_max : break
            vdiv_err = abs(resdev_vout(Vin, r1, r2) - Vout)
            if vdiv_err < vdiv_err_best:
                vdiv_err_best = vdiv_err
                best_match_r1 = r1
                best_match_r2_1 = r2_1
                best_match_r2_2 = r2_2

    return (best_match_r1, best_match_r2_1, best_match_r2_2)

def calc_resdev(Vin, Vout, Rout_min = 1, Rout_max = 10, Err_max = 1, eser = es.E24):
    R1, R2 = resdev_r1_r2(Vin, Vout, Rout_min, Rout_max, eser)
    err = resdev_vout(Vin, R1, R2) - Vout
    err_percent = abs(err)/Vout*100
    if err_percent <= Err_max:
        print("Resistor divider with two Resistors:")
        print("R1: {}, R2: {}".format(str(EngNumber(R1)), str(EngNumber(R2))))
        print("Vout error: {:.3f}% ({}V)".format(err_percent, str(EngNumber(err))))
        print("Output resistance: {}\n".format(str(EngNumber(resdev_rout(R1, R2)))))
    R1, R2_1, R2_2 = resdev_r1_2r2(Vin, Vout, Rout_min, Rout_max, eser)
    err = resdev_vout(Vin, R1, r1_p_r2(R2_1, R2_2)) - Vout
    err_percent = abs(err)/Vout*100
    if err_percent <= Err_max:
        print("Resistor divider with three Resistors:")
        print("R1: {}, R2: {}//{}".format(str(EngNumber(R1)), str(EngNumber(R2_1)), str(EngNumber(R2_2))))
        print("Vout error: {:.3f}% ({}V)".format(err_percent, str(EngNumber(err))))
        print("Output resistance: {}".format(str(EngNumber(resdev_rout(R1, r1_p_r2(R2_1, R2_2))))))
    else:
        print("Cannot find a solution for given parameters")