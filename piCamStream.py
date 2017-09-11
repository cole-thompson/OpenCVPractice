#Cole Thompson

#Live stream image processing based on the following documentation
#Very slow without multithreading 
#http://picamera.readthedocs.io/en/release-1.10/recipes1.html#recording-to-a-network-stream
#http://docs.opencv.org/trunk/d7/d8b/tutorial_py_face_detection.html

#packages to add on Raspberry Pi: numpy, opencv-python, picamera
import socket
import time
import picamera
import time
import io
import numpy
import struct
import cv2

#TODO use two threads
#TODO add more methods to replace findFaces to try different image processing tests

maxStreamTime = 60 * 5
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

imgstream = io.BytesIO()
camera = picamera.PiCamera()

def main():
    global imgstream, camera
    
    #camera settings
    camera.resolution = (1080, 720)
    camera.framerate = 10
    
    connection = startConnection()
    
    print 'Connection found, starting video stream'
    
    try:
        #stream(connection)
        faceStream(connection)
    finally:
        connection.close()
        server_socket.close()
        
#wait for connection on a server socket and return a connection object
def startConnection():
    # Listen and wait for a connection on a port
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 8000))
    print 'Listening for Connection'
    server_socket.listen(0)
    
    # Accept a single connection and make a file-like object out of it
    return server_socket.accept()[0].makefile('wb')
    
#normal stream for testing
def stream(connection):
    camera.start_recording(connection, format='h264')
    camera.wait_recording(maxStreamTime)
    camera.stop_recording()
        
#take pictures while streaming to count number of faces, display text on video stream        
def faceStream(connection):
    global imgstream
    
    #check for cascade file
    print 'Face Cascade XML Found: ' + str(face_cascade.empty() == False)
    
    #start recording on the camera
    camera.start_recording(connection, format='h264')
    camera.wait_recording(1)
    startTime = time.time()
    
    #take periodic pictures and send to openCV
    while (time.time() - startTime < maxStreamTime):
        imgstream.truncate()
        imgstream.seek(0)
        camera.capture(imgstream, 'jpeg', use_video_port=True)
        numFaces = findFaces()
    	if numFaces > 0:
            camera.annotate_text = str(numFaces) + ' Face(s) Detected'
    	else:
       	    camera.annotate_text = 'No Face(s) Detected'
    camera.wait_recording(1)
    camera.stop_recording()
    
#use haar cascades in OpenCV to find the number of faces in an image
#also finds the coordinates of the square around each face
def findFaces():
    global imgstream
    buff = numpy.fromstring(imgstream.getvalue(), dtype=numpy.uint8)
    #grayimg = cv2.imdecode(buff, 0)
    img = cv2.imdecode(buff, 1)
    grayimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    grayimg = cv2.equalizeHist(grayimg)
    faces = face_cascade.detectMultiScale(grayimg, scaleFactor=1.3, minNeighbors=4, minSize=(30,30), flags=cv2.CASCADE_SCALE_IMAGE)
    print "Faces Found: " + str(len(faces))
    return len(faces)

