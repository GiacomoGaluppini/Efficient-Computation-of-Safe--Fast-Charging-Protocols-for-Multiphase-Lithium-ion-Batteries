function [MultiPathStruct_p,MultiPathStruct_m] = createMultiplePath4FD(PathStruct,numParams)
% [MultiPathStruct_p,MultiPathStruct_m] = createMultiplePath4FD(PathStruct,numParams)
% Update paths to mpet config folders used to parallelize computation of derivatives via central finitie
% difference f'(x)=f(xp)-f(xm)/(xp-xm)
%Inputs:
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
    MultiPathStruct_p(i)=PathStruct;
    MultiPathStruct_p(i).configFolder=[MultiPathStruct_p(i).configFolder,'_wp',num2str(i)];
    MultiPathStruct_p(i).outputFolder=[MultiPathStruct_p(i).outputFolder,'_wp',num2str(i)];

    MultiPathStruct_p(i).outputFolder_absPath=[MultiPathStruct_p(i).outputFolder_absPath,'_wp',num2str(i)];

    
    MultiPathStruct_m(i)=PathStruct;
    MultiPathStruct_m(i).configFolder=[MultiPathStruct_m(i).configFolder,'_wm',num2str(i)];
    MultiPathStruct_m(i).outputFolder=[MultiPathStruct_m(i).outputFolder,'_wm',num2str(i)];
    
    MultiPathStruct_m(i).outputFolder_absPath=[MultiPathStruct_m(i).outputFolder_absPath,'_wm',num2str(i)];

end
end

