"""These models define individual particles of active material.

This includes the equations for both 1-parameter models and 2-parameters models defining
 - mass conservation (concentration evolution)
 - reaction rate at the surface of the particles
In each model class it has options for different types of particles:
 - homogeneous
 - Fick-like diffusion
 - Cahn-Hilliard (with reaction boundary condition)
 - Allen-Cahn (with reaction throughout the particle)
These models can be instantiated from the mod_cell module to simulate various types of active
materials within a battery electrode.
"""
import daetools.pyDAE as dae
import numpy as np
import scipy.sparse as sprs
import scipy.interpolate as sintrp

import mpet.extern_funcs as extern_funcs
import mpet.geometry as geo
import mpet.ports as ports
import mpet.props_am as props_am
import mpet.utils as utils
import mpet.electrode.reactions as reactions
from mpet.daeVariableTypes import *


class Mod2var(dae.daeModel):
    def __init__(self, config, trode, vInd, pInd,
                 Name, Parent=None, Description=""):
        super().__init__(Name, Parent, Description)

        self.config = config
        self.trode = trode
        self.ind = (vInd, pInd)

        # Domain
        self.Dmn = dae.daeDomain("discretizationDomain", self, dae.unit(),
                                 "discretization domain")

        # Variables
        self.c1 = dae.daeVariable(
            "c1", mole_frac_t, self,
            "Concentration in 'layer' 1 of active particle", [self.Dmn])
        self.c2 = dae.daeVariable(
            "c2", mole_frac_t, self,
            "Concentration in 'layer' 2 of active particle", [self.Dmn])
        self.cbar = dae.daeVariable(
            "cbar", mole_frac_t, self,
            "Average concentration in active particle")
        self.c1bar = dae.daeVariable(
            "c1bar", mole_frac_t, self,
            "Average concentration in 'layer' 1 of active particle")
        self.c2bar = dae.daeVariable(
            "c2bar", mole_frac_t, self,
            "Average concentration in 'layer' 2 of active particle")
        self.dcbardt = dae.daeVariable("dcbardt", dae.no_t, self, "Rate of particle filling")
        self.dcbar1dt = dae.daeVariable("dcbar1dt", dae.no_t, self, "Rate of particle 1 filling")
        self.dcbar2dt = dae.daeVariable("dcbar2dt", dae.no_t, self, "Rate of particle 2 filling")
        self.q_rxn_bar = dae.daeVariable(
            "q_rxn_bar", dae.no_t, self, "Rate of heat generation in particle")
        if self.get_trode_param("type") not in ["ACR2"]:
            self.Rxn1 = dae.daeVariable("Rxn1", dae.no_t, self, "Rate of reaction 1")
            self.Rxn2 = dae.daeVariable("Rxn2", dae.no_t, self, "Rate of reaction 2")
        else:
            self.Rxn1 = dae.daeVariable("Rxn1", dae.no_t, self, "Rate of reaction 1", [self.Dmn])
            self.Rxn2 = dae.daeVariable("Rxn2", dae.no_t, self, "Rate of reaction 2", [self.Dmn])
        

        # Get reaction rate function
        self.calc_rxn_rate = utils.import_function(config[trode, "rxnType_filename"],
                                                   config[trode, "rxnType"],
                                                   mpet_module="mpet.electrode.reactions")

        # Ports
        self.portInLyte = ports.portFromElyte(
            "portInLyte", dae.eInletPort, self, "Inlet port from electrolyte")
        self.portInBulk = ports.portFromBulk(
            "portInBulk", dae.eInletPort, self,
            "Inlet port from e- conducting phase")
        self.phi_lyte = self.portInLyte.phi_lyte
        self.T_lyte = self.portInLyte.T_lyte
        self.c_lyte = self.portInLyte.c_lyte
        self.phi_m = self.portInBulk.phi_m

    def get_trode_param(self, item):
        """
        Shorthand to retrieve electrode-specific value
        """
        value = self.config[self.trode, item]
        # check if it is a particle-specific parameter
        if item in self.config.params_per_particle:
            value = value[self.ind]
        return value

    def DeclareEquations(self):
        dae.daeModel.DeclareEquations(self)
        N = self.get_trode_param("N")  # number of grid points in particle
        r_vec, volfrac_vec = geo.get_unit_solid_discr(self.get_trode_param('shape'), N)

        # Prepare the Ideal Solution log ratio terms
        self.ISfuncs1 = self.ISfuncs2 = None
        if self.get_trode_param("logPad"):
            self.ISfuncs1 = np.array([
                extern_funcs.LogRatio("LR1", self, dae.unit(), self.c1(k))
                for k in range(N)])
            self.ISfuncs2 = np.array([
                extern_funcs.LogRatio("LR2", self, dae.unit(), self.c2(k))
                for k in range(N)])
        ISfuncs = (self.ISfuncs1, self.ISfuncs2)

        # Prepare noise
        self.noise1 = self.noise2 = None
        if self.get_trode_param("noise"):
            numnoise = self.get_trode_param("numnoise")
            noise_prefac = self.get_trode_param("noise_prefac")
            tvec = np.linspace(0., 1.05*self.config["tend"], numnoise)
            noise_data1 = noise_prefac*np.random.randn(numnoise, N)
            noise_data2 = noise_prefac*np.random.randn(numnoise, N)
            self.noise1 = sintrp.interp1d(tvec, noise_data1, axis=0,
                                          bounds_error=False, fill_value=0.)
            self.noise2 = sintrp.interp1d(tvec, noise_data2, axis=0,
                                          bounds_error=False, fill_value=0.)
        noises = (self.noise1, self.noise2)

        # Figure out mu_O, mu of the oxidized state
        mu_O, act_lyte = calc_mu_O(
            self.c_lyte(), self.phi_lyte(), self.phi_m(), self.T_lyte(),
            self.config["elyteModelType"])

        # Define average filling fractions in particle
        eq1 = self.CreateEquation("c1bar")
        eq2 = self.CreateEquation("c2bar")
        eq1.Residual = self.c1bar()
        eq2.Residual = self.c2bar()
        for k in range(N):
            eq1.Residual -= self.c1(k) * volfrac_vec[k]
            eq2.Residual -= self.c2(k) * volfrac_vec[k]
        eq = self.CreateEquation("cbar")
        eq.Residual = self.cbar() - .5*(self.c1bar() + self.c2bar())

        # Define average rate of filling of particle
        eq = self.CreateEquation("dcbardt")
        eq.Residual = self.dcbardt()
        for k in range(N):
            eq.Residual -= .5*(self.c1.dt(k) + self.c2.dt(k)) * volfrac_vec[k]

        # Define average rate of filling of particle for cbar1
        eq = self.CreateEquation("dcbar1dt")
        eq.Residual = self.dcbar1dt()
        for k in range(N):
            eq.Residual -= self.c1.dt(k) * volfrac_vec[k]

        # Define average rate of filling of particle for cbar1
        eq = self.CreateEquation("dcbar2dt")
        eq.Residual = self.dcbar2dt()
        for k in range(N):
            eq.Residual -= self.c2.dt(k) * volfrac_vec[k]

        c1 = np.empty(N, dtype=object)
        c2 = np.empty(N, dtype=object)
        c1[:] = [self.c1(k) for k in range(N)]
        c2[:] = [self.c2(k) for k in range(N)]
        if self.get_trode_param("type") in ["diffn2", "CHR2"]:
            # Equations for 1D particles of 1 field varible
            eta1, eta2, c_surf1, c_surf2 = self.sld_dynamics_1D2var(c1, c2, mu_O, act_lyte,
                                                                    ISfuncs, noises)
        elif self.get_trode_param("type") in ["homog2", "homog2_sdn"]:
            # Equations for 0D particles of 1 field variables
            eta1, eta2, c_surf1, c_surf2 = self.sld_dynamics_0D2var(c1, c2, mu_O, act_lyte,
                                                                    ISfuncs, noises)

        # Define average rate of heat generation
        eq = self.CreateEquation("q_rxn_bar")
        if self.config["ent_heat_gen"]:
            eq.Residual = self.q_rxn_bar() - 0.5 * self.dcbar1dt() * \
                (eta1 - self.T_lyte()*(np.log(c_surf1/(1-c_surf1))-1/self.c_lyte())) \
                - 0.5 * self.dcbar2dt() * (eta2 - self.T_lyte()
                                           * (np.log(c_surf2/(1-c_surf2))-1/self.c_lyte()))
        else:
            eq.Residual = self.q_rxn_bar() - 0.5 * self.dcbar1dt() * eta1 \
                - 0.5 * self.dcbar2dt() * eta2

        for eq in self.Equations:
            eq.CheckUnitsConsistency = False

    def sld_dynamics_0D2var(self, c1, c2, muO, act_lyte, ISfuncs, noises):
        c1_surf = c1
        c2_surf = c2
        (mu1R_surf, mu2R_surf), (act1R_surf, act2R_surf) = calc_muR(
            (c1_surf, c2_surf), (self.c1bar(), self.c2bar()), self.T_lyte(), self.config,
            self.trode, self.ind, ISfuncs)
        eta1 = calc_eta(mu1R_surf, muO)
        eta2 = calc_eta(mu2R_surf, muO)
        eta1_eff = eta1 + self.Rxn1()*self.get_trode_param("Rfilm")
        eta2_eff = eta2 + self.Rxn2()*self.get_trode_param("Rfilm")
        noise1, noise2 = noises
        if self.get_trode_param("noise"):
            eta1_eff += noise1(dae.Time().Value)
            eta2_eff += noise2(dae.Time().Value)
        Rxn1 = self.calc_rxn_rate(
            eta1_eff, c1_surf, self.c_lyte(), self.get_trode_param("k0"),
            self.get_trode_param("E_A"), self.T_lyte(), act1R_surf, act_lyte,
            self.get_trode_param("lambda"), self.get_trode_param("alpha"))
        Rxn2 = self.calc_rxn_rate(
            eta2_eff, c2_surf, self.c_lyte(), self.get_trode_param("k0"),
            self.get_trode_param("E_A"), self.T_lyte(), act2R_surf, act_lyte,
            self.get_trode_param("lambda"), self.get_trode_param("alpha"))
        eq1 = self.CreateEquation("Rxn1")
        eq2 = self.CreateEquation("Rxn2")
        eq1.Residual = self.Rxn1() - Rxn1[0]
        eq2.Residual = self.Rxn2() - Rxn2[0]

        eq1 = self.CreateEquation("dc1sdt")
        eq2 = self.CreateEquation("dc2sdt")
        eq1.Residual = self.c1.dt(0) - self.get_trode_param("delta_L")*Rxn1[0]
        eq2.Residual = self.c2.dt(0) - self.get_trode_param("delta_L")*Rxn2[0]
        return eta1[-1], eta2[-1], c1_surf[-1], c2_surf[-1]

    def sld_dynamics_1D2var(self, c1, c2, muO, act_lyte, ISfuncs, noises):
        N = self.get_trode_param("N")
        # Equations for concentration evolution
        # Mass matrix, M, where M*dcdt = RHS, where c and RHS are vectors
        Mmat = get_Mmat(self.get_trode_param('shape'), N)
        dr, edges = geo.get_dr_edges(self.get_trode_param('shape'), N)

        # Get solid particle chemical potential, overpotential, reaction rate
        if self.get_trode_param("type") in ["diffn2", "CHR2"]:
            (mu1R, mu2R), (act1R, act2R) = calc_muR((c1, c2), (self.c1bar(), self.c2bar()),
                                                    self.T_lyte(), self.config, self.trode,
                                                    self.ind, ISfuncs)
            c1_surf = c1[-1]
            c2_surf = c2[-1]
            mu1R_surf, act1R_surf = mu1R[-1], act1R[-1]
            mu2R_surf, act2R_surf = mu2R[-1], act2R[-1]
        eta1 = calc_eta(mu1R_surf, muO)
        eta2 = calc_eta(mu2R_surf, muO)
        if self.get_trode_param("type") in ["ACR2"]:
            eta1_eff = np.array([eta1[i]
                                 + self.Rxn1(i)*self.get_trode_param("Rfilm") for i in range(N)])
            eta2_eff = np.array([eta2[i]
                                 + self.Rxn2(i)*self.get_trode_param("Rfilm") for i in range(N)])
        else:
            eta1_eff = eta1 + self.Rxn1()*self.get_trode_param("Rfilm")
            eta2_eff = eta2 + self.Rxn2()*self.get_trode_param("Rfilm")
        Rxn1 = self.calc_rxn_rate(
            eta1_eff, c1_surf, self.c_lyte(), self.get_trode_param("k0"),
            self.get_trode_param("E_A"), self.T_lyte(), act1R_surf, act_lyte,
            self.get_trode_param("lambda"), self.get_trode_param("alpha"))
        Rxn2 = self.calc_rxn_rate(
            eta2_eff, c2_surf, self.c_lyte(), self.get_trode_param("k0"),
            self.get_trode_param("E_A"), self.T_lyte(), act2R_surf, act_lyte,
            self.get_trode_param("lambda"), self.get_trode_param("alpha"))
        if self.get_trode_param("type") in ["ACR2"]:
            for i in range(N):
                eq1 = self.CreateEquation("Rxn1_{i}".format(i=i))
                eq2 = self.CreateEquation("Rxn2_{i}".format(i=i))
                eq1.Residual = self.Rxn1(i) - Rxn1[i]
                eq2.Residual = self.Rxn2(i) - Rxn2[i]
        else:
            eq1 = self.CreateEquation("Rxn1")
            eq2 = self.CreateEquation("Rxn2")
            eq1.Residual = self.Rxn1() - Rxn1
            eq2.Residual = self.Rxn2() - Rxn2

        # Get solid particle fluxes (if any) and RHS
        if self.get_trode_param("type") in ["diffn2", "CHR2"]:
            # Positive reaction (reduction, intercalation) is negative
            # flux of Li at the surface.
            Flux1_bc = -0.5 * self.Rxn1()
            Flux2_bc = -0.5 * self.Rxn2()
            Dfunc = props_am.Dfuncs(self.get_trode_param("Dfunc"),
                                    self.get_trode_param("Dfunc_filename")).Dfunc
            if self.get_trode_param("type") == "diffn2":
                pass
#                Flux1_vec, Flux2_vec = calc_Flux_diffn2(
#                    c1, c2, self.get_trode_param("D"), Flux1_bc, Flux2_bc, dr, T)
            elif self.get_trode_param("type") == "CHR2":
                noise1, noise2 = noises
                Flux1_vec, Flux2_vec = calc_flux_CHR2(
                    c1, c2, mu1R, mu2R, self.get_trode_param("D"), Dfunc,
                    self.get_trode_param("E_D"), Flux1_bc, Flux2_bc, dr, self.T_lyte(),
                    noise1, noise2)
            if self.get_trode_param("shape") == "sphere":
                area_vec = 4*np.pi*edges**2
            elif self.get_trode_param("shape") == "cylinder":
                area_vec = 2*np.pi*edges  # per unit height
            RHS1 = -np.diff(Flux1_vec * area_vec)
            RHS2 = -np.diff(Flux2_vec * area_vec)
#            kinterlayer = 1e-3
#            interLayerRxn = (kinterlayer * (1 - c1) * (1 - c2) * (act1R - act2R))
#            RxnTerm1 = -interLayerRxn
#            RxnTerm2 = interLayerRxn
            RxnTerm1 = 0
            RxnTerm2 = 0
            RHS1 += RxnTerm1
            RHS2 += RxnTerm2

        dc1dt_vec = np.empty(N, dtype=object)
        dc2dt_vec = np.empty(N, dtype=object)
        dc1dt_vec[0:N] = [self.c1.dt(k) for k in range(N)]
        dc2dt_vec[0:N] = [self.c2.dt(k) for k in range(N)]
        LHS1_vec = MX(Mmat, dc1dt_vec)
        LHS2_vec = MX(Mmat, dc2dt_vec)
        for k in range(N):
            eq1 = self.CreateEquation("dc1sdt_discr{k}".format(k=k))
            eq2 = self.CreateEquation("dc2sdt_discr{k}".format(k=k))
            eq1.Residual = LHS1_vec[k] - RHS1[k]
            eq2.Residual = LHS2_vec[k] - RHS2[k]

        if self.get_trode_param("type") in ["ACR"]:
            return eta1[-1], eta2[-1], c1_surf[-1], c2_surf[-1]
        else:
            return eta1, eta2, c1_surf, c2_surf


class Mod1var(dae.daeModel):
    def __init__(self, config, trode, vInd, pInd,
                 Name, Parent=None, Description=""):
        super().__init__(Name, Parent, Description)

        self.config = config
        self.trode = trode
        self.ind = (vInd, pInd)

        # Domain
        self.Dmn = dae.daeDomain("discretizationDomain", self, dae.unit(),
                                 "discretization domain")


        # Variables
        #    self.detectora = dae.daeVariable("detectora", dae.no_t, self, "Detectora")
        #    self.detectorb = dae.daeVariable("detectorb", dae.no_t, self, "Detectorb")
        #    self.detectorc = dae.daeVariable("detectorc", dae.no_t, self, "Detectorc", [self.Dmn])
        

        self.didt     = dae.daeVariable("didt", dae.no_t, self, "Rate of all faradaic reactions")

        self.c = dae.daeVariable("c", mole_frac_t, self,
                                 "Concentration in active particle",
                                 [self.Dmn])
        self.cbar = dae.daeVariable(
            "cbar", mole_frac_t, self,
            "Average concentration in active particle")
        self.dcbardt = dae.daeVariable("dcbardt", dae.no_t, self, "Rate of particle filling")
        self.Rxn_tot  = dae.daeVariable( "Rxn_tot", dae.no_t, self, "Total rate of faradaic reaction" )
        self.q_rxn_bar = dae.daeVariable(
            "q_rxn_bar", dae.no_t, self, "Rate of heat generation in particle")
        if config[trode, "type"] not in ["ACR"]:
            self.Rxn = dae.daeVariable("Rxn", dae.no_t, self, "Rate of reaction")
        else:
            self.Rxn = dae.daeVariable("Rxn", dae.no_t, self, "Rate of reaction", [self.Dmn])

        if self.trode == 'a':
            
            #GG
            self.etaPlating = dae.daeVariable("etaPlating", dae.no_t, self,
                                              "Plating overpotential")
            self.VLi      = dae.daeVariable( "VLi",    conc_t, self, "Volume of plated lithium")
            self.dVLidt   = dae.daeVariable( "dVLidt", dae.no_t, self, "Rate of volume change of plated lithium" )

            #self.ALi_p    = dae.daeVariable( "ALi_p",  nodim_positive_t, self, "Projected area of plated lithium")
            self.Atilde   = dae.daeVariable( "Atilde", unit_positive_t, self, "Portion of surface reactive for intercalation")

            self.Rxn_pl   = dae.daeVariable( "Rxn_pl",   dae.no_t, self, "Rate of plating reaction" )
            self.Rxn_chem = dae.daeVariable( "Rxn_chem", dae.no_t, self, "Rate of chemical intercalation" )
            self.chem_intercalation_switch = dae.daeVariable("chem_intercalation_switch", unit_positive_t, self, "Switch on/off the Li metal re-intercalation to avoid numerical instability at VLi~0")
            #GG missing from Huada?
            self.platingState= dae.daeVariable("platingState", dae.no_t, self, "Active state of LiPlating STN")
            
        self.intercalation_switch = dae.daeVariable("intercalation_switch", unit_positive_t, self, "Switch on/off the intercalation to avoid numerical instability at cbar~0.999")
        

        # Get reaction rate function
        self.calc_rxn_rate = utils.import_function(config[trode, "rxnType_filename"],
                                                   config[trode, "rxnType"],
                                                   mpet_module="mpet.electrode.reactions")
        if self.trode=='a':
            self.calc_pl_rate    = getattr( reactions,               "Plating" )
            self.calc_chem_rate  = getattr( reactions,               "ChemInt" )



        # Ports
        self.portInLyte = ports.portFromElyte(
            "portInLyte", dae.eInletPort, self,
            "Inlet port from electrolyte")
        self.portInBulk = ports.portFromBulk(
            "portInBulk", dae.eInletPort, self,
            "Inlet port from e- conducting phase")
        self.phi_lyte = self.portInLyte.phi_lyte
        self.T_lyte = self.portInLyte.T_lyte
        self.c_lyte = self.portInLyte.c_lyte
        self.phi_m = self.portInBulk.phi_m

    def get_trode_param(self, item):
        """
        Shorthand to retrieve electrode-specific value
        """
        value = self.config[self.trode, item]
        # check if it is a particle-specific parameter
        if item in self.config.params_per_particle:
            value = value[self.ind]
        return value

    def DeclareEquations(self):
        dae.daeModel.DeclareEquations(self)
        N = self.get_trode_param("N")  # number of grid points in particle
        r_vec, volfrac_vec = geo.get_unit_solid_discr(self.get_trode_param('shape'), N)

        # Prepare the Ideal Solution log ratio terms
        self.ISfuncs = None
        if self.get_trode_param("logPad"):
            self.ISfuncs = np.array([
                extern_funcs.LogRatio("LR", self, dae.unit(), self.c(k))
                for k in range(N)])

        # Prepare noise
        self.noise = None
        if self.get_trode_param("noise"):
            numnoise = self.get_trode_param("numnoise")
            noise_prefac = self.get_trode_param("noise_prefac")
            tvec = np.linspace(0., 1.05*self.config["tend"], numnoise)
            noise_data = noise_prefac*np.random.randn(numnoise, N)
            self.noise = sintrp.interp1d(tvec, noise_data, axis=0,
                                         bounds_error=False, fill_value=0.)

        # Figure out mu_O, mu of the oxidized state
        mu_O, act_lyte = calc_mu_O(self.c_lyte(), self.phi_lyte(), self.phi_m(), self.T_lyte(),
                                   self.config["elyteModelType"])

        # Define the faradaic current from this particle
        # Huada: For full cell, need to distinguish cathode and anode
        eq = self.CreateEquation("didt")
        if self.trode=='a':
            eq.Residual = self.didt() - self.dcbardt() - self.dVLidt()
        elif self.trode=='c':
            eq.Residual = self.didt() - self.dcbardt()

        # Define the total faradaic reaction rate
        # All faradaic reaction experience the same film resistance.
        eq = self.CreateEquation("Rxn_tot")
        if self.trode=='a':
            eq.Residual = self.Rxn_tot() - self.Atilde() * self.Rxn() - self.Rxn_pl()
        elif self.trode=='c':
            eq.Residual = self.Rxn_tot() - 0.0

        if self.trode=='a':
            # Lithium plating
            # Define volume of plated lithium
            eq = self.CreateEquation("VLi")
            eq.Residual = self.VLi.dt() - self.dVLidt()

            # Equations for lithium plating/stripping
            self.deposit_dynamics(mu_O, act_lyte)

        # Intercalation
        # Define average filling fraction in particle
        eq = self.CreateEquation("cbar")
        eq.Residual = self.cbar()
        for k in range(N):
            eq.Residual -= self.c(k) * volfrac_vec[k]

        if self.trode=='a':
            # Soft flux from li metal to graphite as VLi->0
            eq = self.CreateEquation("chem_intercalation_switch", "flux limiter")
            eq.Residual = self.chem_intercalation_switch() -  np.tanh( 10**6 * (1.0 - self.cbar() ) )

        # Soft flux into fully lithiated graphite cbar=1.0
        eq = self.CreateEquation("intercalation_switch", "flux limiter")
        eq.Residual = self.intercalation_switch() -  np.tanh( 10**6 * (1.0 - self.cbar() ) )

        # Define average rate of filling of particle
        eq = self.CreateEquation("dcbardt")
        eq.Residual = self.dcbardt()
        eq.BuildJacobianExpressions = True
        for k in range(N):
            eq.Residual -= self.c.dt(k) * volfrac_vec[k]

        c = np.empty(N, dtype=object)
        c[:] = [self.c(k) for k in range(N)]
        if self.get_trode_param("type") in ["ACR", "diffn", "CHR"]:
            # Equations for 1D particles of 1 field varible
            eta, c_surf = self.sld_dynamics_1D1var(c, mu_O, act_lyte, self.ISfuncs, self.noise)
        elif self.get_trode_param("type") in ["homog", "homog_sdn"]:
            # Equations for 0D particles of 1 field variables
            eta, c_surf = self.sld_dynamics_0D1var(c, mu_O, act_lyte, self.ISfuncs, self.noise)

        # Define average rate of heat generation
        eq = self.CreateEquation("q_rxn_bar")
        if self.config["ent_heat_gen"]:
            eq.Residual = self.q_rxn_bar() - self.dcbardt() * \
                (eta - self.T_lyte()*(np.log(c_surf/(1-c_surf))-1/self.c_lyte()))
        else:
            eq.Residual = self.q_rxn_bar() - self.dcbardt() * eta

        for eq in self.Equations:
            eq.CheckUnitsConsistency = False

    def deposit_dynamics(self, mu_O, act_lyte):
        #T = self.config["T"]
        T = self.T_lyte()
        Vol_Li_ref = self.get_trode_param("Vol_Li_ref")
        V_nuc   = self.get_trode_param("V_nuc") \
                * np.exp( - ( self.VLi() )**2.0 / ( 2.0 * Vol_Li_ref**(2.0) ) )
        #V_nuc   = self.get_trode_param("V_nuc") \
        #        * np.exp( - 4.0 * ( self.VLi() )**1.0 / ( Vol_Li_ref**(1.0) ) )


        # - self.config[self.trode, "muR_ref"][0]
        eta_eff = self.config[self.trode, "muR_ref"][0] - mu_O + self.Rxn_tot() * self.get_trode_param("Rfilm")

        # In plating direction, V_nuc is needed.
        eta_nuc_eff = eta_eff + V_nuc
        
        #GG
        eq = self.CreateEquation("PlatingOverpotential")
        eq.Residual = self.etaPlating() - eta_nuc_eff

        ## Detectora
        #eq = self.CreateEquation("detectora")
        #eq.Residual = self.detectora() - eta_nuc_eff

        # To make the reaction formula a thermodynamically consistent one.
        # Only needed in plating direction
        #act_Li  = np.exp( V_nuc )

        # An important rule is that all states
        # MUST contain the SAME NUMBER OF EQUATIONS.
        self.stnSideReaction = self.STN("SideReaction")

        self.STATE("NoPlating") #State 0

        eq = self.CreateEquation("Rxn_pl", "No lithium")
        eq.Residual = self.Rxn_pl() - 0.0

        eq = self.CreateEquation("Atilde", "No lithium")
        eq.Residual = self.Atilde() - 1.0
        # Define rate of volume change of plated lithium
        eq = self.CreateEquation("dVLidt", "No lithium")
        eq.Residual = self.dVLidt() - 0.0

        ## Switch to STATE( Nucleation )
        self.ON_CONDITION( eta_nuc_eff < dae.Constant(0.0*dae.unit()),
                           switchToStates    = [ ('SideReaction', 'Nucleation' ) ],
                           setVariableValues = [(self.platingState,1)]) #GG missing from Huada?


        self.STATE("Nucleation") #State 1

        eq = self.CreateEquation("Rxn_pl")
        Rxn_pl = self.calc_pl_rate(
               eta_nuc_eff, self.c_lyte(), self.get_trode_param("k0_nuc"),
               T, 1.0, act_lyte, self.get_trode_param("alpha_nuc") )
        eq.Residual = self.Rxn_pl() - Rxn_pl

        # Define portion of surface area available for intercalation
        eq = self.CreateEquation("Atilde", "Nucleation")
        eq.Residual = self.Atilde() - ( 1.0 - ( self.VLi() / Vol_Li_ref) )

        # Define rate of volume change of plated lithium
        eq = self.CreateEquation("dVLidt")
        eq.Residual = self.dVLidt() - self.get_trode_param("delta_L")\
                                    * ( self.Rxn_pl() - (1 - self.Atilde()) * self.Rxn_chem() )
        #eq.BuildJacobianExpressions = True

        # Switch to STATE( Growth )
        self.ON_CONDITION( self.VLi() > dae.Constant(Vol_Li_ref*dae.unit()),
                               switchToStates    = [ ('SideReaction', 'Growth' ) ],
                               setVariableValues = [(self.platingState,2)]) #GG missing from Huada?
        # Switch to STATE( No Plating )
        #self.ON_CONDITION( self.VLi() < dae.Constant(0.0*dae.unit()),
        #                       switchToStates    = [ ('SideReaction', 'NoPlating' ) ])

        self.STATE("Growth") #State 2
        eq = self.CreateEquation("Rxn_pl")
        Rxn_pl = self.calc_pl_rate(
               eta_nuc_eff, self.c_lyte(), self.get_trode_param("k0_pl"),
               T, 1.0, act_lyte, self.get_trode_param("alpha_pl") )
        eq.Residual = self.Rxn_pl() - Rxn_pl
        # Define portion of surface area available to intercalation
        eq = self.CreateEquation("Atilde", "Growth")
        eq.Residual = self.Atilde() - 0.0

        # Define rate of volume change of plated lithium
        eq = self.CreateEquation("dVLidt")
        eq.Residual = self.dVLidt() - self.get_trode_param("delta_L")\
                                    * ( self.Rxn_pl() - ( 1.0 - self.Atilde() ) * self.Rxn_chem() )

        # Switch to STATE( Nucleation )
        self.ON_CONDITION( self.VLi() < dae.Constant(Vol_Li_ref*dae.unit()),
                               switchToStates    = [ ('SideReaction', 'Nucleation' ) ],
                               setVariableValues = [(self.platingState,1)]) #GG missing from Huada?

        self.END_STN()



    def sld_dynamics_0D1var(self, c, muO, act_lyte, ISfuncs, noise):
        c_surf = c
        muR_surf, actR_surf = calc_muR(c_surf, self.cbar(), self.T_lyte(),self.config,
                                       self.trode, self.ind, ISfuncs)
        eta = calc_eta(muR_surf, muO)
        eta_eff = eta + self.Rxn()*self.get_trode_param("Rfilm")
        if self.get_trode_param("noise"):
            eta_eff += noise[0]()
        Rxn = self.calc_rxn_rate(
            eta_eff, c_surf, self.c_lyte(), self.get_trode_param("k0"),
            self.get_trode_param("E_A"), self.T_lyte(), actR_surf, act_lyte,
            self.get_trode_param("lambda"), self.get_trode_param("alpha"))
        eq = self.CreateEquation("Rxn")
        eq.Residual = self.Rxn() - Rxn[0]

        eq = self.CreateEquation("dcsdt")
        eq.Residual = self.c.dt(0) - self.get_trode_param("delta_L")*self.Rxn()

        return eta[-1], c_surf[-1]

    def sld_dynamics_1D1var(self, c, muO, act_lyte, ISfuncs, noise):
        N = self.get_trode_param("N")
        T = self.T_lyte()
        # Equations for concentration evolution
        # Mass matrix, M, where M*dcdt = RHS, where c and RHS are vectors
        Mmat = get_Mmat(self.get_trode_param('shape'), N)
        dr, edges = geo.get_dr_edges(self.get_trode_param('shape'), N)

        # Get solid particle chemical potential, overpotential, reaction rate
        if self.get_trode_param("type") in ["ACR"]:
            c_surf = c
            muR_surf, actR_surf = calc_muR(
                c_surf, self.cbar(), self.T_lyte(), self.config, self.trode, self.ind, ISfuncs)
        elif self.get_trode_param("type") in ["diffn", "CHR"]:
            muR, actR = calc_muR(c, self.cbar(), self.T_lyte(),
                                 self.config, self.trode, self.ind, ISfuncs)
            c_surf = c[-1]
            muR_surf = muR[-1]
            if actR is None:
                actR_surf = None
            else:
                actR_surf = actR[-1]
        eta = calc_eta(muR_surf, muO)
        if self.get_trode_param("type") in ["ACR"]:
            eta_eff = np.array([eta[i] + self.Rxn(i)*self.get_trode_param("Rfilm")
                                for i in range(N)])
        else:
            #eta_eff = eta + self.Rxn()*self.get_trode_param("Rfilm")
            if self.trode=='a':
                # Huada: self.Rxn -> self.Rxn_tot
                eta_eff      = eta + self.Rxn_tot() * self.get_trode_param("Rfilm")
            elif self.trode=='c':
                eta_eff = eta + self.Rxn_tot() * self.get_trode_param("Rfilm")


        Rxn = self.calc_rxn_rate(
            eta_eff, c_surf, self.c_lyte(), self.get_trode_param("k0"),
            self.get_trode_param("E_A"), self.T_lyte(), actR_surf, act_lyte,
            self.get_trode_param("lambda"), self.get_trode_param("alpha"))
        if self.get_trode_param("type") in ["ACR"]:
            for i in range(N):
                eq = self.CreateEquation("Rxn_{i}".format(i=i))
                eq.Residual = self.Rxn(i) - Rxn[i]
        else:
            eq = self.CreateEquation("Rxn")
            #eq.Residual = self.Rxn() - Rxn
            eq.Residual = self.Rxn() - self.intercalation_switch() * Rxn
        if self.trode=='a':
            # overpotential of chemical intercalation
            eta_chem = (muR_surf - self.config[self.trode, "muR_ref"][0]) - 0.0

            Rxn_chem = self.calc_chem_rate(
                eta_chem, c_surf, self.get_trode_param("k0_chem"),
                T, actR_surf)
            eq = self.CreateEquation("Rxn_chem")
            eq.Residual = self.Rxn_chem() - self.intercalation_switch() * self.chem_intercalation_switch() * Rxn_chem



        # Get solid particle fluxes (if any) and RHS
        if self.get_trode_param("type") in ["ACR"]:
            RHS = np.array([self.get_trode_param("delta_L")*self.Rxn(i) for i in range(N)])
        elif self.get_trode_param("type") in ["diffn", "CHR"]:
            # Positive reaction (reduction, intercalation) is negative
            # flux of Li at the surface.
            #Flux_bc = -self.Rxn()
            # Flux_boundary condition needs a weighted average over intercalation and chemical intercalation
            # Positive reaction (reduction, intercalation, reintercalation) is negative
            # flux of Li at the surface.
            # Flux_bc = -self.Rxn()
            if self.trode=='a':
                Flux_bc = (-self.Atilde() * self.Rxn() - ( 1-self.Atilde() ) * self.Rxn_chem())
            elif self.trode=='c':
                Flux_bc = -self.Rxn()

            Dfunc = props_am.Dfuncs(self.get_trode_param("Dfunc"),
                                    self.get_trode_param("Dfunc_filename")).Dfunc
            if self.get_trode_param("type") == "diffn":
                Flux_vec = calc_flux_diffn(c, self.get_trode_param("D"), Dfunc,
                                           self.get_trode_param("E_D"), Flux_bc, dr,
                                           self.T_lyte(), noise)
            elif self.get_trode_param("type") == "CHR":
                Flux_vec = calc_flux_CHR(c, muR, self.get_trode_param("D"), Dfunc,
                                         self.get_trode_param("E_D"), Flux_bc, dr,
                                         self.T_lyte(), noise)
            if self.get_trode_param("shape") == "sphere":
                area_vec = 4*np.pi*edges**2
            elif self.get_trode_param("shape") == "cylinder":
                area_vec = 2*np.pi*edges  # per unit height
            RHS = -np.diff(Flux_vec * area_vec)

        dcdt_vec = np.empty(N, dtype=object)
        dcdt_vec[0:N] = [self.c.dt(k) for k in range(N)]
        LHS_vec = MX(Mmat, dcdt_vec)
        for k in range(N):
            eq = self.CreateEquation("dcsdt_discr{k}".format(k=k))
            eq.Residual = LHS_vec[k] - RHS[k]

        if self.get_trode_param("type") in ["ACR"]:
            return eta[-1], c_surf[-1]
        else:
            return eta, c_surf


def calc_eta(muR, muO):
    return muR - muO


def get_Mmat(shape, N):
    r_vec, volfrac_vec = geo.get_unit_solid_discr(shape, N)
    if shape == "C3":
        Mmat = sprs.eye(N, N, format="csr")
    elif shape in ["sphere", "cylinder"]:
        Rs = 1.
        # For discretization background, see Zeng & Bazant 2013
        # Mass matrix is common for each shape, diffn or CHR
        if shape == "sphere":
            Vp = 4./3. * np.pi * Rs**3
        elif shape == "cylinder":
            Vp = np.pi * Rs**2  # per unit height
        vol_vec = Vp * volfrac_vec
        M1 = sprs.diags([1./8, 3./4, 1./8], [-1, 0, 1],
                        shape=(N, N), format="csr")
        M1[1,0] = M1[-2,-1] = 1./4
        M2 = sprs.diags(vol_vec, 0, format="csr")
        Mmat = M1*M2
    return Mmat


def calc_flux_diffn(c, D, Dfunc, E_D, Flux_bc, dr, T, noise):
    N = len(c)
    Flux_vec = np.empty(N+1, dtype=object)
    Flux_vec[0] = 0  # Symmetry at r=0
    Flux_vec[-1] = Flux_bc
    c_edges = utils.mean_linear(c)
    if noise is None:
        Flux_vec[1:N] = -D * Dfunc(c_edges) * np.exp(-E_D/T + E_D/1) * np.diff(c)/dr
    else:
        Flux_vec[1:N] = -D * Dfunc(c_edges) * np.exp(-E_D/T + E_D/1) * \
            np.diff(c + noise(dae.Time().Value))/dr
    return Flux_vec


def calc_flux_CHR(c, mu, D, Dfunc, E_D, Flux_bc, dr, T, noise):
    N = len(c)
    Flux_vec = np.empty(N+1, dtype=object)
    Flux_vec[0] = 0  # Symmetry at r=0
    Flux_vec[-1] = Flux_bc
    c_edges = utils.mean_linear(c)
    if noise is None:
        Flux_vec[1:N] = -D/T * Dfunc(c_edges) * np.exp(-E_D/T + E_D/1) * np.diff(mu)/dr
    else:
        Flux_vec[1:N] = -D/T * Dfunc(c_edges) * np.exp(-E_D/T + E_D/1) * \
            np.diff(mu + noise(dae.Time().Value))/dr
    return Flux_vec


def calc_flux_CHR2(c1, c2, mu1_R, mu2_R, D, Dfunc, E_D, Flux1_bc, Flux2_bc, dr, T, noise1, noise2):
    N = len(c1)
    Flux1_vec = np.empty(N+1, dtype=object)
    Flux2_vec = np.empty(N+1, dtype=object)
    Flux1_vec[0] = 0.  # symmetry at r=0
    Flux2_vec[0] = 0.  # symmetry at r=0
    Flux1_vec[-1] = Flux1_bc
    Flux2_vec[-1] = Flux2_bc
    c1_edges = utils.mean_linear(c1)
    c2_edges = utils.mean_linear(c2)
    if noise1 is None:
        Flux1_vec[1:N] = -D/T * Dfunc(c1_edges) * np.exp(-E_D/T + E_D/1) * np.diff(mu1_R)/dr
        Flux2_vec[1:N] = -D/T * Dfunc(c2_edges) * np.exp(-E_D/T + E_D/1) * np.diff(mu2_R)/dr
    else:
        Flux1_vec[1:N] = -D/T * Dfunc(c1_edges) * np.exp(-E_D/T + E_D/1) * \
            np.diff(mu1_R+noise1(dae.Time().Value))/dr
        Flux2_vec[1:N] = -D/T * Dfunc(c2_edges) * np.exp(-E_D/T + E_D/1) * \
            np.diff(mu2_R+noise2(dae.Time().Value))/dr
    return Flux1_vec, Flux2_vec


def calc_mu_O(c_lyte, phi_lyte, phi_sld, T, elyteModelType):
    if elyteModelType == "SM":
        mu_lyte = phi_lyte
        act_lyte = c_lyte
    elif elyteModelType == "dilute":
        act_lyte = c_lyte
        mu_lyte = T*np.log(act_lyte) + phi_lyte
    mu_O = mu_lyte - phi_sld
    return mu_O, act_lyte


def calc_muR(c, cbar, T, config, trode, ind, ISfuncs=None):
    muRfunc = props_am.muRfuncs(config, trode, ind).muRfunc
    muR_ref = config[trode, "muR_ref"]
    muR, actR = muRfunc(c, cbar, T, muR_ref, ISfuncs)
    return muR, actR


def MX(mat, objvec):
    if not isinstance(mat, sprs.csr.csr_matrix):
        raise Exception("MX function designed for csr mult")
    n = objvec.shape[0]
    if isinstance(objvec[0], dae.pyCore.adouble):
        out = np.empty(n, dtype=object)
    else:
        out = np.zeros(n, dtype=float)
    # Loop through the rows
    for i in range(n):
        low = mat.indptr[i]
        up = mat.indptr[i+1]
        if up > low:
            out[i] = np.sum(
                mat.data[low:up] * objvec[mat.indices[low:up]])
        else:
            out[i] = 0.0
    return out
