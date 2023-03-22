function [code,codeLong,charging_time,charge_completed,durations] = generateprotocolCode(last_constraint,t,ffrac_a,ffrac_Tend,names)
% [code,codeLong,charging_time,charge_completed,durations] = generateprotocolCode(last_constraint,t,ffrac_a,ffrac_Tend,names)
%Inputs:
% last_constraint: array, last active constraint at each time sample in t
% (see@ MPET)
% t: array, with time samples
% ffrac_a: array, filling fraction (see@ MPET) of the anode at each time sample in t
% ffrac_Tend: scalar, required filling fraction (see@ MPET) of the anode
% at the end of charging operations (terminal constraint)
% names: cell array of strings, wiht names of operating modes corresponding
% to numerical codes
%Outputs:
% code: string, codes of operating modes summarizing the protocol
% codeLong: string, codes of operating modes summarizing the protocol and
% duration of each operating mode
% charging_time: scalar, total charging time
% charge_completed: bool, true if charging was completed up to ffrac_Tend
% durations: cell array, duration of each operating mode
%%
last_constraint=floor(abs(last_constraint));
switchIdxs=[1 find(diff(last_constraint)~=0) length(last_constraint)];

if ffrac_a(end)>=ffrac_Tend
charge_completed=true;
else
    charge_completed=false;
end

code=[];
for j=1:length(switchIdxs)-1
    idxProtocol=last_constraint(switchIdxs(j+1))+1;
    if idxProtocol>1
        code=[code,names{idxProtocol}];
        if j<length(switchIdxs)-1
            code=[code,'-'];
        end
    end  
end

durations=diff(t(switchIdxs));
if last_constraint(1)==0 && length(durations)>1
durations(1)=[];
end
charging_time=sum(durations);

if ~isempty(code)
    codeSplit=strsplit(code,'-');
else
    codeSplit={};
end
codeLong=[];
for j=1:length(codeSplit)
    codeLong=[codeLong,codeSplit{j},'(',num2str(durations(j),'%.2f'),')'];
    if j<length(codeSplit)
        codeLong=[codeLong,'-'];
    end
end

end

