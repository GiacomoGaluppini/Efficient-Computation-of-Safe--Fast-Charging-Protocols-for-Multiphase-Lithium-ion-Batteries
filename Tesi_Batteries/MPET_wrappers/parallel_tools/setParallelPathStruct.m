function [ParPathStruct, w_ID] = setParallelPathStruct(PathStruct)
% [ParPathStruct, w_ID] = setParallelPathStruct(PathStruct)
% Create Path struct for parallel code execution, based on current parallel worker
% identifier 
% Inputs:
% PathStruct: struct. with reuired paths to python, mpetrun and mpetplot,
% as well as paths to configuration folders and configuration filenames (see @setPaths)
% Outputs:
% ParPathStruct: struct, updated PathStruct from input, based on on current parallel worker
% identifier 
% w_ID: current parallel worker
% identifier 
%%
try
    t = getCurrentTask();
catch
    t=[];
end

if isempty(t)
    ParPathStruct=PathStruct;
    w_ID=[];
else
    w_ID=t.ID;
    ParPathStruct=PathStruct;
    ParPathStruct.configFolder = setParallelWorkerPath(PathStruct.configFolder,w_ID);
    ParPathStruct.outputFolder = setParallelWorkerPath(PathStruct.outputFolder,w_ID);
end

end


