import numpy as np
import scipy.optimize

def makerotation(rx,ry,rz):
    """
    Generate a rotation matrix    

    Parameters
    ----------
    rx,ry,rz : floats
        Amount to rotate around x, y and z axes in degrees

    Returns
    -------
    R : 2D numpy.array (dtype=float)
        Rotation matrix of shape (3,3)
    """
    rx = np.pi*rx/180.0
    ry = np.pi*ry/180.0
    rz = np.pi*rz/180.0

    Rx = np.array([[1,0,0],[0,np.cos(rx),-np.sin(rx)],[0,np.sin(rx),np.cos(rx)]])
    Ry = np.array([[np.cos(ry),0,-np.sin(ry)],[0,1,0],[np.sin(ry),0,np.cos(ry)]])
    Rz = np.array([[np.cos(rz),-np.sin(rz),0],[np.sin(rz),np.cos(rz),0],[0,0,1]])
    R = (Rz @ Ry @ Rx)
    
    return R 

class Camera:
    """
    A simple data structure describing camera parameters 
    
    The parameters describing the camera
    cam.f : float   --- camera focal length (in units of pixels)
    cam.c : 2x1 vector  --- offset of principle point
    cam.R : 3x3 matrix --- camera rotation
    cam.t : 3x1 vector --- camera translation 

    
    """    
    def __init__(self,f,c,R,t):
        self.f = f
        self.c = c
        self.R = R
        self.t = t

    def __str__(self):
        return f'Camera : \n f={self.f} \n c={self.c.T} \n R={self.R} \n t = {self.t.T}'
    
    def project(self,pts3):
        """
        Project the given 3D points in world coordinates into the specified camera    

        Parameters
        ----------
        pts3 : 2D numpy.array (dtype=float)
            Coordinates of N points stored in a array of shape (3,N)

        Returns
        -------
        pts2 : 2D numpy.array (dtype=float)
            Image coordinates of N points stored in an array of shape (2,N)

        """

        assert(pts3.shape[0]==3)
        
        # intrinsic parameters K: note since we are dealing with undefined units (i.e. not mm)
        #           I did not calculate f according to any m_x or m_y
        #           focal length and principle point offset are already in pixel units
        K = np.array([[self.f,0,self.c[0][0]],
                      [0,self.f,self.c[1][0]],
                      [0,0,1]])
        Rinv = np.linalg.inv(self.R)
        # extrinsic parameters Rt
        Rt = np.hstack((Rinv,-(Rinv@self.t)))
        C = K.dot(Rt)
        P = np.vstack((pts3,np.ones((1,pts3.shape[1]))))
        pts2 = C.dot(P)
        # scaling points by z: (x,y,z)-->(x/z,y/z)
        pts2 = (pts2/pts2[2,:])[:2,:]
        
        assert(pts2.shape[1]==pts3.shape[1])
        assert(pts2.shape[0]==2)
    
        return pts2
 
    def makerotation(rx,ry,rz):
        """
        Generate a rotation matrix    

        Parameters
        ----------
        rx,ry,rz : floats
            Amount to rotate around x, y and z axes in degrees

        Returns
        -------
        R : 2D numpy.array (dtype=float)
            Rotation matrix of shape (3,3)
        """
        rad_x = np.radians(rx)
        rad_y = np.radians(ry)
        rad_z = np.radians(rz)

        x = np.array([[1,0,0],
                         [0,np.cos(rad_x),-np.sin(rad_x)],
                         [0,np.sin(rad_x), np.cos(rad_x)]])
        y = np.array([[ np.cos(rad_y),0,np.sin(rad_y)],
                         [0,1,0],
                         [-np.sin(rad_y),0,np.cos(rad_y)]])
        z = np.array([[np.cos(rad_z),-np.sin(rad_z),0],
                         [np.sin(rad_z), np.cos(rad_z),0],
                         [0,0,1]])

        return z.dot(y).dot(x)
  

    
    def update_extrinsics(self,params):
        """
        Given a vector of extrinsic parameters, update the camera
        to use the provided parameters.
  
        Parameters
        ----------
        params : 1D numpy.array (dtype=float)
            Camera parameters we are optimizing over stored in a vector
            params[0:2] are the rotation angles, params[2:5] are the translation

        """
        self.R = makerotation(params[0],params[1],params[2])
        self.t = np.array([[params[3]],[params[4]],[params[5]]])


def triangulate(pts2L,camL,pts2R,camR):
    """
    Triangulate the set of points seen at location pts2L / pts2R in the
    corresponding pair of cameras. Return the 3D coordinates relative
    to the global coordinate system


    Parameters
    ----------
    pts2L : 2D numpy.array (dtype=float)
        Coordinates of N points stored in a array of shape (2,N) seen from camL camera

    pts2R : 2D numpy.array (dtype=float)
        Coordinates of N points stored in a array of shape (2,N) seen from camR camera

    camL : Camera
        The first "left" camera view

    camR : Camera
        The second "right" camera view

    Returns
    -------
    pts3 : 2D numpy.array (dtype=float)
        (3,N) array containing 3D coordinates of the points in global coordinates

    """

    #
    # Your code goes here.  I recommend adding assert statements to check the
    # sizes of the inputs and outputs to make sure they are correct 
    #
    assert(pts2L.shape[0]==2)
    assert(pts2L.shape==pts2R.shape)
    
    # create qL and qR vectors for each point for easier access in the for loop
    qL = (pts2L-camL.c[0][0])/camL.f
    qR = (pts2R-camR.c[1][0])/camR.f
    pts2L_q = np.vstack((qL,np.ones((1,pts2L.shape[1]))))
    pts2R_q = np.vstack((qR,np.ones((1,pts2R.shape[1]))))
    
    # initialize pts3 as an empty 2D numpy.array to hold triangulated points 
    pts3=np.empty((3,1))
     
    # loop through each point to be triangulated
    for i in range(pts2L.shape[1]):
        RLqL = camL.R@pts2L_q[:,i].reshape((3,1))
        RRqR = camR.R@pts2R_q[:,i].reshape((3,1))
        
        A = np.hstack((RLqL,-RRqR))
        assert(A.shape==(3,2))
        
        b = camR.t-camL.t
        assert(b.shape==(3,1))
        
        u = np.linalg.lstsq(A,b,rcond=None)[0]

        P1 = camL.R@(u[0]*pts2L_q[:,i].reshape((3,1)))+camL.t
        P2 = camR.R@(u[1]*pts2R_q[:,i].reshape((3,1)))+camR.t
        
        P = 0.5*(P1+P2)
        pts3 = np.hstack((pts3,P))
    
    pts3 = pts3[:,1:]
    assert(pts3.shape[1]==pts2L.shape[1])

    return pts3


def residuals(pts3,pts2,cam,params):
    """
    Compute the difference between the projection of 3D points by the camera
    with the given parameters and the observed 2D locations

    Parameters
    ----------
    pts3 : 2D numpy.array (dtype=float)
        Coordinates of N points stored in a array of shape (3,N)

    pts2 : 2D numpy.array (dtype=float)
        Coordinates of N points stored in a array of shape (2,N)

    params : 1D numpy.array (dtype=float)
        Camera parameters we are optimizing over stored in a vector

    Returns
    -------
    residual : 1D numpy.array (dtype=float)
        Vector of residual 2D projection errors of size 2*N
        
    """

    cam.update_extrinsics(params)
    residual = pts2 - cam.project(pts3)
    
    return residual.flatten()

def calibratePose(pts3,pts2,cam_init,params_init):
    """
    Calibrate the provided camera by updating R,t so that pts3 projects
    as close as possible to pts2

    Parameters
    ----------
    pts3 : 2D numpy.array (dtype=float)
        Coordinates of N points stored in a array of shape (3,N)

    pts2 : 2D numpy.array (dtype=float)
        Coordinates of N points stored in a array of shape (2,N)

    cam : Camera
        Initial estimate of camera

    Returns
    -------
    cam_opt : Camera
        Refined estimate of camera with updated R,t parameters
        
    """

    # define our error function
    efun = lambda params: residuals(pts3,pts2,cam_init,params)        
    popt,_ = scipy.optimize.leastsq(efun,params_init)
    cam_init.update_extrinsics(popt)

    return cam_init


