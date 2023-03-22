function setOutFolderAsPrevDir4FD(MultiPathStruct_p,MultiPathStruct_m,setFalse)
% setOutFolderAsPrevDir4FD(MultiPathStruct_p,MultiPathStruct_m,setFalse)
% set the MPET main configuration files pointed in MultiPathStruct_p and MultiPathStruct_m so that the
% MPET output folder is also used as continuation folder ('prevDir') to resume simulations
%Inputs:
% MultiPathStruct_p: struct array, with reuired paths to python, mpetrun and mpetplot,
% as well as paths to configuration folders and configuration filenames (see @createMultipleConfigFolders4FD)
% MultiPathStruct_m: struct array, with reuired paths to python, mpetrun and mpetplot,
% as well as paths to configuration folders and configuration filenames (see @createMultipleConfigFolders4FD)
% setFalse: bool, set to true or 1 to start fresh simulations
%%
for i=1:length(MultiPathStruct_p)
    setOutFolderAsPrevDir(MultiPathStruct_p(i),setFalse)
end
for i=1:length(MultiPathStruct_m)
    setOutFolderAsPrevDir(MultiPathStruct_m(i),setFalse)
end


end

