function [ParamStruct] = createParamStruct(ParVal,ParName,ParType)
% [ParamStruct] = createParamStruct(ParVal,ParName,ParType)
% Inputs: 
% ParVal: array or cell array of scalars,  parameter values
% ParName: cell array of strings, parameter names
% ParType: cell array of strings, parameter file identifier (A,C,M)
% Outputs:
% ParamStruct: struct, with param info from input as follows:
% ParamStruct.name=ParName
% ParamStruct.val=ParVal
% ParamStruct.type=ParType
%%

if length(ParVal)~=length(ParName) || length(ParVal)~=length(ParType) || length(ParType)~=length(ParName)
    error('ParVal,ParName and ParType must have the same dimensions')
end

%%

for i=1:length(ParVal)
    ParamStruct(i).name=ParName{i};
    
    if iscell(ParVal)
        ParamStruct(i).val=ParVal{i};
    else
        ParamStruct(i).val=ParVal(i);
    end
    
    ParamStruct(i).type=ParType{i};
end

end

