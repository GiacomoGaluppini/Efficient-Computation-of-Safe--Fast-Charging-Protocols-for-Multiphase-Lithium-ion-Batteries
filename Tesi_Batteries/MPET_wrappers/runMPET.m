function [status] = runMPET(PathStruct,clearOutputFolder,varargin)
%[status] = runMPET(PathStruct,clearOutputFolder,varargin)
%Run a simulation on MPET (requires specific MPET version!)
% Inputs:
% PathStruct: struct. with reuired paths to python, mpetrun and mpetplot,
% as well as paths to configuration folders and configuration filenames (see @setPaths)
% clearOutputFolder: bool, set to true/1 to clear the content of the mpet output
% folder before running a simulation
% Optional Inputs:
% verbose: bool, set to false/0 to redirect python stdout and stderr to files in the configuration folder
% timeout: double, timeout for mpet execution. If stopped, Mpet will not save results.
% Outputs:
% status: bool, true/1 if errors occur during the mpet simulation
%%
switch nargin
    case 2
        verbose=0;
        timeout=1e20;
    case 3
        verbose=varargin{1};
        timeout=1e20;
    case 4
        verbose=varargin{1};
        timeout=varargin{2};
        
        if timeout==Inf || timeout==0
            timeout=1e20;
        end
     
end

%%

arg1=PathStruct.PY;
arg2=PathStruct.MPETrun;
arg3=[PathStruct.configFolder,'/',PathStruct.configFileMain];
arg4=PathStruct.outputFolder;

if clearOutputFolder
    delete([PathStruct.outputFolder,'/*']);
end

systemCommand = [arg1,' ',arg2,' ',arg3,' ', arg4];

if ~verbose 
        systemCommand = [systemCommand ' >',PathStruct.configFolder,'/null 2>&1'];
end


systemCommand = [systemCommand,' ', num2str(timeout)];

if isunix
    keyboard
    systemCommand = [PathStruct.venv,'; ',systemCommand];
end


system(systemCommand);

if ~verbose 
[error]=checkForError(PathStruct);
else
    error=0;
end

if error
    status=1;
    warning('error running MPET')
else
    status=0;
end

end


function [error]=checkForError(PathStruct)
output=fileread([PathStruct.configFolder,'/null']);

error = (contains(output,'FAIL') ||...
    contains(output,'failed')) || contains(output,'cowardly') ||...
    contains(output,'dastardly');

end