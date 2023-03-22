function [poolsize] = createParallelConfigFolders(PathStruct)
% [poolsize] = createParallelConfigFolders(PathStruct)
% Create a set of mpet configuration folder copies for parallel code execution
% Inputs:
% PathStruct: struct. with reuired paths to python, mpetrun and mpetplot,
% as well as paths to configuration folders and configuration filenames (see @setPaths)
% Outputs:
% poolsize: scalar, number of active parallel pools detected
%%
p = gcp('nocreate'); % If no pool, do not create new one.
if isempty(p)
    poolsize = 0;
else
    poolsize=p.NumWorkers;
    for i=1:poolsize
        source=PathStruct.configFolder;
        destination=[source,'_w',num2str(i)];
        flag=copyfile(source,destination);
    end
end


end

