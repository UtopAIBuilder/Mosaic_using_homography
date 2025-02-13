# -*- coding: utf-8 -*-
"""final version of visionAssignment1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Dknql05zq5tbH_9llxwDMrJbL2ezClIG
"""

#from google.colab import drive
#drive.mount('/content/drive')

#import cv2
#from google.colab.patches import cv2_imshow
import numpy as np
import math
from tqdm import tqdm

image1=cv2.imread('/homework02.images/image01.jpg')
image2=cv2.imread('/homework02.images/image02.jpg')
image3=cv2.imread('/homework02.images/image03.jpg')
image4=cv2.imread('/homework02.images/image04.jpg')
image5=cv2.imread('/homework02.images/image05.jpg')


def extractData(filePath):
    labels=[]
    X=[]
    f= open(filePath,"r")
    f1= f.readlines()
    for x in f1:
        x=x.rstrip("\n")
        a=x.split()
        X.append(toFloatArray(a))
    my_data=np.array(X)
    return my_data

def toFloatArray(a):
    x=[]
    for i in a:
        x.append(float(i))
    return x

#cv2_imshow(image1)
path12="/content/drive/My Drive/VisionAss1Res/rawmatches12.txt"
#my_data12=extractData(file_name)
path23="/content/drive/My Drive/VisionAss1Res/rawmatches23.txt"
#my_data23=extractData(file_name)
path34="/content/drive/My Drive/VisionAss1Res/rawmatches34.txt"
#my_data34=extractData(file_name)
path45="/content/drive/My Drive/VisionAss1Res/rawmatches45.txt"
#my_data45=extractData(file_name)

"""**translation and scaling of points in img1 and img2**"""

def NormalizeByTransform(A):
  mean=(np.mean(A,axis=0))
  T11=np.diag([1.0,1.0,1.0])
  T11[0,2]=-mean[0]
  T11[1,2]=-mean[1]
  #print(T11,mean)
  A=(np.dot(T11,A.T)).T
  C=0
  for i in A[:,:-1]:
    C+=np.linalg.norm(i)
  C=C/A.shape[0]
  sqrt2=math.sqrt(2)
  T12=np.diag([sqrt2/C,sqrt2/C,1.0])
  return np.dot(T12,A.T).T, np.dot(T12,T11)


"""**Homography in Ransac loop**"""



def computeHomographyUsingRansac(img1_norm_matrix,img2_norm_matrix):
  a=np.zeros(3)
  epsilon=.0005
  #best_inliers=[]
  max_score=0
  A=np.zeros((2*img1_norm_matrix.shape[0],9))
  for j in range(img1_norm_matrix.shape[0]):
    A[2*j]=np.concatenate((-img1_norm_matrix[j],a,img2_norm_matrix[j,0]*img1_norm_matrix[j]),axis=0)
    A[2*j+1]=np.concatenate((a,-img1_norm_matrix[j],img2_norm_matrix[j,1]*img1_norm_matrix[j]),axis=0)
  for i in range(200):
    rand_index=2*np.array(range(img1_norm_matrix.shape[0]))
    np.random.shuffle(rand_index)
 
    B=np.concatenate((A[rand_index[:4]],A[rand_index[:4]+1]),axis=0)
    u,s,vh=np.linalg.svd(B)  
    H=(vh.T)[:,-1]

    error=abs(np.dot(A,H))
  
    inliers_even=2*np.where(error[::2]<epsilon)[0]
    inliers_odd=2*np.where(error[1::2]<epsilon)[0]
    inliers_indices=np.intersect1d(inliers_even,inliers_odd,assume_unique=True)
    if(len(inliers_indices)>max_score):
      H_best=H
      max_score=len(inliers_indices)
     
  return H_best

def returnHomo(path):
  my_data12=extractData(path)
  img121_matrix=np.ones((my_data12.shape[0],3))
  img122_matrix=np.ones((my_data12.shape[0],3))
  img121_matrix[:,:2]=my_data12[:,:2]
  img122_matrix[:,:2]=my_data12[:,2:]
  img121_norm_matrix,T121=NormalizeByTransform(img121_matrix)
  img122_norm_matrix,T122=NormalizeByTransform(img122_matrix)
  H_best12=computeHomographyUsingRansac(img121_norm_matrix,img122_norm_matrix)
  H_final12=H_best12.reshape(3,3)
  H_orig12=np.linalg.multi_dot([np.linalg.inv(T122),H_final12,T121])
  print(H_orig12/H_orig12[2,2])
  return H_orig12


H_orig12=returnHomo(path12)
H_orig23=returnHomo(path23)
H_orig34=returnHomo(path34)
H_orig45=returnHomo(path45)

"""**Now some Mosaic Shit**"""



def computeMinMaxFor5images(image1,image2,image3,image4,image5,H_orig12,H_orig23,H_inv34,H_inv45):
    #image1 cordinates....
    p11=np.linalg.multi_dot([H_orig23,H_orig12,np.array([1,1,1])])
    p11=p11/p11[2]
    p12=np.linalg.multi_dot([H_orig23,H_orig12,np.array([1,image1.shape[0],1])])
    p12=p12/p12[2]
    p13=np.linalg.multi_dot([H_orig23,H_orig12,np.array([image1.shape[1],1,1])])
    p13=p13/p13[2]
    p14=np.linalg.multi_dot([H_orig23,H_orig12,np.array([image1.shape[1],image1.shape[0],1])])
    p14=p14/p14[2]
    #image2 cordinates
    p21=np.linalg.multi_dot([H_orig23,np.array([1,1,1])])
    p21=p21/p21[2]
    p22=np.linalg.multi_dot([H_orig23,np.array([1,image2.shape[0],1])])
    p22=p22/p22[2]
    p23=np.linalg.multi_dot([H_orig23,np.array([image2.shape[1],1,1])])
    p23=p23/p23[2]
    p24=np.linalg.multi_dot([H_orig23,np.array([image2.shape[1],image2.shape[0],1])])
    p24=p24/p24[2]
    #image4 cordinates
    p41=np.linalg.multi_dot([H_inv34,np.array([1,1,1])])
    p41=p41/p41[2]
    p42=np.linalg.multi_dot([H_inv34,np.array([1,image4.shape[0],1])])
    p42=p42/p42[2]
    p43=np.linalg.multi_dot([H_inv34,np.array([image4.shape[1],image4.shape[0],1])])
    p43=p43/p43[2]
    p44=np.linalg.multi_dot([H_inv34,np.array([image4.shape[1],image4.shape[0],1])])
    p44=p44/p44[2]
    #image5 cordinates
    p51=np.linalg.multi_dot([H_inv34,H_inv45,np.array([1,1,1])])
    p51=p51/p51[2]
    p52=np.linalg.multi_dot([H_inv34,H_inv45,np.array([1,image5.shape[0],1])])
    p52=p52/p52[2]
    p53=np.linalg.multi_dot([H_inv34,H_inv45,np.array([image5.shape[1],1,1])])
    p53=p53/p53[2]
    p54=np.linalg.multi_dot([H_inv34,H_inv45,np.array([image5.shape[1],image5.shape[0],1])])
    p54=p54/p54[2]
    #compute min,max
    min_x=math.floor(min(1,p21[0],p22[0],p23[0],p24[0],
                         p11[0],p12[0],p13[0],p14[0],
                         p41[0],p42[0],p43[0],p44[0],
                         p51[0],p52[0],p53[0],p54[0]))
    min_y=math.floor(min(1,p21[1],p22[1],p23[1],p24[1],
                         p11[1],p12[1],p13[1],p14[1],
                         p41[1],p42[1],p43[1],p44[1],
                         p51[1],p52[1],p53[1],p54[1]))
    max_x=math.ceil(max(image3.shape[1],p21[0],p22[0],p23[0],p24[0],
                        p11[0],p12[0],p13[0],p14[0],
                        p41[0],p42[0],p43[0],p44[0],
                        p51[0],p52[0],p53[0],p54[0]))
    max_y=math.ceil(max(image3.shape[0],p21[1],p22[1],p23[1],p24[1],
                        p11[1],p12[1],p13[1],p14[1],
                        p41[1],p42[1],p43[1],p44[1],
                        p51[1],p52[1],p53[1],p54[1]))
    return min_x,min_y,max_x,max_y

def getPixelValue(x,y,image):
  x_floor=math.floor(x-1)
  if(x_floor<0):
    x_floor=0
  y_floor=math.floor(y-1)
  if(y_floor<0):
    y_floor=0
  x_ceil=math.ceil(x-1)
  if(x_ceil>=image.shape[1]):
    x_ceil=0
  y_ceil=math.ceil(y-1)
  if(y_ceil>=image.shape[0]):
    y_ceil=0
  p1=[x_floor,y_floor]
  p2=[x_floor,y_ceil]
  p3=[x_ceil,y_floor]
  p4=[x_ceil,y_ceil]
  a=np.array([[image[p1[1],p1[0],:],image[p2[1],p2[0],:]],
              [image[p3[1],p3[0]-1,:],image[p4[1],p4[0],:]]])
  #print(a.shape)
  return cv2.resize(a,None,fx=1/2,fy=1/2,interpolation=cv2.INTER_LINEAR)[0,0]

def isItInside(p,image):
    if (p[0]<=image.shape[1] and p[0]>=1 and p[1]>=1 and p[1]<=image.shape[0]):
        return 1.0
    return 0.0

def stichImages(image1,image2,image3,image4,image5,H_orig12,H_orig23,H_orig34,H_orig45):
    H_inv12=np.linalg.inv(H_orig12)
    H_inv23=np.linalg.inv(H_orig23)
    H_inv34=np.linalg.inv(H_orig34)
    H_inv45=np.linalg.inv(H_orig45)
    min_x,min_y,max_x,max_y=computeMinMaxFor5images(image1,image2,image3,image4,image5,
                                                    H_orig12,H_orig23,H_inv34,H_inv45)
    mosaic=np.zeros((max_y-min_y+1,max_x-min_x+1,3))
    #alpha=1/2
    for j in tqdm(range(min_y,max_y+1)):
        for i in range(min_x,max_x+1):
            p3=np.array([i,j,1])
            p2=np.dot(H_inv23,p3)
            p2=p2/p2[2]
            p1=np.dot(H_inv12,p2)
            p1=p1/p1[2]
            p4=np.dot(H_orig34,p3)
            p4=p4/p4[2]
            p5=np.dot(H_orig45,p4)
            p5=p5/p5[2]
        
            #Now we start the surgery,Get your hands dirty... Not really coz Eww! it's gross..
            #value=0
            f1=isItInside(p1,image1)
            f2=isItInside(p2,image2)
            f3=isItInside(p3,image3)
            f4=isItInside(p4,image4)
            f5=isItInside(p5,image5)
            sumf=f1+f2+f3+f4+f5
            if(sumf!=0):
                f1=f1/sumf
                f2=f2/sumf
                f3=f3/sumf
                f4=f4/sumf
                f5=f5/sumf
            i1=i2=i3=i4=i5=0
            if(f1>0):
              i1=f1*getPixelValue(p1[0],p1[1],image1)
            if(f2>0):
                i2=f2*getPixelValue(p2[0],p2[1],image2)
            if(f3>0):
              i3=f3*image3[p3[1]-1,p3[0]-1,:]
            if(f4>0):
                i4=f4*getPixelValue(p4[0],p4[1],image4)
            if(f5>0):
                i5=f5*getPixelValue(p5[0],p5[1],image5)
            value=i1+i2+i3+i4+i5
            mosaic[j-min_y,i-min_x,:]=value
    return mosaic

mosaic=stichImages(image1,image2,image3,image4,image5,
                   H_orig12,H_orig23,H_orig34,H_orig45)



cv2_imshow(mosaic)

cv2.imwrite('output/colorMosa.jpg',mosaic)

cv2_imshow(mosaic)



