clear;
clc;
rgb=imread('Einstein.jpg');
r=rgb(:,:,1);
g=rgb(:,:,2);
b=rgb(:,:,3);
xlswrite('rgb.xlsx',r,'r');
xlswrite('rgb.xlsx',g,'g');
xlswrite('rgb.xlsx',b,'b');
disp('OK!');