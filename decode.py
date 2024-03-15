from matplotlib import pyplot as plt
import numpy as np

def decode(imprefix,start,threshold,x):
    """
    Given a sequence of 20 images of a scene showing projected 10 bit gray code, 
    decode the binary sequence into a decimal value in (0,1023) for each pixel.
    Mark those pixels whose code is likely to be incorrect based on the user 
    provided threshold.  Images are assumed to be named "imageprefixN.png" where
    N is a 2 digit index (e.g., "img00.png,img01.png,img02.png...")
 
    Parameters
    ----------
    imprefix : str
       Image name prefix
      
    start : int
       Starting index
       
    threshold : float
       Threshold to determine if a bit is decodeable
       
    Returns
    -------
    code : 2D numpy.array (dtype=float)
        Array the same size as input images with entries in (0..1023)
        
    mask : 2D numpy.array (dtype=logical)
        Array indicating which pixels were correctly decoded based on the threshold
    
    """
    
    
    thresh = .325
    imprefixColor = imprefix+f'color_C{x}_'
    background = plt.imread(imprefixColor+"00.png")
    foreground = plt.imread(imprefixColor+"01.png")
    if (background.dtype == np.uint8):
        background = background.astype(float) / 256
#     if (len(background.shape)==3):    
#         background = background.mean(axis=-1,keepdims=1)[:,:,0]
    if (foreground.dtype == np.uint8):
        foreground = foreground.astype(float) / 256
#     if (len(foreground.shape)==3):
#         foreground = foreground.mean(axis=-1,keepdims=1)[:,:,0]

    obj = (np.sum(np.abs(foreground-background),axis=-1) > thresh).astype(int)
    
    # we will assume a 10 bit code
    nbits = 10
    # generate list of image files
    images = []
    imprefix = imprefix + f'frame_C{x}_'
    for i in range(20):
        im = imprefix+"0"+str(i) if start+i<10 else imprefix+str(start+i)
        images.append(im+".png")
        
    
    
    gcode = [] # list to contain all of the gray code bits for each pair of images
    for i in range(10):
        im1 = plt.imread(images[2*i])
        im2 = plt.imread(images[2*i+1])

        # don't forget to convert images to grayscale / float after loading them in
        if (im1.dtype == np.uint8):
            im1 = im1.astype(float) / 256
        if (len(im1.shape)==3):    
            im1 = im1.mean(axis=-1,keepdims=1)[:,:,0]
        if (im2.dtype == np.uint8):
            im2 = im2.astype(float) / 256
        if (len(im2.shape)==3):
            im2 = im2.mean(axis=-1,keepdims=1)[:,:,0]
        
        if (i==0):
            H,W = im1.shape
            mask = np.ones((H,W)).astype(int) #create binary mask, intially all True
        gcode.append((im1>im2).astype(int))
        new_mask = np.abs(im1-im2)>=threshold
        mask *= new_mask
    
    bcode = gcode[0].reshape((H,W,1)) # create binary code 3D array
    for i in range(len(gcode)-1):
        bcode = np.dstack((bcode,(np.logical_xor(bcode[:,:,i],gcode[i+1])).astype(int)))
 
    code = []
    for i in range(H):
        for binary in bcode[i]:
            code.append(int(''.join(str(b) for b in binary),2))

    code = np.array(code).reshape((H,W))
    return code,mask,obj