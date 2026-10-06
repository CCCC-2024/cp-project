% Artlab is our simplest lab. All we do is read in an image and try to
% create effects by making the image different.

% Read in the picture of green mountains
im = imread('mountains.png');

% Q1: What is the size of the image? Use the function "size"
imageSize = size(im)

% Q2: Create a red, green and blue matrix of the image 
red = im(:,:,1);
green = im(:,:,2);
blue = im(:,:,3);

% Create a gray version of the image
% "double" turns the data into floating point numbers
grayim = (double(red) + double(green) + double(blue))/3; 

% "range" gives max minus min. Display all three values so that the
% thresholds used below are easier to understand.
grayMin = min(grayim(:))
grayMax = max(grayim(:))
grayRange = range(grayim(:))

% Q3: This is the point of the lab. We need to figure out how to quantize
% the image, using the range as a starting point. I've given one example
% here.

level1 = 50;
level2 = 100;
level3 = 150;

% Preallocate an output image of the same size and type as the input.
quantim = zeros(size(im), 'uint8');

% for every color
for i = 1:3
    sourceChannel = im(:,:,i);
    tmp = zeros(size(sourceChannel), 'uint8');

    % Reduce the 256 possible values to four representative values.
    % Use sourceChannel in every condition so that changing tmp does not
    % affect the conditions that follow.
    tmp(sourceChannel <= level1) = 25;
    tmp(sourceChannel > level1 & sourceChannel <= level2) = 75;
    tmp(sourceChannel > level2 & sourceChannel <= level3) = 140;
    tmp(sourceChannel > level3) = 220;
    
    quantim(:,:,i) = tmp;
    
end
    

% Show them together
figure;
imshowpair(im,quantim,'montage');
title('Original Image (left) and Quantized Image (right)');
