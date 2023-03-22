function [scalingConstants]=getScalingConstants(batteryData)
% [scalingConstants]=getScalingConstants(batteryData)
% Compute scaling constants to match adimensionalization carried out in
% MPET
%Inputs:
% batteryData: struct, with fields:
% batteryData.A.rho_s
% batteryData.C.rho_s
% batteryData.A.type
% batteryData.C.type
% batteryData.A.L
% batteryData.A.poros
% batteryData.A.P_L
% batteryData.A.muRef
% batteryData.C.muRef
% the meaning of each field mathes that of the corresponding variable in an MPET configuration 
%Outputs:
% scalingConstants: struct, with fields:
% scalingConstants.c_ref
% scalingConstants.T_ref
% scalingConstants.N_A
% scalingConstants.e
% scalingConstants.k
% scalingConstants.A.phiref
% scalingConstants.C.phiref
% scalingConstants.Voff_ref
% scalingConstants.A.csmax
% scalingConstants.C.csmax
% scalingConstants.A.csref
% scalingConstants.C.csref
% scalingConstants.A.C
% the meaning of each field mathes that of the corresponding variable in MPET 
%%
scalingConstants.c_ref = 1000;
scalingConstants.T_ref = 298;
scalingConstants.N_A = 6.022e23;
scalingConstants.e = 1.602e-19;
scalingConstants.k = 1.381e-23;

scalingConstants.A.phiref=-batteryData.A.muRef;
scalingConstants.C.phiref=-batteryData.C.muRef;

scalingConstants.Voff_ref=scalingConstants.C.phiref-scalingConstants.A.phiref;

scalingConstants.A.csmax=batteryData.A.rho_s/scalingConstants.N_A;
scalingConstants.C.csmax=batteryData.C.rho_s/scalingConstants.N_A;

scalingConstants.A.csref=(1/batteryData.A.type)*scalingConstants.A.csmax;
scalingConstants.C.csref=(1/batteryData.C.type)*scalingConstants.C.csmax;


scalingConstants.A.C=scalingConstants.e* batteryData.A.L * (1 - batteryData.A.poros)*batteryData.A.P_L *batteryData.A.rho_s;
end