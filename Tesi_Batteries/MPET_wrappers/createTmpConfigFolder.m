function [PathStruct] = createTmpConfigFolder(PathStruct,varargin)
%[PathStruct] = createTmpConfigFolder(PathStruct,varargin)
% Create a temporary copy of mpet config folder
% Inputs:
% PathStruct: struct, with reuired paths to python, mpetrun and mpetplot,
% as well as paths to configuration folders and configuration filenames (see @setPaths)
% Optional Inputs:
% suffix: string, suffix for the new folder filename (defaults to 'tmp')
%Outputs:
% PathStruct: PathStruct from Inputs, updated with path to the new
% configuration folder 


%%
if nargin==2
    suffix=varargin{1};
else
    suffix='tmp';
end
%%

tmpConfig=[PathStruct.configFolder,suffix];
copyfile(PathStruct.configFolder,tmpConfig);
PathStruct.configFolder=tmpConfig;
end

