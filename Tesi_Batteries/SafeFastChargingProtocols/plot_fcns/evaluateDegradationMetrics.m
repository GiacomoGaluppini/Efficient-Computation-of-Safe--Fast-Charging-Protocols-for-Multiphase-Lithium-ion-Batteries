function [metrics] = evaluateDegradationMetrics(t,T_lyte,T_ub,etaPlating_a,LPOverpot_lb)
% [metrics] = evaluateDegradationMetrics(t,T_lyte,T_ub,etaPlating_a,LPOverpot_lb)
% evaluate performances of a charging rptotocol in terms of battery degradation
%Inputs:
% t: array, with time samples
% T_lyte: array, electrolyte temperature at each time instant in t
% T_ub: scalar, upper limit for electrolyte temperature
% etaPlating_a: array, Li plating overpotential at each time instant in t
% LPOverpot_lb: scalar, lower limit for Li plating overpotential
%Outputs:
% metrics: struct, with fields:
% metrics.T_lyte_timeAbove: scalar, overall time spent with electrolyte temperature
% higher than T_ub
% metrics.etaPlating_a_timeBelow: scalar, overall time spent with Li plating overpotential
% lower than LPOverpot_lb
%%
dt=[0; diff(t)];

%% T_lyte_max  integral above limit

if ~isempty(T_lyte)
    
    if ~isvector(T_lyte)
        T_lyte=max(T_lyte')';
    end
    
    idxAbove=find(T_lyte>T_ub);
    idxBelow=find(T_lyte<=T_ub);
    
    T_lyte=T_lyte-T_ub;
    T_lyte(idxBelow)=0;
    
    metrics.T_lyte_integralAbove=abs(sum(T_lyte.*dt));
    metrics.T_lyte_timeAbove=sum(dt(idxAbove));
end

%% etaPlating_a min integral above limit

if ~isempty(etaPlating_a)
    etaPlating_a=min(etaPlating_a')';
    
    idxAbove=find(etaPlating_a>=LPOverpot_lb);
    idxBelow=find(etaPlating_a<LPOverpot_lb);
    
    etaPlating_a=etaPlating_a-LPOverpot_lb;
    etaPlating_a(idxAbove)=0;
    
    metrics.etaPlating_a_integralBelow=abs(sum(etaPlating_a.*dt));
    metrics.etaPlating_a_timeBelow=sum(dt(idxBelow));
end


end

