function [Amap,Smap,Cmap] = createElectrodeColormap(N_a,N_s,N_c,L_a,L_s,L_c)
% [Amap,Smap,Cmap] = createElectrodeColormap(N_a,N_s,N_c,L_a,L_s,L_c)
% Creates and plots a colormap for anode, cathode and separator to identify
% position of outputs based on colour intensity
%Inputs:
% N_a: scalar, number of volumes in the anode
% N_s: scalar, number of volumes in the separator
% N_c: scalar, number of volumes in the cathode
% L_a: scalar, length of the anode
% L_s: scalar, length of the separator
% L_c: scalar, length of the cathode
%Outputs:
% Amap: color look-up table (see @colormap) for the anode
% Smap: color look-up table (see @colormap) for the separator
% Cmap: color look-up table (see @colormap) for the cathode
%%
f=gcf;
f.Name='Electrode Colormap Anode';
[Amap] = createElectrodeColormap_util(N_a,L_a,'winter','Anode');
set(f,'Position',[11.8000   72.6000  600.0000  272.8000]);
% exportgraphics(f,'ElectrodeColormap_a.eps','ContentType','image','Resolution',400)
  
f=figure(f.Number+1);
f.Name='Electrode Colormap Separator';
[Smap] = createElectrodeColormap_util(N_s,L_s,'gray','Separator');
set(f,'Position',[11.8000   72.6000  600.0000  272.8000]);
% exportgraphics(f,'ElectrodeColormap_s.eps','ContentType','image','Resolution',400)
  
f=figure(f.Number+1); 
f.Name='Electrode Colormap Cathode';
[Cmap] = createElectrodeColormap_util(N_c,L_c,'autumn','Cathode');
set(f,'Position',[11.8000   72.6000  600.0000  272.8000]);
% exportgraphics(f,'ElectrodeColormap_c.eps','ContentType','image','Resolution',400)
  

end

function [map] = createElectrodeColormap_util(N,L,colormapstring,electrodestring)
% [map] = createElectrodeColormap_util(N,L,colormapstring,electrodestring)
% Creates and plots a colormap for anode, cathode and separator to identify
% position of outputs based on colour intensity
%Inputs:
% N:  scalar, number of volumes in the electrode
% L: scalar, length of the electrode
% colormapstring: string, identifying a valid matlab colormap (see @colormap)
% electrodestring: string, identifying an electrode (a,c,s)
%Outputs:
% map: color look-up table (see @colormap)
%%
t = tiledlayout(1,1);
ax1 = axes(t);
map = colormap(colormapstring);
map = map(round(linspace(1,256,N)),:);
imagesc(1:N)
xlabel('$Volume$','FontSize',16)
ax1.XLabel.Interpreter='latex';
ax1.YTickLabel=[];
ax1.FontSize=16;
xt=ax1.XTick;
xt=linspace(1,N,5);
xt=unique(ceil(xt));
ax1.XTick=xt;

L=L*1e6;
ax2 = axes(t);
lt=(L./N).*xt;
plot(linspace(0,L,256),100*ones(1,256))
xlabel('$Position\;[\mu m]$','FontSize',16)
ax2.XLabel.Interpreter='latex';
title(electrodestring,'FontSize',16)
ax2.YTickLabel=[];
ax2.FontSize=16;
ax2.XAxisLocation = 'top';
ax2.YAxisLocation = 'right';
ax2.XLim=[0 L];
ax2.XTick=lt-lt(1)*0.5;
ax2.YLim=[-0.5 0.5];


ax2.Color = 'none';
ax1.Box = 'off';
ax2.Box = 'off';


end
