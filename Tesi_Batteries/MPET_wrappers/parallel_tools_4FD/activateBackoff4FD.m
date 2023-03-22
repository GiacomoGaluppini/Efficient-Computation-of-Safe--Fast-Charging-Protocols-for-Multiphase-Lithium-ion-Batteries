function activateBackoff4FD(MultiPathStruct_p,MultiPathStruct_m,setFalse)
% activateBackoff4FD(MultiPathStruct_p,MultiPathStruct_m,setFalse)
% set backoff option on the MPET main configuration files pointed in
% MultiPathStruct_p and MultiPathStruct_m
%Inputs:
% MultiPathStruct_p: struct array, with reuired paths to python, mpetrun and mpetplot,
% as well as paths to configuration folders and configuration filenames (see @createMultipleConfigFolders4FD)
% MultiPathStruct_m: struct array, with reuired paths to python, mpetrun and mpetplot,
% as well as paths to configuration folders and configuration filenames (see @createMultipleConfigFolders4FD)
% setFalse: bool, set to true or 1 to deactivate backoff in MPET
%%
for i=1:length(MultiPathStruct_p)
    activateBackoff(MultiPathStruct_p(i),setFalse)
end
for i=1:length(MultiPathStruct_m)
    activateBackoff(MultiPathStruct_m(i),setFalse)
end

end

