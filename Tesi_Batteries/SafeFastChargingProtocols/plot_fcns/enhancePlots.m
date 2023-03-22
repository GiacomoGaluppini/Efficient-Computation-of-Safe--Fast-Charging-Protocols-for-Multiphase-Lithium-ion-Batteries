function enhancePlots(t,last_constraint,h,OMcolors)
% enhancePlots(t,last_constraint,h,colori)
% Enhance plots of MPET outputs with information about the active operating
% mode at each instant t
%Inputs:
% t: array, with time samples from MPET
% last_constraint: array, last active constraint at each time sample in t
% (see@ MPET)
% h: figure handle, handle to current figure to be enhanced
% OMcolors: cell array of strings, codes for matlab colours to be
% associated with each battery operating mode (see @setAvailableOperatingModes)
%%
last_constraint=floor(abs(last_constraint));

switchIdxs=[1 find(diff(last_constraint)~=0) length(last_constraint)];

for i=1:length(h)
    try
        axes(h(i))
        hold on
        for j=1:length(switchIdxs)-1
            x=[t(switchIdxs(j)) t(switchIdxs(j+1)) t(switchIdxs(j+1)) t(switchIdxs(j))];
            Ylim=h(i).YLim;
            y=[h(i).YLim(1)-1e5 h(i).YLim(1)-1e5 h(i).YLim(2)+1e5 h(i).YLim(2)+1e5];
            idxProtocol=last_constraint(switchIdxs(j+1))+1;
            p=patch(x,y,OMcolors{idxProtocol});
            set(p,'FaceAlpha',0.1);
            h(i).YLim=Ylim;
            h(i).XLim=[0 t(end)];
        end
    catch
    end
end
end

