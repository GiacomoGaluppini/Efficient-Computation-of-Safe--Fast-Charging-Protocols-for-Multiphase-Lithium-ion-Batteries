function [idxslash] = findlastslash(Path)
idxslash=strfind(Path,'/');
if isempty(idxslash)
    idxslash=strfind(Path,'\');
end
idxslash=idxslash(end);
end

