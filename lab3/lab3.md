This lab has three parts, A, B and C.

B and C should probably have one object, but A must have a few different objects.

For A you need to submit (a) a picture of the scene, and the two EPI images.

For B you need to submit a GIF of the 3D structure of the scene. 

For C you need to submit a GIF of the VGGT output. 

 

A) EPI 

EPI: See steps below

1. Arrange the simple objects you obtained on a flat surface

2. At some distance away, place your camera.

3. Collect a video from the camera as you slide the camera in a direction that is parallel to the image plane, and perpendicular to the viewing direction.

4. Import this into Matlab/Python/etc. Suppose the variable name is vid, then vid has four dimensions, x, y, color and time (frames).

5. Create an EPI slice of this image by extracting, epi_im = vid(mid,:,:,:); % mid is the midpoint of the rows

6. Display the epi image. Try different locations of mid. Try the perpendicular EPI images created by epi_im_perp = vid(:,mid,:,:);

7. Upload one EPI image, and text file with your observations about the differences between the EPI images.

8. Now pick a "patch" which is a set of rectangular coordinates. For example a patch could be (10,10,100,100). Color all the patch pixels in the video the same color. For example, if you pick red, then at frame 33 , you would do vid(10:100,10:100,:,33) = [255 0 0];

9. Generate EPI images and explain what is happening. Play the video back and explain what is happening. The explanations should be in the text file you upload.

2. Run colmap and submit a screen shot of the reconstruction and the camera positions:

B) Colmap (Thanks to Raul Rolon for the links on the syllabus --- you can also ask an AI to help you instead)

C) VGGT https://huggingface.co/spaces/facebook/vggt-omega