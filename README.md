# PointCloudRegistration-py

### Testing 4 level point cloud registration 
1. filtering (remove noise)
2. down sampling (reduce point)
3. global registration (rough registration)
4. local refinement (elaborate registration)

### main dependencies
- tkinter (user interface)
- panda3d (scene graph)
- open3d (point cloud)

### Usage
![](https://github.com/eunwonki/PointCloudRegistration-Py/blob/main/data/Screenshot/13.png?raw=true)
     
### Screenshot    

#### View   
   
| mesh                                                                                                 | point cloud                                                                                          | down sampled point cloud                                                                             |
|------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| ![](https://github.com/eunwonki/PointCloudRegistration-Py/blob/main/data/Screenshot/10.JPG?raw=true) | ![](https://github.com/eunwonki/PointCloudRegistration-Py/blob/main/data/Screenshot/11.JPG?raw=true) | ![](https://github.com/eunwonki/PointCloudRegistration-Py/blob/main/data/Screenshot/12.JPG?raw=true) |
       

In this screenshot, processing means down sampling and filtering.
We just do 5 mm scale down sampling at now.

|initial|global registration result| local registration result        |
|----------|---------|----------------------------------|
|![](https://github.com/eunwonki/PointCloudRegistration-Py/blob/main/data/Screenshot/3.PNG?raw=true)|![](https://github.com/eunwonki/PointCloudRegistration-Py/blob/main/data/Screenshot/4.PNG?raw=true)|![](https://github.com/eunwonki/PointCloudRegistration-Py/blob/main/data/Screenshot/5.PNG?raw=true)|

We support point cloud registration by right buttons.    
global point cloud registration -> using feature point ransac ([open3d global registration](http://www.open3d.org/docs/0.12.0/tutorial/pipelines/global_registration.html))     
local point cloud registration -> open3d g-icp

![](https://github.com/eunwonki/PointCloudRegistration-Py/blob/main/data/Screenshot/14.JPG?raw=true)
![](https://github.com/eunwonki/PointCloudRegistration-Py/blob/main/data/Screenshot/15.JPG?raw=true)
![](https://github.com/eunwonki/PointCloudRegistration-Py/blob/main/data/Screenshot/16.JPG?raw=true)

And we support changing to custom source or target by menu (just only obj file...)


### TODO
다양한 PointCloud Registration Option을 넣을 수 있는 User Interface 추가
