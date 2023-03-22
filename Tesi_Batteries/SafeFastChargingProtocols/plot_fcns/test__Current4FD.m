function test__Current4FD(nparams,figNum)
%% debugFCN
%%
fnames={'./simout'};

for i=1:nparams
    fnames{end+1}=['./simout_wp',num2str(i)];
    fnames{end+1}=['./simout_wm',num2str(i)];
end

for i=1:length(fnames)
    load([fnames{i},'/output_data.mat'],'current','phi_applied_times')
    curr{i}=current;
    t{i}=phi_applied_times;
end

figure(figNum)
clf
hold on
for i=1:length(curr)
    stairs(t{i},curr{i})
end
legend(fnames)
drawnow
end

