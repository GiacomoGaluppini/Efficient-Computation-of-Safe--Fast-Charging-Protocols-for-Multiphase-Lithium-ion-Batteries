clear all
% close all
clc


%% run from config

[PathStruct,MainFolder] = setPaths('tower','.\configA123_optimalcontrol')


%% run
clearOutputFolder=1;
verbose=1;
[status] = runMPET(PathStruct,clearOutputFolder,verbose);

if status==0
    %% read results and plot
    
    [t,V,I,status,ffrac_c] = readDischargeCurve(PathStruct);
    
    figure(1)
    plot(t,V,'LineWidth',2)
    grid on
    xlabel('t [s]')
    ylabel('V [V]')
    
    
    figure(2)
    plot(t,I,'LineWidth',2)
    grid on
    xlabel('t [s]')
    ylabel('I [C rate]')


    
end

