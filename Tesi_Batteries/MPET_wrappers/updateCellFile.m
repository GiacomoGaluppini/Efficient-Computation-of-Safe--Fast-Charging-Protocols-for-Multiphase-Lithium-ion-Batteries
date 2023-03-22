function [FileCell] = updateCellFile(FileCell,newParsStruct)
% [FileCell] = updateCellFile(FileCell,newParsStruct)
% Update mpet config file as cell array with new parameter values
% Inputs:
% FileCell: cell array of strings, with content of file pointed by path (see @readFile2Cell)
% newParsStruct: struct, with param info from input as follows (see @createParamStruct):
% newParsStruct.name=ParName
% newParsStruct.val=ParVal
% newParsStruct.type=ParType
% Outputs:
% FileCell: cell array of strings, updated version of input FileCell
%%
%find comment lines
IndexComments = find(contains(FileCell,'#'));

%find line for specific param and set the new value
for i=1:length(newParsStruct)
    
    if isnumeric(newParsStruct(i).val)
            parval=num2str(newParsStruct(i).val);
    else
        parval=newParsStruct(i).val;
    end
    
    %% handling of special cases
    %(brugg exp must be negative but can be specified as positive for use with log)
    if regexp(newParsStruct(i).name,regexptranslate('wildcard','BruggExp_*'))
        parval=num2str(-abs(str2double(parval)));
    end
        %(Nparts must be integer, >=1,  for use with log)
    if regexp(newParsStruct(i).name,regexptranslate('wildcard','Npart_*'))
        parval=num2str(ceil(str2double(parval)));
    end
    

    %% 
    IndexParname = find(contains(FileCell,newParsStruct(i).name));
    idxLine=setdiff(IndexParname,IndexComments);
    
    if strcmp(newParsStruct(i).name,'segments')
        if length(idxLine)>1
            idxLine(1)=[];
        end
    end
    
    if length(idxLine)==1
        if strcmp(newParsStruct(i).name,'segments')
            nextCommentIdx=IndexComments(find(IndexComments>idxLine,1));
            
            FileCellSeg{1}=['segments=['];
            for i=1:length(parval.duration)
                FileCellSeg{end+1}=['            (',...
                    num2str(parval.values(i)),',',num2str(parval.duration(i)),'),'];
            end
            FileCellSeg{end+1}=['            ]'];
            
            FileCell=[FileCell(1:idxLine-1) FileCellSeg FileCell(nextCommentIdx:end)];

        else
            FileCell{idxLine}=[newParsStruct(i).name,'=',parval];
        end
    else
        for j=1:length(idxLine)
            Line=FileCell{idxLine(j)};
            idxeq=find(Line=='=');
            parname=Line(1:idxeq-1);
            parname= parname(~isspace(parname)); %remove spaces
            
            if strcmp(parname,newParsStruct(i).name)
                %update param value
                FileCell{idxLine(j)}=[newParsStruct(i).name,'=',parval];
                break
            end
        end
    end
    
end
end

