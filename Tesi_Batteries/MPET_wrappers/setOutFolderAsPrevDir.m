function setOutFolderAsPrevDir(PathStruct,setFalse)
% setOutFolderAsPrevDir(PathStruct,setFalse)
% set the MPET main configuration file pointed in PathStruct so that the
% MPET output folder is also used as continuation folder ('prevDir') to resume simulations 
%Inputs:
% PathStruct: struct, with reuired paths to python, mpetrun and mpetplot,
% as well as paths to configuration folders and configuration filenames (see @setPaths)
% setFalse: bool, set to true or 1 to start a fresh simulation
%%
ParType={'M'};
ParName={'prevDir'};
if setFalse
    ParVal={'false'};
else
    ParVal={PathStruct.outputFolder_absPath};
end
[ParamStruct] = createParamStruct(ParVal,ParName,ParType);
setConfigurationFiles(PathStruct,ParamStruct);

end

