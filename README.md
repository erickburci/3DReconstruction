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
**1. calibrate.py**
  - This script was provided by Professor Fowlkes in assignment3. It collects the
images from the calib_jpg_u folder and utilizes the opencv library to find the
corners of the checkerboard and calculates the intrinsic parameters for the
cameras to store them in a pickle file for use later in the project. Once the intrinsic
parameters are retrieved, I was able to create camera objects and calculate the
extrinsic parameters.
**2. def calibratePose**
  - This function takes in two camera objects, each created with the intrinsic
parameters calculated previously along with initial parameters of its orientation,
and uses least squares to calculate the extrinsic parameters of the camera (i.e. its
rotation and transformation)


