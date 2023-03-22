function WorkerPath = setParallelWorkerPath(Path,Worker_id)
% WorkerPath = setParallelWorkerPath(Path,Worker_id)
% Update path string based on worker identifier
% Inputs:
% Path: string, path
% as well as paths to configuration folders and configuration filenames (see @setPaths)
% Worker_id: string, worker identifier
% Outputs:
% WorkerPath: string, updated Path from input
%%
WorkerPath=[Path,'_w',num2str(Worker_id)];

end