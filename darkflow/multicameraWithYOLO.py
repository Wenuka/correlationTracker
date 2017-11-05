# Import the required modules
import dlib
from darkflow.net.build import TFNet
import cv2
import argparse as ap
import get_points
import json

def run(source=0, source2=0):
    # initializing yolo
    options = {"model": "cfg/tiny-yolo-voc.cfg", "load": "tiny-yolo-voc.weights", "threshold": 0.5, "gpu":1.0}
    tfnet = TFNet(options)

    # Create the VideoCapture object
    cam = cv2.VideoCapture(source)
    cam2 = cv2.VideoCapture(source2)

    # If Camera Device is not opened, exit the program
    if not cam.isOpened():
        print "Video device 1 or file 1 couldn't be opened"
        exit()
    if not cam2.isOpened():
        print "Video device 2 or file 2 couldn't be opened"
        exit()
    
    #video starts
    print "Press key `p` to pause the video to start tracking"
    while True:
        # Retrieve an image and Display it.
        retval, img = cam.read()
        retval2, img2 = cam2.read()
        if not retval:
            print "Cannot capture frame device 1"
            exit()
        if not retval2:
            print "Cannot capture frame device 2"
            exit()
        if(cv2.waitKey(10)==ord('p')):  #start detecting cars if "p" pressed
            break
        cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
        cv2.namedWindow("Image2", cv2.WINDOW_NORMAL)
        cv2.imshow("Image", img)
        cv2.imshow("Image2", img2)

        # result = tfnet.return_predict(img) #enable if detection is necessary for every frame
        # print(result)


    # cv2.destroyWindow("Image")  # video stopped
    # cv2.destroyWindow("Image2")  # video stopped
    threshld = 10
    height = len(img) -threshld
    width = len(img[0]) -threshld
    limit = height - 40
    tryframes = 8   # how many frames to try to detect a vehicle before neglecting the request

    # Co-ordinates of objects to be tracked  # will be stored in a list named `points`
    points = []
    # yolo detection
    yoloresult = tfnet.return_predict(img) 
    for detectObj in yoloresult:
        if (inRegion(detectObj)):
            vehicleloc = (detectObj['topleft']['x'],detectObj['topleft']['y'],detectObj['bottomright']['x'],detectObj['bottomright']['y'])
            points.append(vehicleloc)
            print ("Tracking started for the request")
            break # only one vehicle will be added per one request *************** optimize this to reduce issues with multi vehicles trying to enter at the same time

    # (or) start tracking from manually entered position
    # points = get_points.run(img, multi=True) 

    if (len(points)<1):
        print "No vehicle found in the frame : trying few other frames"
        for _ in xrange(tryframes):  # trying few frames to capture a vehicle if not detected from first few frames
            # Retrieve an image and Display it.
            retval, img = cam.read()  # read next frame(s)
            retval2, img2 = cam2.read()
            if not retval:
                print "Cannot capture frame device 1"
                exit()
            if not retval2:
                print "Cannot capture frame device 2"
                exit()
            cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
            cv2.namedWindow("Image2", cv2.WINDOW_NORMAL)
            cv2.imshow("Image", img)      # not showing ?? ******************************* ??,
            cv2.imshow("Image2", img2)

            yoloresult = tfnet.return_predict(img)
            flagdetected = False
            for detectObj in yoloresult:
                if (inRegion(detectObj)):
                    vehicleloc = (detectObj['topleft']['x'],detectObj['topleft']['y'],detectObj['bottomright']['x'],detectObj['bottomright']['y'])
                    points.append(vehicleloc)
                    print ("Tracking started for the request")
                    flagdetected = True
                    break
            if flagdetected:
                break
            print("Vehicle detection fails for the new frame as well.")   
    points2 = []
    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Image2", cv2.WINDOW_NORMAL)
    cv2.imshow("Image", img)
    cv2.imshow("Image2", img2)

    # Initial co-ordinates of the object to be tracked 
    # Create the tracker object
    tracker = [dlib.correlation_tracker() for _ in xrange(len(points))]
    tracker2 = [dlib.correlation_tracker() for _ in xrange(0)]
    # Provide the tracker the initial position of the object
    # [tracker[i].start_track(img, dlib.rectangle(*rect)) for i, rect in enumerate(points)]
    for k, rect in enumerate(points):
        tracker[k].start_track(img, dlib.rectangle(*rect))
    for k2, rect in enumerate(points2):
        tracker[k2].start_track(img2, dlib.rectangle(*rect))
 
    temp_tracker = list(tracker) #to remove the deleted trackers from tracker without affecting for loop 
    temp_tracker2 = list(tracker2)
    trigerYolo = 0
    while True:
        # print tracker
        # print temp_tracker
        tracker = list(temp_tracker) 
        tracker2 = list(temp_tracker2) 
        # Read frame from device or file
        retval, img = cam.read()
        retval2, img2 = cam2.read()
        if not retval:
            print "Cannot capture frame device 1 | CODE TERMINATION....."
            exit()
        if not retval2:
            print "Cannot capture frame device 2 | CODE TERMINATION....."
            exit()
        new_points = []
        if(cv2.waitKey(10)==ord('p')):  #new vehicle trying to add if "p" pressed
            # yolo detection
            yoloresult = tfnet.return_predict(img) 
            for detectObj in yoloresult:
                if (inRegion(detectObj)):
                    vehicleloc = (detectObj['topleft']['x'],detectObj['topleft']['y'],detectObj['bottomright']['x'],detectObj['bottomright']['y'])
                    new_points.append(vehicleloc)
                    print ("Tracking started for the request")
                    break # only one vehicle will be added per one request *************** optimize this to reduce issues with multi vehicles trying to enter at the same time
            if (len(new_points)<1):
                print "no vehicle found in frame 1: trying few other frames triggered"
                trigerYolo = tryframes   # trying few frames to capture a vehicle if not detected from first few frames

        if trigerYolo > 0:  # if detection was not happened for the last frame
            yoloresult = tfnet.return_predict(img)
            for detectObj in yoloresult:
                if (inRegion(detectObj)):
                    vehicleloc = (detectObj['topleft']['x'],detectObj['topleft']['y'],detectObj['bottomright']['x'],detectObj['bottomright']['y'])
                    new_points.append(vehicleloc)
                    print ("Tracking started for the request")
                    trigerYolo = 0
                    break
            print("Vehicle detection fails for the request for the next frame as well.")   
            trigerYolo -= trigerYolo

        if len(new_points) > 0: # if there is a new detected vehicled
            # Create the tracker object
            new_tracker = [dlib.correlation_tracker() for _ in xrange(len(new_points))]
            # Provide the tracker the new positions of the object
            for j, rect2 in enumerate(new_points):
                new_tracker[j].start_track(img, dlib.rectangle(*rect2))
            # [tracker[j].start_track(img, dlib.rectangle(*rect)) for j, rect in enumerate(points)]
            tracker.extend(new_tracker)
            print "Success: Tracking started for the newly entered vehicle."

        temp_tracker = list(tracker)
        # Update the tracker  
        for i in xrange(len(tracker)): #for number of objects to track
            confdnc = tracker[i].update(img)
            # print confdnc
            
            # Get the position of th object, draw a 
            # bounding box around it and display it.
            rect = tracker[i].get_position()
            pt1 = (int(rect.left()), int(rect.top()))
            pt2 = (int(rect.right()), int(rect.bottom()))


            if (pt1[0]< threshld or pt1[1]< threshld or pt2[0]>=width):
                del temp_tracker[i]
                print "Object removed: out of the frame/ unexpected behavior"
                continue
            if (pt2[1]>= limit):
                del temp_tracker[i]
                print "Object removed: vehicle enters next view"
                new_points2 = [(0, 150, 130, 260)]
                # new_tracker2 = dlib.correlation_tracker()
                # # Provide the tracker the new positions of the object
                # new_tracker2.start_track(img2, dlib.rectangle(*new_points2[0]))
                # # [tracker[j].start_track(img, dlib.rectangle(*rect)) for j, rect in enumerate(points)]
                # tracker2.append(new_tracker2)

                new_tracker2 = [dlib.correlation_tracker() for _ in xrange(len(new_points2))]
                # Provide the tracker the new positions of the object
                for j2, rect2_2 in enumerate(new_points2):
                    new_tracker2[j2].start_track(img2, dlib.rectangle(*rect2_2))
                # [tracker[j].start_track(img, dlib.rectangle(*rect)) for j, rect in enumerate(points)]
                tracker2.extend(new_tracker2)


                print "Success: Tracking started from view 2."
                continue
            # if (confdnc < 3.5):
            #     print "Low Confidence"
            #     # continue

            cv2.rectangle(img, pt1, pt2, (255, 255, 255), 3)
            # print "Object {} tracked at [{}, {}] \r".format(i, pt1, pt2),

            # show location of box if mentionedd
            loc = (int(rect.left()), int(rect.top()-20))
            txt = "Vehicle : [{}]".format('KM-3210')
            cv2.putText(img, txt, loc , cv2.FONT_HERSHEY_SIMPLEX, .5, (255,255,255), 1)
        temp_tracker2 = list(tracker2)
        for i2 in xrange(len(tracker2)): #for number of objects to track
            confdnc2 = tracker2[i2].update(img2)
            rect_2 = tracker2[i2].get_position()

            pt1_2 = (int(rect_2.left()), int(rect_2.top()))
            pt2_2 = (int(rect_2.right()), int(rect_2.bottom()))

            cv2.rectangle(img2, pt1_2, pt2_2, (255, 255, 255), 3)
            loc = (int(rect_2.left()), int(rect_2.top()-20))
            txt = "Vehicle : [{}]".format('KM-3210')
            cv2.putText(img2, txt, loc , cv2.FONT_HERSHEY_SIMPLEX, .5, (255,255,255), 1)
        cv2.namedWindow("Image", cv2.WINDOW_NORMAL)        # ***** commented *******
        # cv2.namedWindow("Image2", cv2.WINDOW_NORMAL)
        cv2.imshow("Image", img)
        cv2.imshow("Image2", img2)
        # Continue until the user presses ESC key
        if cv2.waitKey(1) == 27:
            break

    # Relase the VideoCapture object
    cam.release()
    cam2.release()


def inRegion(detectObj):
    if detectObj['label'] != 'car': return False
    if (detectObj['bottomright']['y'] > 80 and detectObj['topleft']['x'] > 130 and detectObj['bottomright']['x'] < 430): return True
    return False 


if __name__ == "__main__":
    source = '../vid/cam1.avi' 
    source2 = '../vid/cam2.avi'    
    run(source, source2)
