function [FileCell] = readFile2Cell(path)
%  [FileCell] = readFile2Cell(path)
% Read mpet configuration file into cell array of strings
% Inputs:
% path: string, path to the desired mpet configuration file
% Outputs:
% FileCell: cell array of strings, with content of file pointed by path
%%
fid = fopen(path);
tline = fgetl(fid);
l=1;
while ischar(tline)
    FileCell{l}=tline;
    tline = fgetl(fid);
    l=l+1;
end
fclose(fid);

end

