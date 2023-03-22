function [AnodePS,CathodePS] = readDiscretizationData(PathStruct)
% [AnodePS,CathodePS] = readDiscretizationData(PathStruct)
% Read data from mpet discretization data output file and output actual particle
% sizes
% Inputs:
% PathStruct: struct. with required paths to python, mpetrun and mpetplot,
% as well as paths to configuration folders and configuration filenames (see @setPaths)
% Outputs:
% AnodePS: matrix, anode actual particle sizes
% CathodePS: matrix, cathode actual particle sizes
%%
arg1=PathStruct.PY;
arg2=PathStruct.MPETplot;
arg3=PathStruct.outputFolder;

systemCommand = [arg1,' ', arg2,' ',arg3, ' text',' >',PathStruct.configFolder,'/null2 2>&1'];
%systemCommand = [arg1,' ', arg2,' ',arg3, ' text'];

if isunix
    keyboard
    systemCommand = [PathStruct.venv,'; ',systemCommand];
end

[status] = system(systemCommand);

if status~=0
    warning('error reading MPET data')
else
    
    fileCell={};
    fid = fopen([PathStruct.outputFolder,'/discData.txt']);
    tline = fgetl(fid);
    while ischar(tline)
        fileCell{end+1} = tline;
        tline= fgetl(fid);
    end
    fclose(fid);
    
    idxCPS_start=find(contains(fileCell,'Cathode particle sizes [m]'))+1;
    idxCPS_end=find(contains(fileCell,'Cathode particle number of discr. points'))-2;
    idxAPS_start=find(contains(fileCell,'Anode particle sizes [m]'))+1;
    idxAPS_end=find(contains(fileCell,'Anode particle number of discr. points'))-2;
    
    CathodePS=[];
    for i=idxCPS_start:idxCPS_end
        fileline=fileCell{i};
        if ~isempty(fileline)
            CathodePS=[CathodePS;str2double(strsplit(fileline,','))];
        end
    end
    
    AnodePS=[];
    for i=idxAPS_start:idxAPS_end
        fileline=fileCell{i};
        if ~isempty(fileline)
            AnodePS=[AnodePS;str2double(strsplit(fileline,','))];
        end
    end
    
end

end

