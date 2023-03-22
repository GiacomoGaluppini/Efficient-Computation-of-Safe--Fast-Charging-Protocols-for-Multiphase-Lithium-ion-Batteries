function plotProtocolLegend(OMnames,OMcolors,code)
%plotProtocolLegend(OMnames,OMcolors,code)
% Plots a legend associating operating modes to colours
%Inputs:
% OMnames: cell array of strings, names of available battery operating modes
% OMcolors: cell array of strings, codes for matlab colours to be
% associated with each battery operating mode in OMnames
% code: empty or cell array of strings, codes for operating modes in a
% charging protocol. If empty, plot all available operating modes,
% otherwise plot just those used in the charging protocol
%%
fname='ProtocolLegend';

if ~isempty(code)
    fname=[code,'_',fname];
end

if ~isempty(code)
    usedModes=[{'Start'} strsplit(code,'-')];
    usedIdxs=ismember(OMnames,usedModes);
    OMnames=OMnames(usedIdxs);
    OMcolors=OMcolors(usedIdxs);
end
n=length(OMnames);

x = [1.25 1.5 1.5 1.25];
y = [1 1 1.75 1.75];


for i=1:n
    h=subplot(1,n,i);
    p=patch(x,y,OMcolors{i});
    p.FaceAlpha=0.15;
    p.LineWidth=1;
    h.XTick=[];
    h.YTick=[];
    h.XLabel.String=OMnames{i};
    h.FontSize=16;
    axis tight
end

f=gcf;
f.Name=fname;
set(f,'Position',[10 10 100+n*50 150])
% exportgraphics(f,'ProtocolLegend.eps','ContentType','image','Resolution',400)
    

end

