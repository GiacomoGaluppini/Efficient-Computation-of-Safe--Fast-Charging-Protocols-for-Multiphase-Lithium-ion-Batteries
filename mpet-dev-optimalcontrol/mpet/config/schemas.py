# definition of config file sections, parameters, types

import ast
from distutils.util import strtobool

from schema import Schema, Use, Optional, And, Or
import numpy as np

from mpet.config import constants


def parse_segments(key):
    """
    Parse the segments key of the configuration file and
    validate it

    :param str key: The raw key from the config file
    :return: segments (tuple)
    """
    segments = ast.literal_eval(key)
    assert isinstance(segments, list), "segments must be a list"
    assert len(segments) > 0, "There must be at least one segment"
    for item in segments:
        assert (isinstance(item, tuple)) and (len(item) == 2), \
            "Each segment must be a tuple of (setpoint, time)"
    return segments


def check_allowed_values(value, allowed_values):
    """
    Check if value was chosen from a set of allowed values

    :param value: Value to verify
    :param list allowed_values: Possible values
    :return: True if value appears in allowed_values, else and AssertionError is raised
    """
    assert value in allowed_values, f"{value} is invalid, options are: {allowed_values}"
    # Schema needs a True return value if the check passes
    return True


def tobool(value):
    """
    Convert string value (y/yes/t/true/1/on, n/no/f/false/0/off) to boolean

    :param str value: Value to convert to bool
    :return: Boolean representation of value
    """
    assert isinstance(value, str), f"{value} must be a string"
    # strtobool returns 0 or 1, use bool() to convert to actual boolean type
    return bool(strtobool(value))


#: System parameters, per section
system = {'Sim Params': {'profileType': lambda x:
                         check_allowed_values(x, ["CC", "CV", "CP", "CCsegments", "CVsegments","BBcontrol"]),#GG
                         'Crate': Use(float),
                         Optional('power', default=None): Use(float),
                         Optional('1C_current_density', default=None): Use(float),
                         Optional('tramp', default=0.): Use(float),
                         'Vmax': Use(float),
                         'Vmin': Use(float),
                         'Vset': Use(float),
                         Optional('capFrac', default=1.0): Use(float),
                         'segments': Use(parse_segments),
                         Optional('prevDir', default=''): str,
                         'tend': And(Use(float), lambda x: x > 0),
                         'tsteps': And(Use(int), lambda x: x > 0),
                         'relTol': And(Use(float), lambda x: x > 0),
                         'absTol': And(Use(float), lambda x: x > 0),
                         'T0': Use(float),
                         Optional('nonisothermal', default=False): Use(tobool),
                         'randomSeed': Use(tobool),
                         Optional('seed'): And(Use(int), lambda x: x >= 0),
                         Optional('dataReporter', default='mat'): str,
                         'Rser': Use(float),
                         'Nvol_c': And(Use(int), lambda x: x > 0),
                         'Nvol_s': And(Use(int), lambda x: x >= 0),
                         'Nvol_a': And(Use(int), lambda x: x >= 0),
                         'Npart_c': And(Use(int), lambda x: x >= 0),
                         'Npart_a': And(Use(int), lambda x: x >= 0),
                         #Control Constraints #GG
                        Optional('V_ub', default=float('inf')):Use(float),
                        Optional('I_ub', default=float('inf')):Use(float),
                        Optional('P_ub', default=float('inf')):Use(float),
                        Optional('LPOverpot_lb', default=float('-inf')):Use(float),
                        Optional('Ce_lb', default=float('-inf')):Use(float),
                        Optional('Ce_ub', default=float('inf')):Use(float),
                        Optional('Cs_ub', default=float('inf')):Use(float),
                        Optional('T_ub', default=float('inf')):Use(float),
                        Optional('ffrac_Tend', default=float('inf')):Use(float),
                        Optional('deadband', default=0):Use(float)},
          'Electrodes': {'cathode': str,
                         'anode': str,
                         'k0_foil': Use(float),
                         'Rfilm_foil': Use(float)},
          'Particles': {'distribution_c': str,
                        'mean_c': Use(float),
                        'stddev_c': Use(float),
                        'distribution_a': str,
                        'mean_a': Use(float),
                        'stddev_a': Use(float),
                        'cs0_c': Use(float),
                        'cs0_a': Use(float),
                        Optional('specified_psd_c', default=False):
                            Or(Use(tobool), Use(lambda x: np.array(ast.literal_eval(x)))),
                        Optional('specified_psd_a', default=False):
                            Or(Use(tobool), Use(lambda x: np.array(ast.literal_eval(x))))},
          'Conductivity': {'simBulkCond_c': Use(tobool),
                           'simBulkCond_a': Use(tobool),
                           'sigma_s_c': Use(float),
                           'sigma_s_a': Use(float),
                           'simPartCond_c': Use(tobool),
                           'simPartCond_a': Use(tobool),
                           'G_mean_c': Use(float),
                           'G_stddev_c': Use(float),
                           'G_mean_a': Use(float),
                           'G_stddev_a': Use(float)},
          'Geometry': {'L_c': Use(float),
                       'L_a': Use(float),
                       'L_s': Use(float),
                       'P_L_c': Use(float),
                       'P_L_a': Use(float),
                       'poros_c': Use(float),
                       'poros_a': Use(float),
                       'poros_s': Use(float),
                       'BruggExp_c': Use(float),
                       'BruggExp_a': Use(float),
                       'BruggExp_s': Use(float)},
          'Thermal Parameters': {Optional('cp_c', default=1e8): Use(float),
                                 Optional('cp_a', default=1e8): Use(float),
                                 Optional('cp_l', default=1e8): Use(float),
                                 Optional('rhom_c', default=0.2): Use(float),
                                 Optional('rhom_a', default=0.2): Use(float),
                                 Optional('rhom_l', default=0.2): Use(float),
                                 Optional('k_h_c', default=0.2): Use(float),
                                 Optional('k_h_a', default=0.2): Use(float),
                                 Optional('k_h_s', default=0.2): Use(float),
                                 Optional('h_h', default=500): Use(float),
                                 Optional('sigma_l', default=500): Use(float),
                                 Optional('ent_heat_gen', default=True): Use(tobool)},
          'Electrolyte': {'c0': Use(float),
                          'zp': Use(int),
                          'zm': And(Use(int), lambda x: x < 0),
                          'nup': Use(int),
                          'num': Use(int),
                          'elyteModelType': str,
                          Optional('SMset_filename', default=None): str,
                          'SMset': str,
                          'n': Use(int),
                          'sp': Use(int),
                          'Dp': Use(float),
                          'Dm': Use(float)}}

#: Electrode parameters, per section
electrode = {'Particles': {'type': lambda x: check_allowed_values(x,
                                                                  constants.one_var_types
                                                                  + constants.two_var_types),
                           'discretization': Use(float),
                           'shape': lambda x:
                               check_allowed_values(x, ["C3", "sphere", "cylinder", "homog_sdn"]),
                           Optional('thickness'): Use(float)},
             'Material': {Optional('muRfunc_filename', default=None): str,
                          'muRfunc': str,
                          'logPad': Use(tobool),
                          'noise': Use(tobool),
                          'noise_prefac': Use(float),
                          'numnoise': Use(int),
                          Optional('Omega_a', default=None): Use(float),
                          Optional('Omega_b', default=None): Use(float),
                          Optional('Omega_c', default=None): Use(float),
                          'kappa': Use(float),
                          'B': Use(float),
                          Optional('EvdW', default=None): Use(float),
                          'rho_s': Use(float),
                          'D': Use(float),
                          Optional('Dfunc_filename', default=None): str,
                          'Dfunc': str,
                          Optional('E_D', default=0.): Use(float),
                          'dgammadc': Use(float),
                          'cwet': Use(float)},
             'Reactions': {Optional('rxnType_filename', default=None): str,
                           'rxnType': str,
                           'k0': Use(float),
                           Optional('E_A', default=0.): Use(float),
                           'alpha': Use(float),
                           'lambda': Use(float),
                           'Rfilm': Use(float),
                           Optional('k0_nuc', default=None): Use(float),
                           Optional('alpha_nuc', default=None): Use(float),
                           Optional('V_nuc', default=None): Use(float),
                           Optional('gamma', default=None): Use(float),
                           Optional('k0_pl', default=None): Use(float),
                           Optional('alpha_pl', default=None): Use(float),
                           Optional('k0_chem', default=None): Use(float)}}


# convert the dictionaries to actual schemas
for d in [system, electrode]:
    for key, value in d.items():
        d[key] = Schema(value, ignore_extra_keys=False)
