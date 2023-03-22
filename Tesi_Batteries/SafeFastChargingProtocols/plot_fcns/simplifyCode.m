function [codeSimplified] = simplifyCode(code)
% [codeSimplified] = simplifyCode(code)
% Simplifies code for charging protocol by removing repeations of opearting
% modes
%Inputs:
% code: string, codes of operating modes summarizing the protocol (see @generateprotocolCode)
%Outputs:
% codeSimplified: string, codes of operating modes summarizing the protocol
% without repetition of used operating modes (e.g. CC-CV-CC-CV-CP  is simplified as CC-CV-CP)
%%
    codeNoRep=unique(strsplit(code,'-'));
    codeSimplified=[];
    
    for i=1:length(codeNoRep)
        codeSimplified=[codeSimplified,codeNoRep{i}];
        if i<length(codeNoRep)
            codeSimplified=[codeSimplified,'-'];
        end
    end
end

