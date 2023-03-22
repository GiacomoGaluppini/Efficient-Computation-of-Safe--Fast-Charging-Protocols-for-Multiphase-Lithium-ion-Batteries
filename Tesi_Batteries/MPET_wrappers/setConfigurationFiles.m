function setConfigurationFiles(PathStruct,newPars)
% function setConfigurationFiles(PathStruct,newPars)
% Propely modify mpet configuration files to set the desired parameter set
% Inputs:
% PathStruct: struct. with required paths to python, mpetrun and mpetplot,
% as well as paths to configuration folders and configuration filenames (see @setPaths)
% newPars: struct, with param info from input as follows (see @createParamStruct):
% newPars.name=ParName
% newPars.val=ParVal
% newPars.type=ParType

%%
mainIdx=find(strcmp(upper({newPars.type}),'M')==1);
anodeIdx=find(strcmp(upper({newPars.type}),'A')==1);
cathodeIdx=find(strcmp(upper({newPars.type}),'C')==1);

for i=1:3
    
    switch i
        case 1
            if ~isempty(mainIdx)
                filepath=[PathStruct.configFolder,'/',PathStruct.configFileMain];
                setParamFile(filepath,newPars(mainIdx))
            end
        case 2
            if ~isempty(anodeIdx)
                filepath=[PathStruct.configFolder,'/',PathStruct.configFileAnode];
                setParamFile(filepath,newPars(anodeIdx))
            end
        case 3
            if ~isempty(cathodeIdx)
                filepath=[PathStruct.configFolder,'/',PathStruct.configFileCathode];
                setParamFile(filepath,newPars(cathodeIdx))
            end
    end
    

end

end

