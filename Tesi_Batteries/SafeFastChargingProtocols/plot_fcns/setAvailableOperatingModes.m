function [OMnames,OMcolors] = setAvailableOperatingModes()
% [OMnames,OMcolors] = setAvailableOperatingModes()
%Outputs:
% OMnames: cell array of strings, names of available battery operating modes
% OMcolors: cell array of strings, codes for matlab colours to be
% associated with each battery operating mode in OMnames
%%
OMnames={'Start','CC','CV','CP','CLO','CCe','CCs','CT'};
OMcolors={'w','r','b','y','g','c','k','m'};


plotProtocolLegend(OMnames,OMcolors,[])

end

