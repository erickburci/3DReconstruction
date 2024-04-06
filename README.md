# 3D Reconstruction

## Project Overview
In this project I implemented 3D reconstruction which is the process of generating
3D information of an object using a collection of 2D image data. **The primary goal of this project was to study and deploy algorithms that closely mimic human vision, enabling machines to perceive the world through image capture.** This report gives an overview of some of
these algorithms, how they were used in the project, results from their usage on practical
image data, and then discusses some implementation issues. Functions implemented in this
project that are related to image capturing include: **camera calibration**, **projection**, and
**triangulation**. Algorithms and strategies implemented that are related to 3D model generation
include: **decoding structured light, Delaunay triangulation, mesh cleaning, mesh smoothing,
mesh aligning**, and **poisson reconstruction.**
The purpose of this project was to create computer generated models of 3D objects from
its digital images. Generally, image processing works well on 2D images of an object and is
useful in many applications, however it misses the depth parameter of that object. Depth
information of an object is vital in many situations and plays a significant role in computer
vision. The main goal of 3D reconstruction is to regenerate that depth information from a series
of simple 2D images of an object. This final project implements 3D reconstruction and produces
a 3D model as an output, which could be stored and viewed or modified freely in future.

## Data
The data used for this project focused on two sets:
#### calib_jpg_u
This folder contained 40 total images. 20
of which were from a left positioned camera while the remaining 20 were from a right positioned
camera. The object in this image was a checkerboard with known dimensions. This data was
solely used to calibrate the left and right cameras so that I could calculate the extrinsic and
intrinsic parameters of each camera and create my camera objects.
#### manny
The second folder contained 5 folders (grab_{0-4}_u) each of which contained 84
images. All images had resolution 1200x1920 pixels. The first four images in each folder were
used to get the color of the object; there were two images per camera which and of those two,
one image had the plain background while the other had the object of interest. This was so that I
could write code to record the color data of the object and also to create a mask so that I can
discern the difference between the object and the background. The remaining 80 pictures were
also divided between the two cameras (40 for the left, 40 for the right). The 40 images were
divided again where the first twenty had structured light projected onto the object in various
intensities and the other half was the same structured light pattern but the inverse of the first half.
This was essential for determining corresponding points in the image.

## Algorithms/Functions/Scripts and Their Results
The following algorithms are explained in the order of implementation/its usage in the
scanning pipeline of the final project.
1. calibrate.py
  - This script was provided by Professor Fowlkes in assignment3. It collects the
images from the calib_jpg_u folder and utilizes the opencv library to find the
corners of the checkerboard and calculates the intrinsic parameters for the
cameras to store them in a pickle file for use later in the project. Once the intrinsic
parameters are retrieved, I was able to create camera objects and calculate the
extrinsic parameters.
2. def calibratePose
  - This function takes in two camera objects, each created with the intrinsic
parameters calculated previously along with initial parameters of its orientation,
and uses least squares to calculate the extrinsic parameters of the camera (i.e. its
rotation and transformation)

![image](https://github.com/erickburci/3DReconstruction/assets/159087967/3ba15140-88db-4ad7-ad68-83ff35b1aa9b)
![image](https://github.com/erickburci/3DReconstruction/assets/159087967/b5c8e800-69e3-472f-b9f3-4e19f07fa4b9)

3. def decode
  - This function reads in the file location for images captured with the left and right
cameras that have the object with the structure light projected onto it. From the
structured light patterned the function figures out the gray code, converts it to
binary code, and then to its decimal value and finally and returns an array which
is the same size as the camera image where each element contains the decoded
value as well as a binary image mask indicating which pixels were reliably
decoded. Most of the code was left the same from my assignment4, however for
this project I added a few lines to calculate an object mask using the colored
images in each folder.

![image](https://github.com/erickburci/3DReconstruction/assets/159087967/a0e7eac5-cffd-48a4-8fe0-fb675f1d1a2e)

4. def reconstruct
  - This function reads in the file location of the set of graycoded images from each
camera and produces a 3D point cloud. The decode function is called four times
(twice for each camera because the greycoded images have the standard projected
light and its inverse) to decode the horizontal and vertical images for both the left
and right cameras. Once decode returns the decoded greycoded images and their
mask, the reconstruct function combines the horizontal and vertical codes to get a
single (20-bit) integer for the left and right cameras as well as combines the
corresponding binary masks so only pixels with both good horizontal and vertical
codes are marked as valid. Furthermore, for this project I also combine the object
mask so that the background for each image is removed as much as possible.
Then, the function finds corresponding points for both the left and right images
for each pixel which was successfully decoded. To do this, I utilized the
numpy.intersect1d function. Finally, after getting the indices of the corresponding
points, I was able to use the triangulate function to get the 3D coordinates for the
set of pixels.

5. def triangulate
  - This function is called in the previously described reconstruct function. This code
was not changed from when I implemented it in assignment2.
  - The function takes in the coordinates of points in two images calculated in the
reconstruct function, along with the camera parameters calculated from
calibratePose, and returns the 3D coordinates of the points in the real world. To
triangulate the points, I again use the least squares technique (np.linalg.lstsq), this
time to calculate the z coordinates for the object. Finally, after the z-coordinates
are calculated, the function transforms them back to the world coordinate system.

![image](https://github.com/erickburci/3DReconstruction/assets/159087967/c71b2544-318b-4ea3-97cc-bb99038e87c8)

Once the 3D coordinates were successfully calculated, I was able to generate a
simple mesh to represent the object.

6. Mesh Clean Up
  - Bounding Box Pruning
    - After displaying the generated 3D coordinates, I was able to visualize the
boundaries of the object. I then created an array of the bounds:
np.array([lowerX, upperX, lowerY, upperY, lowerZ, upperZ]) and then
used intersect1D to prune the indices of the points in pts3 so that only the
points that were inside the bounds were kept.

*xlims = np.intersect1d(np.argwhere(pts3[0]>boxlimits[0]),np.argwhere(pts3[0]<boxlimits[1]))*
*ylims = np.intersect1d(np.argwhere(pts3[1]>boxlimits[2]),np.argwhere(pts3[1]<boxlimits[3]))*
*zlims = np.intersect1d(np.argwhere(pts3[2]>boxlimits[4]),np.argwhere(pts3[2]<boxlimits[5]))*
*tlims = np.intersect1d(xlims,ylims)*
*tlims = np.intersect1d(tlims,zlims)*
*pts3pruned = pts3[:,tlims]*
*pts2Lpruned = pts2L[:,tlims]*
*pts2Rpruned = pts2R[:,tlims]*

  - Triangle Pruning
    - Once I recovered the pruned 3D points, I was able to use the Delaunay
function to triangulate the coordinates. After getting triangles for the left
and right 2D points, I used those coordinate indices to find the triangles in
3D. Then for each triangle I checked to see if any edge was greater than
some threshold (1.7 seemed to work best).
  - To check prune the larger triangles I implemented a function
edgeCheck which took in triangle corners and calculated the
Euclidean distance between each point and checked if it was
greater than the threshold.

![image](https://github.com/erickburci/3DReconstruction/assets/159087967/01e211c6-c1ec-4277-a047-1e386806877c)

7. Mesh Smoothing
  - The original mesh results were very rough. To improve the meshes that were
generated, I implemented the simplest strategy. For each corner in each triangle I
calculate the average of the other two corners and save the new coordinate point.
After calculating new corners, I stored the triangle back inside a copy of the
original pruned 3D points. Once finished, the new set of 3D points contained a
smoother version of the original. I only calculated the average of two surrounding
points each time because I figured the process will propagate for each point and
will eventually get averaged by more surround points as I iterate through every
triangle. For the manny object, I found that 2 smoothing iterations worked best
before the mesh became over-smoothed.

*pts3smoothed = pts3pruned.copy()*
*for i in range(x):*
*for triangle in Tri:*
*p1,p2,p3 = pts3smoothed[:,tri].T*
*p1new = (p2+p3)/2*
*p2new = (p1+p3)/2*
*p3new = (p1+p2)/2*
*pts3smoothed[:,tri] = np.array([p1new,p2new,p3new]).T*

![image](https://github.com/erickburci/3DReconstruction/assets/159087967/3adb6bcb-e49a-4992-b8fb-5501c17ce176)

8. MeshLab
  - After generating each mesh, I used mesh.export(‘mesh.ply’) to save the individually
generated meshes for each set of 3D points.
    - Mesh Aligning
      - I used the mesh aligning tools in MeshLab to align the smoothed mesh
models. For the most part, point alignment seemed to work well, however,
for some meshes I had to manually align the meshes myself which took a
considerable amount of time.

![image](https://github.com/erickburci/3DReconstruction/assets/159087967/1f1f135b-3119-4ed0-97d0-22df2df8cfff)

  -  Poisson Surface Reconstruction
    - I also used the meshLab tools for Poisson Surface Reconstruction. To use the tool I first had to flatten my mesh result after alignment. The tool itself was fairly simple to use, and I found that the default parameters worked best for manny.

![image](https://github.com/erickburci/3DReconstruction/assets/159087967/73f41e81-bc9f-4333-b0cb-80e25a62929d)

## Assessment and Evaluation
Putting everything together for this final project proved to be a lot more difficult than
anticipated. And due to personal conflicts and complications throughout the last two week of the
quarter I wasn’t able to dedicate as much time as I had hoped on this assignment. That being
said, I don’t believe that this is my best work, however I am still proud of what I was able to
accomplish. When I began the assignment I initially wanted to work with the teapot, and for the
most part it was working alright, but when I tired to create the object mask by computing the
difference in the colored images I found that the teapot cast a large dark shadow which was near
impossible for me to get rid of. Despite this, I decided to continue with the following steps in the
project. More problems arose when I found that I wasn’t able to get a clean mesh after
reconstructing the 3D points. My box and triangle pruning strategies weren’t implemented in the
most effective way. Perhaps my edgeCheck function that calculated the Euclidean distance was
the issue, but I could not figure out a more effective way to prune out large triangles. Or maybe
there were some issues with my decode implementation; my conversion from greycode to binary
may have been wrong which may have led to the points for the left and right images not being
effectively corresponded. Whatever the reason, I found that when I went to meshLab to align my
meshes, some of the meshes did not align well at all. Mainly the handle for each mesh was in a
slightly different spot/angle. Also, there were many artifacts through the aligned mesh and even
large holes in the teapot. To make matters worse, point alignment did not seem to work at all for
my teapot meshes, so I had to align all of them together by hand which was very strenuous.
When I was finally ready to do Poisson surface reconstruction, some of the issues were fixed,
such as the large holes being filled in, however the handle was a complete mess.

![image](https://github.com/erickburci/3DReconstruction/assets/159087967/251d61d3-133f-437c-a1fc-ed873f960084)

After the teapot, I attempted the couple but for some reason I could not generate the meshes for
the object. They all came out inverse, where the outside detail (which was supposed to be
convex) came out concave and when I tried to fix it so that it was properly convexed, all of the
detail was lost. I also had a hard time getting the color to show up on any of my meshes so
without the detail of the texture, the couple object looked like a log. Ultimately I decided to work
with many, which had similar problems of not having much detail in texture and not having color
but it seemed to work the best. Perhaps a lot of detail was lost because of my mesh smoothing
technique; rather than taking all neighbors of all triangles that connected to a given point, I only
averaged amongst the neighbors within its own triangle, thinking that the effect would propagate
as I visited every triangle. Manny had the best image data when creating my object mask, It was
able to almost perfectly distinguish between background and the foreground object. Whereas the
large shadow in the teapot made mesh cleaning very difficult. If I gave myself more time to work
on this project I would have definitely figured out how to add color to the 3D models. I also did
not give myself enough time to organize all my code and streamline the process. All in all, I had
some fun with the final project and was excited to see some results, even if they weren't what I
expected.
