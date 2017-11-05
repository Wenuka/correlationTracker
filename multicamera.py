# Import the required modules
import dlib
import cv2
import argparse as ap
import get_points

def run(source=0, source2=0, dispLoc=False):
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
        if(cv2.waitKey(10)==ord('p')):  #stop playing video if "p" pressed
            break
        cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
        cv2.namedWindow("Image2", cv2.WINDOW_NORMAL)
        cv2.imshow("Image", img)
        cv2.imshow("Image2", img2)
    cv2.destroyWindow("Image")  # video stopped
    # cv2.destroyWindow("Image2")  # video stopped
    threshld = 10
    height = len(img) -threshld
    width = len(img[0]) -threshld
    limit = height - 40
    # print height
    # print width
    print limit


    # Co-ordinates of objects to be tracked 
    # will be stored in a list named `points`
    points = get_points.run(img, multi=True)  #new video to take tracking data
    points2 = []
    print points
    if not points:
        print "ERROR: No object to be tracked initially."
        # exit()
    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    # cv2.namedWindow("Image2", cv2.WINDOW_NORMAL)
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
         #    if dispLoc:
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
            # if dispLoc:
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

if __name__ == "__main__":
    # Parse command line arguments
    parser = ap.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', "--deviceID", help="Device ID")
    # group.add_argument('-f', "--deviceID2", help="Device ID")
    group.add_argument('-v', "--videoFile", help="Path to Video File")
    # group.add_argument('-w', "--videoFile2", help="Path to Video File 2")
    parser.add_argument('-l', "--dispLoc", dest="dispLoc", action="store_true")
    args = vars(parser.parse_args())

    # Get the source of video
    if args["videoFile"]:
        source = args["videoFile"]
        source2 = 'vid/cam2.avi'    #***********************************
        # source2 = args["videoFile2"]
    else:
        source = int(args["deviceID"])
        source2 = 'vid/cam2.avi'    #************************************
        # source2 = int(args["deviceID2"])
    run(source, source2, args["dispLoc"])
