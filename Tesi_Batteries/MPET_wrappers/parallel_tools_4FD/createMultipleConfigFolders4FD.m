function [MultiPathStruct_p,MultiPathStruct_m]=createMultipleConfigFolders4FD(PathStruct,numParams)
% [MultiPathStruct_p,MultiPathStruct_m]=createMultipleConfigFolders4FD(PathStruct,numParams)
% Create a temporary copies of mpet config folder to parallelize computation of derivatives via central finitie
% difference f'(x)=f(xp)-f(xm)/(xp-xm)
% Inputs:
% PathStruct: struct, with reuired paths to python, mpetrun and mpetplot,
% as well as paths to configuration folders and configuration filenames (see @setPaths)
% numParams: number of dimensions of the parameter space
%Outputs:
% MultiPathStruct_p: struct array, containing copies of PathStruct from Inputs, updated with path to the new
% configuration folder for positive perturbations
% MultiPathStruct_m: struct array, containing copies of PathStruct from Inputs, updated with path to the new
% configuration folder for negative perturbations
%%
for i=1:numParams
    source=PathStruct.configFolder;
    destination_p=[source,'_wp',num2str(i)];
    destination_m=[source,'_wm',num2str(i)];
    flag_p=copyfile(source,destination_p);
    flag_m=copyfile(source,destination_m);
end

[MultiPathStruct_p,MultiPathStruct_m] = createMultiplePath4FD(PathStruct,numParams);
    
end

