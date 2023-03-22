function setParam4FD(MultiPathStruct_p,MultiPathStruct_m,ParVal,ParName,ParType)
% setParam4FD(MultiPathStruct_p,MultiPathStruct_m,ParVal,ParName,ParType)
% write desired parameter values in the MPET configuration files pointed in
% MultiPathStruct_p and MultiPathStruct_m
%Inputs:
% MultiPathStruct_p: struct array, with reuired paths to python, mpetrun and mpetplot,
% as well as paths to configuration folders and configuration filenames (see @createMultipleConfigFolders4FD)
% MultiPathStruct_m: struct array, with reuired paths to python, mpetrun and mpetplot,
% as well as paths to configuration folders and configuration filenames (see @createMultipleConfigFolders4FD)
% ParVal: array or cell array of scalars,  parameter values
% ParName: cell array of strings, parameter names
% ParType: cell array of strings, parameter file identifier (A,C,M)
%%

for i=1:length(MultiPathStruct_p)
    setParam(MultiPathStruct_p(i),ParVal,ParName,ParType)
end
for i=1:length(MultiPathStruct_m)
    setParam(MultiPathStruct_m(i),ParVal,ParName,ParType)
end
end


