function [t,V,I,status,ffrac_c,ffrac_a,J] = readDischargeCurve(PathStruct)
%[t,V,I,status,ffrac_c,ffrac_a,J] = readGeneralData(PathStruct)
% Read data from mpet general data output file
%Input:
% PathStruct: struct. with reuired paths to python, mpetrun and mpetplot,
% as well as paths to configuration folders and configuration filenames (see @setPaths)
% Outputs:
% t: array, time from mpet general data
% V: array, voltage from mpet general data
% I: array, C rate from mpet general data
% status: bool, true/1 if errors occur during the mpet output file readout
% ffrac_c: array, cathode filling fraction from mpet general data
% ffrac_a: array, anode filling fraction from mpet general data
% J: array, current from mpet general data
%%
arg1=PathStruct.PY;
arg2=PathStruct.MPETplot;
arg3=PathStruct.outputFolder;

systemCommand = [arg1,' ', arg2,' ',arg3, ' text',' >',PathStruct.configFolder,'/null2 2>&1'];
%systemCommand = [arg1,' ', arg2,' ',arg3, ' text'];

if isunix
    keyboard
    systemCommand = [PathStruct.venv,'; ',systemCommand];
end

[status] = system(systemCommand);

if status~=0
    warning('error reading MPET data')
    t=nan;
    V=nan;
    I=nan;
    ffrac_c=nan;
else
    
    generalData = importResultFile([PathStruct.outputFolder,'/generalData.txt']);

    t=str2double(generalData.Times);
    V=str2double(generalData.VoltageV);
    I=str2double(generalData.CurrentCrate);
    J=str2double(generalData.CurrentAm2);
    ffrac_c=str2double(generalData.Fillingfractionofcathode);
    ffrac_a=str2double(generalData.Fillingfractionofanode);
end

end

