function [PathStruct,MainFolder] = setPaths(PC,configFolder)
%[PathStruct,MainFolder] = setPaths(PC,configFolder)
% Create Path structure based on user and MPET configuration folder
% Input:
% PC: string, defining the pc using the code (useful for multiple pc access when code is on cloud).
% configFolder: string, path to the desired MPET configuration folder
% Output:
% PathStruct: struct, with the following fields:
% PathStruct.PY: string, path to python.exe
% PathStruct.MPETrun=string, path to mpetrun.py
% PathStruct.MPETplot=string, path to mpetplot.py
% PathStruct.configFolder=string, path to configFolder
% PathStruct.configFileMain=string, input_params_system file name
% PathStruct.configFileCathode=string, input_params_c file name
% PathStruct.configFileAnode=string, input_params_a file name
% PathStruct.historyFolder=string, path to history folder
% PathStruct.outputFolder=string, path to simout folder
% MainFolder string, path to main folder with matlab code

%%

switch lower(PC)
    case 'giek'
        PathStruct.PY='C:\Users\Giek\AppData\Local\Programs\Python\Python37\python.exe';
        PathStruct.MPETrun='C:\Users\Giek\AppData\Local\Programs\Python\Python37\Scripts\mpetrun.py';
        PathStruct.MPETplot='C:\Users\Giek\AppData\Local\Programs\Python\Python37\Scripts\mpetplot.py';
        
        MainFolder='D:\Dropbox\Tesi_Batteries\Identifiability Analysis';
        
        PathStruct.path2Dataset.path1='D:\Materiale Batterie\Batterie_Dataset\2017-05-12_batchdata_updated_struct_errorcorrect';
        PathStruct.path2Dataset.path2='D:\Materiale Batterie\Batterie_Dataset\2017-06-30_batchdata_updated_struct_errorcorrect';
        PathStruct.path2Dataset.path3='D:\Materiale Batterie\Batterie_Dataset\2018-04-12_batchdata_updated_struct_errorcorrect';
      
      case 'tower'
        PathStruct.PY='C:\Users\Windows\AppData\Local\Programs\Python\Python37\python.exe';
        PathStruct.MPETrun='C:\Users\Windows\AppData\Local\Programs\Python\Python37\Scripts\mpetrun.py';
        PathStruct.MPETplot='C:\Users\Windows\AppData\Local\Programs\Python\Python37\Scripts\mpetplot.py';
        
        MainFolder='C:\Users\Windows\Documents\MATLAB\Tesi_Batteries\Identifiability Analysis';
        
      case 'towerdropbox'
        PathStruct.PY='C:\Users\Windows\AppData\Local\Programs\Python\Python37\python.exe';
        PathStruct.MPETrun='C:\Users\Windows\AppData\Local\Programs\Python\Python37\Scripts\mpetrun.py';
        PathStruct.MPETplot='C:\Users\Windows\AppData\Local\Programs\Python\Python37\Scripts\mpetplot.py';
        
        MainFolder='C:\Users\Windows\Dropbox\Tesi_Batteries\Identifiability Analysis';

    case 'braatz'
        PathStruct.PY='C:\Users\galuppin\AppData\Local\Programs\Python\Python37\python.exe';
        PathStruct.MPETrun='C:\Users\galuppin\AppData\Local\Programs\Python\Python37\Scripts\mpetrun.py';
        PathStruct.MPETplot='C:\Users\galuppin\AppData\Local\Programs\Python\Python37\Scripts\mpetplot.py';
        
        
        MainFolder='C:\Users\galuppin\Documents\MATLAB\Tesi_Batteries\Identifiability Analysis';
        
        PathStruct.path2Dataset.path1='D:\galuppin\Batterie_Dataset\2017-05-12_batchdata_updated_struct_errorcorrect';
        PathStruct.path2Dataset.path2='D:\galuppin\Batterie_Dataset\2017-06-30_batchdata_updated_struct_errorcorrect';
        PathStruct.path2Dataset.path3='D:\galuppin\Batterie_Dataset\2018-04-12_batchdata_updated_struct_errorcorrect';
        
end

PathStruct.configFolder=configFolder;
PathStruct.configFileMain='input_params_system.cfg';
PathStruct.configFileCathode='input_params_c.cfg';
PathStruct.configFileAnode='input_params_a.cfg';


PathStruct.historyFolder='./history';
PathStruct.outputFolder='./simout';
end


