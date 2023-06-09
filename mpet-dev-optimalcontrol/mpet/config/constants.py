# global constants

#: Reference temperature, K
T_ref = 298.
#: Boltzmann constant, J/(K particle)
k = 1.381e-23
#: Electron charge, C
e = 1.602e-19
#: Avogadro constant, particle / mol
N_A = 6.022e23
#: Reference flux, C/mol
F = e * N_A
#: General particle classification (1 var)
two_var_types = ["diffn2", "CHR2", "homog2", "homog2_sdn"]
#: General particle classification (2 var)
one_var_types = ["ACR", "diffn", "CHR", "homog", "homog_sdn"]
#: Reference concentration, mol/m^3 = 1M
c_ref = 1000.
#: Molar volume of lithium, m^3/mol
Omega_Li = 13.02 * 10**(-6)



#: parameter that are defined per electrode with a ``_{electrode}`` suffix
PARAMS_PER_TRODE = ['Nvol', 'Npart', 'distribution','mean', 'stddev', 'cs0', 'simBulkCond', 'sigma_s',
                    'simPartCond', 'G_mean', 'G_stddev', 'L', 'P_L', 'poros', 'BruggExp',
                    'specified_psd', 'rhom', 'cp', 'k_h']
#: subset of ``PARAMS_PER_TRODE``` that is defined for the separator as well
PARAMS_SEPARATOR = ['Nvol', 'L', 'poros', 'BruggExp', 'k_h']
# PARAMETERS THAT ARE NEEDED IN A THERMAL MODEL FOR ELECTROLYTE PROPERTIES
PARAMS_ELYTE = ['cp', 'sigma', 'rhom']
#: parameters that are defined for each particle, and their type
PARAMS_PARTICLE = {'N': int, 'kappa': float, 'beta_s': float, 'D': float, 'k0': float,
                   'Rfilm': float, 'delta_L': float, 'Omega_a': float, 'E_D': float,
                   'E_A': float, 'k0_nuc': float, 'k0_pl': float, 'V_nuc': float,
                   'Vol_ref': float, 'Vol_Li_ref': float,
                   'gamma': float, 'r_crit': float, 'k0_chem': float, 'parea': float}
