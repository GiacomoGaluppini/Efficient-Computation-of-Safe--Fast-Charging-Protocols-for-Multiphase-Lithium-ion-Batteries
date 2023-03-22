close all
clear all
clc


figure(1212)
[nomiProtocolli,coloriProtocolli] = setAvailableOperatingModes();

%% script options

salvaRisu=0;
separaPlot=0;
detailedProtocol=0;
%%
PathStruct.PY='C:\Users\Giek\AppData\Local\Programs\Python\Python37\python.exe';
MPETpath='C:\Users\Giek\Documents\EclipseWorkspace\mpet-dev-optimalcontrol\';
% MPETpath='C:\Users\Giek\Documents\EclipseWorkspace\mpet-dev-stachasticoptimalcontrol\';
PathStruct.MPETplot=[MPETpath,'bin\mpetplot.py'];

%%%%%%%%%%  results just generated  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% PathStruct.outputFolder=[MPETpath,'simout'];
% PathStruct.configFolder=[MPETpath,'configs'];
% PathStruct.configFileMain='params_system_A123LFP_optimalcontrol.cfg';

%%%%%%%%%%  archived results %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
ResultsPath='D:\Dropbox\Tesi_Batteries\Results\SafeFastChargingProtocols\';
PathStruct.outputFolder=[ResultsPath,'CC-CSe-CCs\simout'];
PathStruct.configFolder=PathStruct.outputFolder;
PathStruct.configFileMain='input_params_system.cfg';
%% READ SPECS

[V_ub,I_ub,P_ub,LPOverpot_lb,Ce_lb,Ce_ub,Cs_ub,T_ub,ffrac_Tend,Vmax,deadband] = readConfigParams([PathStruct.configFolder,'\',PathStruct.configFileMain],...
    'V_ub','I_ub','P_ub','LPOverpot_lb','Ce_lb','Ce_ub','Cs_ub','T_ub','ffrac_Tend','Vmax','deadband');

[Nvol_a,Nvol_c,Nvol_s,Npart_a,Npart_c,L_a,L_s,L_c,tend] = readConfigParams([PathStruct.configFolder,'\',PathStruct.configFileMain],...
    'Nvol_a','Nvol_c','Nvol_s','Npart_a','Npart_c','L_a','L_s','L_c','tend');

figure(2000)
[Amap,Smap,Cmap] = createElectrodeColormap(Nvol_a,Nvol_s,Nvol_c,L_a,L_s,L_c);

dbf_plus=1+0.01*deadband;
dbf_minus=1-0.01*deadband;
%% get scaling constants

batteryData.A.rho_s = 1.7e28;
batteryData.C.rho_s = 1.3793e28;

batteryData.A.type=1;%CHR
batteryData.C.type=1;%ACR

batteryData.A.L=38e-6;
batteryData.A.poros=0.414;
batteryData.A.P_L=0.9;


batteryData.A.muRef=31.03379049;%CHR
batteryData.C.muRef=133.29084007;

[scalingConstants]=getScalingConstants(batteryData);

%% main plots

[t,V,I,status,ffrac_c,ffrac_a,J] = readDischargeCurve(PathStruct);

f1=figure(1)

h(1)=subplot(4,2,1);
plot(t,ffrac_a,'k','LineWidth',2)
hold on
plot(t(end),ffrac_Tend,'or','LineWidth',2,'MarkerSize',8)
xlabel('$t\;[s]$','Interpreter','latex')
ylabel('$SOC\;[-]$','Interpreter','latex')
grid on
h(1).YLim=[0 0.9];
ytickformat('%,.2f')

h(2)=subplot(4,2,2);
plot(t,V,'k','LineWidth',2)
hold on
plot([t(1) t(end)],[V_ub V_ub],'--r','LineWidth',2)
plot([t(1) t(end)],[V_ub V_ub]*dbf_plus,'--r','LineWidth',0.5)
xlabel('$t\;[s]$','Interpreter','latex')
ylabel('$V\;[V]$','Interpreter','latex')
grid on
h(2).YLim=[2 3.8];
ytickformat('%,.2f')

h(3)=subplot(4,2,3);
plot(t,-I,'k','LineWidth',2)
hold on
plot([t(1) t(end)],-[I_ub I_ub],'--r','LineWidth',2)
plot([t(1) t(end)],-[I_ub I_ub]*dbf_plus,'--r','LineWidth',0.5)
xlabel('$t\;[s]$','Interpreter','latex')
ylabel('$I\;[Crate]$','Interpreter','latex')
grid on
h(3).YLim=[0 9];
ytickformat('%,.0f')

h(4)=subplot(4,2,4);
plot(t,-V.*J,'k','LineWidth',2)
hold on
plot([t(1) t(end)],[P_ub P_ub],'--r','LineWidth',2)
plot([t(1) t(end)],[P_ub P_ub]*dbf_plus,'--r','LineWidth',0.5)
xlabel('$t\;[s]$','Interpreter','latex')
ylabel('$P\;[W/m^2]$','Interpreter','latex')
grid on
h(4).YLim=[0 480];
ytickformat('%,.0f')

%% main plots 2
load([PathStruct.outputFolder,'\output_data.mat'])

etaPlating_a=[];
try
    factor=scalingConstants.e/(scalingConstants.k*scalingConstants.T_ref);
    h(5)=subplot(4,2,5);
    cla
    for i=0:Nvol_a-1
        vol_col=Amap(i+1,:);
        for j=0:Npart_a-1
            %tmp=eval(['partTrodeavol',num2str(i),'partplating',num2str(j),'_etaPlating'])/factor;
            tmp=eval(['partTrodeavol',num2str(i),'part',num2str(j),'_etaPlating'])/factor;
            etaPlating_a=[etaPlating_a tmp'];
            plot(t,tmp,'Color',vol_col,'LineWidth',2)
            hold on
        end
    end
    plot([t(1) t(end)],[LPOverpot_lb LPOverpot_lb],'--r','LineWidth',2)
    plot([t(1) t(end)],[LPOverpot_lb LPOverpot_lb]*dbf_minus,'--r','LineWidth',0.5)
    %plot([t(1) t(end)],[0 0],':m','LineWidth',1,'color',[0.4940 0.1840 0.5560])
    xlabel('$t\;[s]$','Interpreter','latex')
    ylabel('$\eta_p\;[V]$','Interpreter','latex')
    grid on
    h(5).YLim=[-0.1 0.8];
    ytickformat('%,.2f')
catch
end

try
    T_lyte=[T_lyte_a T_lyte_s T_lyte_c]*scalingConstants.T_ref;
    T_lyte_mean=mean(T_lyte,2);
    h(6)=subplot(4,2,6);
    for i=1:Nvol_c
        vol_col=Cmap(i,:);
        plot(t,T_lyte_c(:,i)*scalingConstants.T_ref,':g','LineWidth',2,'Color',vol_col)
        hold on
    end
    for i=1:Nvol_a
        vol_col=Amap(i,:);
        plot(t,T_lyte_a(:,i)*scalingConstants.T_ref,':','LineWidth',2,'Color',vol_col)
    end
    plot(t,T_lyte_mean,':k','LineWidth',4)
    hold on
    plot([t(1) t(end)],[T_ub T_ub],'--r','LineWidth',2)
    plot([t(1) t(end)],[T_ub T_ub]*dbf_plus,'--r','LineWidth',0.5)
    ylabel('$T_{avg}\;[K]$','Interpreter','latex')
    xlabel('$t\;[s]$','Interpreter','latex')
    grid on
    h(6).YLim=[295 325];
    ytickformat('%,.0f')
catch
end

h(7)=subplot(4,2,7);
cla
for i=1:Nvol_c
    vol_col=Cmap(i,:);
    plot(t,c_lyte_c(:,i)*scalingConstants.c_ref,':g','LineWidth',2,'Color',vol_col)
    hold on
end
for i=1:Nvol_a
    vol_col=Amap(i,:);
    plot(t,c_lyte_a(:,i)*scalingConstants.c_ref,':','LineWidth',2,'Color',vol_col)
end
plot([t(1) t(end)],[Ce_lb Ce_lb],'--r','LineWidth',2)
plot([t(1) t(end)],[Ce_lb Ce_lb]*dbf_minus,'--r','LineWidth',0.5)
plot([t(1) t(end)],[Ce_ub Ce_ub],'--r','LineWidth',2)
plot([t(1) t(end)],[Ce_ub Ce_ub]*dbf_plus,'--r','LineWidth',0.5)
xlabel('$t\;[s]$','Interpreter','latex')
ylabel('$C_e\;[Kmol/m^3]$','Interpreter','latex')
ytickformat('%,.2f')
h(7).YLim=[0.25 1.75]*1000;
h(7).YTickLabel= h(7).YTick/1000;
grid on

h(8)=subplot(4,2,8);
cla
for i=0:Nvol_a-1
    vol_col=Amap(i+1,:);
    for j=0:Npart_a-1
        plot(t,eval(['partTrodeavol',num2str(i),'part',num2str(j),'_cbar'])*scalingConstants.A.csref,':','LineWidth',2,'Color',vol_col)
        hold on
    end
end
for i=0:Nvol_c-1
    vol_col=Cmap(i+1,:);
    for j=0:Npart_c-1
        plot(t,eval(['partTrodecvol',num2str(i),'part',num2str(j),'_cbar'])*scalingConstants.C.csref,':','LineWidth',2,'Color',vol_col)
        hold on
    end
end
plot([t(1) t(end)],[Cs_ub Cs_ub],'--r','LineWidth',2)
plot([t(1) t(end)],[Cs_ub Cs_ub]*dbf_plus,'--r','LineWidth',0.5)
xlabel('$t\;[s]$','Interpreter','latex')
ylabel('$C_s\;[Kmol/m^3]$','Interpreter','latex')
grid on
ytickformat('%,.0f')
h(8).YLim=[0 30]*1000;
h(8).YTickLabel= h(8).YTick/1000;
linkaxes(h,'x')


%% plot protocol
figure(2)
plot(t,floor(abs(last_constraint)),'-k','LineWidth',2)
grid on
xlabel('$t\;[s]$','Interpreter','latex')
ylabel('$Operating\;Mode$','Interpreter','latex')

ax=gca;
ax.YLim=[-1 8];
ax.YTick=[0:7];
ax.YTickLabel=nomiProtocolli;

h=[h ax];
linkaxes(h,'x')

if detailedProtocol
    figure(20)
    plot(t,last_constraint,':k','LineWidth',1)
    grid on
end
%% compute protocol code and performance metrics
[code,codeLong,charging_time,charge_completed,durations] = generateprotocolCode(last_constraint,t,ffrac_a,ffrac_Tend,nomiProtocolli);
% [code,codeLong,charging_time,charge_completed,durations] = generateprotocolCode(last_constraint,t,tend,nomiProtocolli);

if ~exist('T_lyte')
    T_lyte=[];
end
if ~exist('etaPlating_a')
    etaPlating_a=[];
end

% T_lyte_limit=320;
% etaPlating_limit=0;
% [metrics] = evaluateDegradationMetrics(t,T_lyte_mean,T_lyte_limit,etaPlating_a,etaPlating_limit);
% metrics.charging_time=charging_time;
% metrics.charge_completed=charge_completed;
% metrics
%% enhance plots

for i=1:8
    try
        h(i).YTick=linspace(min(h(i).YLim),max(h(i).YLim),4);
        if i==7 || i==8
            h(i).YTickLabel= h(i).YTick/1000;
        end
    catch
    end
end

h(5).YTick=sort([0 h(5).YTick])

enhancePlots(t,last_constraint,h,coloriProtocolli);

figure(2)
if charge_completed
    titoloProtocollo={codeLong;['Charging time=',num2str(charging_time),' s']};
else
    titoloProtocollo={code;['Charging not complete']};
end
title(titoloProtocollo)

figure(1213)
plotProtocolLegend(nomiProtocolli,coloriProtocolli,code)

%% separate plots if requested

if separaPlot
    for i=1:length(h)
        try
            
            idx=strfind(h(i).YLabel.String,'[');
            figname=h(i).YLabel.String(1:idx-2);
            figname=strrep(figname,'\','');
            figname=strrep(figname,'$','');
            figname=strrep(figname,';','');
            f_separate{i}=figure('Name',figname);
            
            copyobj(h(i),f_separate{i})
            
            set(f_separate{i}.Children,'position',[.12 .12 .78 .78])
            f_separate{i}.Position=[10 10 1200 500];
            
            title('')
            
            h_separate(i)=gca;
            h_separate(i).FontSize=16;
            h_separate(i).YLabel.FontSize=20;
            %         h_separate(i).YLabel.Position(1)=-75;
            h_separate(i).YLabel.Position(1)=-160;
            hold on
        catch
        end
    end
    
    linkaxes([h h_separate],'x')
end

%% save

if salvaRisu
    
    cartella=[code];
    [SUCCESS,MESSAGE]=mkdir(cartella);
    
    if contains(MESSAGE,'Directory already exists')
        keyboard
    end
    
    copyfile(PathStruct.outputFolder,[cartella,'/simout'])
    
    figure(1)
    savefig(gcf,[cartella,'/',code,'_all_plots'])
    exportgraphics(gcf,[cartella,'/',code,'_all_plots.eps'],'ContentType','image','Resolution',400)
    exportgraphics(gcf,[cartella,'/',code,'_all_plots.tiff'],'ContentType','image','Resolution',400)
    
    figure(2)
    savefig(gcf,[cartella,'/',code,'_protocol'])
    exportgraphics(gcf,[cartella,'/',code,'_protocol.eps'],'ContentType','image','Resolution',400)
    exportgraphics(gcf,[cartella,'/',code,'_protocol.tiff'],'ContentType','image','Resolution',400)
    
    if separaPlot
        for i=1:length(f_separate)
            try
                exportgraphics(f_separate{i},[cartella,'/',code,'_',f_separate{i}.Name,'.eps'],'ContentType','image','Resolution',400)
                exportgraphics(f_separate{i},[cartella,'/',code,'_',f_separate{i}.Name,'.tiff'],'ContentType','image','Resolution',400)
                
                savefig(f_separate{i},[cartella,'/',code,'_',f_separate{i}.Name])
            catch
            end
        end
    end
    
    exportgraphics(figure(1213),[cartella,'/',code,'_ProtocolLegend.eps'],'ContentType','image','Resolution',400)
    
    save([cartella,'/',code,'_alladata'])
    
    %     moviename=[cartella,'/',codice,'_movie']
    %     plotCmapMovie(PathStruct,20,'cbar',moviename,1,1)
    
else
    %     plotCmapMovie(PathStruct,10,'cbar',[],0,[])
    figure(1)
end


