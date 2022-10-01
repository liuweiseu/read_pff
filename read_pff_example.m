clear;
clc;

%--------------------Select data file-------------------------%
[filename0, pathname] = uigetfile( ...
    {'*.pff','pff Files';...
    '*.*','All Files' },...
    'Please select the pff file',...
    './');
if isequal(filename0,0)
   disp('User selected Cancel')
   return;
else
   filename= fullfile(pathname, filename0);
end
%-------------------------------------------------------------%

q = read_pff(filename);

q(1)
q(2)
q(3)
q(4)