function setParam(PathStruct,ParVal,ParName,ParType)
% setParam(PathStruct,ParVal,ParName,ParType)
% write desired parameter values in the MPET configuration files pointed in
% PathStruct
%Inputs:
% PathStruct: struct, with reuired paths to python, mpetrun and mpetplot,
% as well as paths to configuration folders and configuration filenames (see @setPaths)
% ParVal: array or cell array of scalars,  parameter values
% ParName: cell array of strings, parameter names
% ParType: cell array of strings, parameter file identifier (A,C,M)
%%
[ParamStruct] = createParamStruct(ParVal,ParName,ParType);
setConfigurationFiles(PathStruct,ParamStruct);

end