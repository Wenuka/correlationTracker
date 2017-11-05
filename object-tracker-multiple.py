# Import the required modules
import dlib
import cv2
import argparse as ap
import get_points

def run(source=0, dispLoc=False):
    # Create the VideoCapture object
    cam = cv2.VideoCapture(source)

    # If Camera Device is not opened, exit the program
    if not cam.isOpened():
        print "Video device or file couldn't be opened"
        exit()
    
    #video starts
    print "Press key `p` to pause the video to start tracking"
    while True:
        # Retrieve an image and Display it.
        retval, img = cam.read()
        if not retval:
            print "Cannot capture frame device"
            exit()
        if(cv2.waitKey(10)==ord('p')):  #stop playing video if "p" pressed
            break
        cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
        cv2.imshow("Image", img)
    cv2.destroyWindow("Image")  # video stopped

    threshld = 40
    height = len(img) -threshld
    width = len(img[0]) -threshld

    # Co-ordinates of objects to be tracked 
    # will be stored in a list named `points`
    points = get_points.run(img, multi=True)  #new video to take tracking data

    if not points:
        print "ERROR: No object to be tracked initially."
        # exit()
    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    cv2.imshow("Image", img)

    # Initial co-ordinates of the object to be tracked 
    # Create the tracker object
    tracker = [dlib.correlation_tracker() for _ in xrange(len(points))]
    # Provide the tracker the initial position of the object
    # [tracker[i].start_track(img, dlib.rectangle(*rect)) for i, rect in enumerate(points)]
    for k, rect in enumerate(points):
        tracker[k].start_track(img, dlib.rectangle(*rect))
    





    temp_tracker = list(tracker) #to remove the deleted trackers from tracker without affecting for loop 
    
    while True:
        # print tracker
        # print temp_tracker
        tracker = list(temp_tracker) 
        # Read frame from device or file
        retval, img = cam.read()
        if not retval:
            print "Cannot capture frame device | CODE TERMINATION....."
            exit()
        if(cv2.waitKey(10)==ord('p')):  #stop playing video if "p" pressed
            new_points = get_points.run(img, multi=True)  #new video to take tracking data
            
            if not new_points:
                print "ERROR: No new object added at last stop."
            else:
                # points.extend(new_points)
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
            # print len(tracker)
            # print i
            confdnc = tracker[i].update(img)
            # print type(confdnc)
            print confdnc
            # try:
            #   tracker[i].update(img)
            # except IndexError:
            #     del tracker[i]
            #     print "Object removed: couldn't identify, list index out of range."
            #     continue
            
            # Get the position of th object, draw a 
            # bounding box around it and display it.
            rect = tracker[i].get_position()
            pt1 = (int(rect.left()), int(rect.top()))
            pt2 = (int(rect.right()), int(rect.bottom()))

            # print type(pt1)
            # print type(temp_tracker)







            if (pt1[0]< threshld or pt2[0]>= width or pt1[1]< threshld or pt2[1]>=height):
                # del temp_tracker[i]
                print "Object removed: out of the frame"
                # continue
            if (confdnc < 3.5):
                print "Low Confidence"
                # continue










            cv2.rectangle(img, pt1, pt2, (255, 255, 255), 3)
            # print "Object {} tracked at [{}, {}] \r".format(i, pt1, pt2),

            # show location of box if mentionedd
            if dispLoc:
                loc = (int(rect.left()), int(rect.top()-20))
	        txt = "Object tracked at [{}, {}]".format(pt1, pt2)
	        cv2.putText(img, txt, loc , cv2.FONT_HERSHEY_SIMPLEX, .5, (255,255,255), 1)
        cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
        cv2.imshow("Image", img)
        # Continue until the user presses ESC key
        if cv2.waitKey(1) == 27:
            break

    # Relase the VideoCapture object
    cam.release()

if __name__ == "__main__":
    # Parse command line arguments
    parser = ap.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', "--deviceID", help="Device ID")
    group.add_argument('-v', "--videoFile", help="Path to Video File")
    parser.add_argument('-l', "--dispLoc", dest="dispLoc", action="store_true")
    args = vars(parser.parse_args())

    # Get the source of video
    if args["videoFile"]:
        source = args["videoFile"]
    else:
        source = int(args["deviceID"])
    run(source, args["dispLoc"])
