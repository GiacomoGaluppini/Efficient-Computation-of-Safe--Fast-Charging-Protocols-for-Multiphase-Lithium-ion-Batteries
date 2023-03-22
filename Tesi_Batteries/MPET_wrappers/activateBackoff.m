function activateBackoff(PathStruct,setFalse)
% activateBackoff(PathStruct,setFalse)
% set backoff option on the MPET main configuration file pointed in PathStruct
%Inputs:
% PathStruct: struct, with reuired paths to python, mpetrun and mpetplot,
% as well as paths to configuration folders and configuration filenames (see @setPaths)
% setFalse: bool, set to true or 1 to deactivate backoff in MPET
%%
ParType={'M','M'};
ParName={'useBackoff','backoffFile'};
ParVal={'true','backoffs.mat'};
if setFalse
    ParVal{1}='false';
end

[ParamStruct] = createParamStruct(ParVal,ParName,ParType);
setConfigurationFiles(PathStruct,ParamStruct);

end

