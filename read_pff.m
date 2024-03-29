% read metadata and img data from pff file, and return a struct
%
function [q, frametime_epoch] = read_pff(filename)

insert(py.sys.path,int32(0),'');

% parse the file name
s = strsplit(filename, '/');
fn = strsplit(s{length(s)},'.');
dp = strsplit(fn{2},'_');
ft = dp{2};
% call the python script to finish the reading work
d = pyrunfile(['read_pff_wrapper.py ',filename],'d');

% get the metadata and img data from the return data,
% and then put the data into the structs
if(strcmp(ft,'img16') || strcmp(ft,'img8'))
    for i = 1:4
        q(i).image          = double(d{(i-1)*7+1});
        q(i).boardloc       = double(d{(i-1)*7+2});
        q(i).tai            = double(d{(i-1)*7+3});
        q(i).nanosec        = double(d{(i-1)*7+4});
        q(i).acq_mode       = double(d{(i-1)*7+5});
        q(i).packet_no      = double(d{(i-1)*7+6});
        frametime_epoch{i}  = double(d{(i-1)*7+7}); 
    end
elseif(strcmp(ft,'ph256') || strcmp(ft,'ph16'))
    q.ph                = double(d{1});
    q.quabo_no          = double(d{2});
    q.tai               = double(d{3});
    q.nanosec           = double(d{4});
    q.packet_no         = double(d{5});
    frametime_epoch     = double(d{6});
elseif(strcmp(ft,'ph1024'))
    for i=1:4
        q(i).ph             = double(d{(i-1)*5+1});
        q(i).tai            = double(d{(i-1)*5+2});
        q(i).nanosec        = double(d{(i-1)*5+3});
        q(i).packet_no      = double(d{(i-1)*5+4});
        frametime_epoch{i}  = double(d{(i-1)*5+5});
    end
end
