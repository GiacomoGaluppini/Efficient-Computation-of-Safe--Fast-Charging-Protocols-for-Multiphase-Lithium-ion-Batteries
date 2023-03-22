function writeCell2File(path,FileCell)
% writeCell2File(path,FileCell)
% Rrite mpet config file as cell array back to .cfg file format
% Inputs:
% path: string, path to the desired mpet configuration file
% FileCell: cell array of strings, with content of file pointed by path (see @readFile2Cell, @updateCellFile)
%%
fid = fopen(path, 'w');
for i = 1:numel(FileCell)
        fprintf(fid,'%s\n', FileCell{i});
end
fclose(fid);
end

