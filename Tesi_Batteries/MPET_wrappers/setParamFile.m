function setParamFile(filepath,newParsStruct)
% setParamFile(filepath,newPars)
% Write a new set of param values on an mpet configuration file
% Inputs:
% filepath: string, path to the desired mpet configuration file
% newParsStruct: struct, with param info from input as follows (see @createParamStruct):
% newParsStruct.name=ParName
% newParsStruct.val=ParVal
% newParsStruct.type=ParType
%%
[configFileCell] = readFile2Cell(filepath);
[configFileCell] = updateCellFile(configFileCell,newParsStruct);
writeCell2File(filepath,configFileCell);
end

