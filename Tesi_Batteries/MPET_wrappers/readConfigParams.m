function [varargout] = readConfigParams(filePath,varargin)
%  [varargout] = readConfigParams(filePath,varargin)
% Read a desired set of parameters from a desired mpet configuration file
% Inputs:
% filePath: string, path to mpet config file
% Optional Inputs:
% paramNames: series of strings, parameter names
% Optional Outputs:
% paramval: series of scalars, parameter values
%%

paramNames=varargin;
%%
[FileCell] = readFile2Cell(filePath);
%find comment lines
IndexComments = find(contains(FileCell,'#'));
FileCell(IndexComments)=[];

%%
paramval=cell(size(paramNames));
for i=1:length(varargin)
    idx=find(contains(FileCell,paramNames{i}));
    if ~isempty(idx)
    paramStr = FileCell{idx};
    [paramStr] = strsplit(paramStr, '=');
    paramval{i}=str2double(paramStr{2});
    else
        paramval{i}=NaN;
        warning([paramNames{i},' not found in the specified file'])
    end
end

varargout=paramval;
end

