import socket
import time
from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2
from collections import deque
from multiprocessing import Process
import threading
import queue
 
def MotionDetection(g,out_queue):
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video",
	    help="path to the (optional) video file")
    ap.add_argument("-b", "--buffer", type=int, default=32,
    	    help="max buffer size")
    args = vars(ap.parse_args())

# define the lower and upper boundaries of the "green"
# ball in the HSV color space
    greenLower = (29, 86, 6)
    greenUpper = (64, 255, 255)
    z=g    
# initialize the list of tracked points, the frame counter,
# and the coordinate deltas
    pts = deque(maxlen=args["buffer"])
    counter = 0


# if a video path was not supplied, grab the reference
# to the webcam
    if not args.get("video", False):
	    vs = VideoStream(src=0).start()

# otherwise, grab a reference to the video file
    else:
	    vs = cv2.VideoCapture(args["video"])

    vs = VideoStream(src=0).start()
    time.sleep(2.0)
    frame = vs.read()
                #frame = frame if args.get("video", None) is None else frame[1]
                # resize the frame, convert it to grayscale, and blur it
    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (11, 11), 0)    # okunan frame
    previousFrame= gray
     
    while True:
               
                global x
                global y
                frame = vs.read()
                #frame = frame if args.get("video", None) is None else frame[1]
                # resize the frame, convert it to grayscale, and blur it
                frame = imutils.resize(frame, width=500)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (11, 11), 0)    # okunan frame
	# if the first frame is None, initialize it
	        #if previousFrame is None:
		 #        previousFrame = gray
		  #       continue
              
                frameDelta = cv2.absdiff(previousFrame, gray)
                thresh = cv2.threshold(frameDelta, 15, 255, cv2.THRESH_BINARY)[1]

	# dilate the thresholded image to fill in holes, then find contours
	# on thresholded image
                thresh = cv2.dilate(thresh, None, iterations=2)
                cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                        cv2.CHAIN_APPROX_SIMPLE)
                cnts = imutils.grab_contours(cnts)

	
        # only proceed if at least one contour was found
                if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
                        c = max(cnts, key=cv2.contourArea)
                        ((x, y), radius) = cv2.minEnclosingCircle(c)
                        M = cv2.moments(c)
                        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                		# only proceed if the radius meets a minimum size
                        if radius >8:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
                                cv2.circle(frame, (int(x), int(y)), int(radius),
                                        (0, 255, 255), 2)
                                cv2.circle(frame, center, 5, (0, 0, 255), -1)
                                pts.appendleft(center)
                                cv2.putText(frame, " x: {}, y: {}".format( x,  y),(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,0.35, (0, 0, 255), 1)
                                print ("x=%d" %x)
                                print ("y=%d" %y) 
                                out_queue.put(x)
                                out_queue.put(y)
                                

               
                previousFrame=gray

	# show the frame and record if the user presses a key
                cv2.imshow("Estimated Coordinates", frame) 
                #coordinates[0]=x
                #coordinates[1]=y
                
                time.sleep(0.5)
                
	

	



def Socket(take_queue):
        #*********************************************************************
    HOST = '' # Server IP or Hostname
    PORT = 12345 # Pick an open Port (1000+ recommended), must match the client sport
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print ("Socket created")

#managing error exception
    try:
        s.bind((HOST, PORT))
    except socket.error:
        print ("Bind failed" )

    s.listen(5)
    print ("Socket awaiting messages")
    (conn, addr) = s.accept()
    print ("Connected")
    
    
    while True:
        a=str(take_queue.get())
        b=str(take_queue.get())
        data = conn.recv(1024)
        print ("data=%s " %data.decode('utf-8').strip())
        reply1 = ''
        reply2 = ''
	
                # process your message
        if (data.decode('utf-8').strip() =="1656616566"):
                reply1 = a
                reply2 = b
	
        else:
                reply1 = 'jigubigule1'
                reply2 = 'jigubigule2'
       
                # Sending reply
        conn.send(reply1.encode('utf-8').strip())
        conn.send(reply2.encode('utf-8').strip())
        time.sleep(0.5)
       
     
if __name__=='__main__':
        
      
        my_queue = queue.Queue()
      
        t = threading.Thread(name='MotionDetection',args=(1,my_queue), target=MotionDetection)
        w = threading.Thread(name='Socket',args = (my_queue,), target=Socket)

        
        t.start()
        w.start()
        t.join()
        time.sleep(0.2)
        
 
        
       
       
       
