# Project Overview
For the final project I implemented 3D reconstruction which is the process of generating
3D information of an object using numerous 2D image data. The main aim of this course was to
learn and implement algorithms that work hand in hand with image capturing and would allow
machines to visualize the world as humans do. Various algorithms have been covered for
reconstruction purposes throughout the quarter. This final report gives an overview of some of
these algorithms, how they were used in the final project, results from their usage on practical
image data, and then discusses some implementation issues. Functions implemented in this
project that are related to image capturing include: camera calibration, projection, and
triangulation. Algorithms and strategies implemented that are related to 3D model generation
include: decoding structured light, Delaunay triangulation, mesh cleaning, mesh smoothing,
mesh aligning, and poisson reconstruction.
The purpose of this project was to create computer generated models of 3D objects from
its digital images. Generally, image processing works well on 2D images of an object and is
useful in many applications, however it misses the depth parameter of that object. Depth
information of an object is vital in many situations and plays a significant role in computer
vision. The main goal of 3D reconstruction is to regenerate that depth information from a series
of simple 2D images of an object. This final project implements 3D reconstruction and produces
a 3D model as an output, which could be stored and viewed or modified freely in future.
