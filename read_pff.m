% read metadata and img data from pff file, and return a struct
%
function [q, frametime_epoch] = read_pff(filename)

insert(py.sys.path,int32(0),'');

% call the python script to finish the reading work
d = pyrunfile(['read_pff_wrapper.py ',filename],'d');

% get the metadata and img data from the return data,
% and then put the data into the structs
for i = 1:4
    q(i).image          = double(d{(i-1)*7+1});
    q(i).boardloc       = double(d{(i-1)*7+2});
    q(i).utc            = double(d{(i-1)*7+3});
    q(i).nanosec        = double(d{(i-1)*7+4});
    q(i).acq_mode       = double(d{(i-1)*7+5});
    q(i).packet_no      = double(d{(i-1)*7+6});
    frametime_epoch{i}  = double(d{(i-1)*7+7}); 
end

end
