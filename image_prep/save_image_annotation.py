import argparse
import cv2
import json
import numpy as np
import os

#GLOBALS
# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
refPt = []
neg_refPt = []
window_side = 48
halfwin_side = window_side // 2
positive_examples = True
image = None

def batch_image_roi_collector(images_l, dirpath, shuffle_files = False, 
                                seen_files = None):
    """
    Save pixel locations of regions of interest across a batch of images.
    Images are displayed and a user clicks on ROIs in the image to be recorded.

    KEYBOARD USAGE:
    p: Set next clicks to be recorded as Positive Examples. Displays green box.
    n: Set next clicks to be recorded as Negative Examples. Displays blue box.
    r: Remove last clicked pixel from saved list. (i.e. if clicked accidentally
        or with wrong labeling of Pos/Neg). Displays white box.
    c: Move on to next image in the batch.
    q: Quit. 

    INPUT: 
    images_l: (list) of image filenames.
    dirpath: (str) File path to images.
    shuffle_files: (bool) Randomize the order images are shown.
    seen_files: (list) of image filenames, that are a subset of images_l, that 
                have been seen, and therefore should not be fetched again.

    OUTPUT:
    (list of dicts) Can be written to JSON. Contains: Image filename, lists of
        pixel locations for positive and negative examples. 
        E.g.:
        [{"img_file": "img0_1_37.7792471625_-122.395741018_zoom18.png", 
          "negative_points": [[366, 290], [420, 389], [457, 643]], 
          "positive_points": [[585, 436], [840, 283], [416, 187]]}, 
         {"img_file": "img-1_1_37.7792471625_-122.401920827_zoom18.png", 
         "negative_points": [[605, 259]], "positive_points": []}]
    """
    global image, refPt, neg_refPt, positive_examples
    img_roi_ds = []


    if seen_files is not None:
        original_images_len = len(images_l)
        images_l = np.setdiff1d(images_l, seen_files)
        #print "Removed {0} images from input images list.".format(original_images_len - len(images_l))
    if shuffle_files:
        np.random.shuffle(images_l)

    quit_called = False
    for img_fname in images_l:
    # load the image, clone it, and setup the mouse callback function
        if quit_called:
            break
        image = cv2.imread(os.path.join(dirpath, img_fname))

        ## DEPRECATED.
        ## Download file here instead of in google_satellite_images.py
        ## using the file name format
        ## e.g. img-1_0_37.7841313802_-122.401920827_zoom18.png
        # lat, lng = img_fname.split('_')[2:4]

        # map_byte_str = googlemapspixels.api_url_builder_requester(lat, lng)
        # map_arr = np.fromstring(map_byte_str, np.uint8)
        # image = cv2.imdecode(map_arr, cv2.CV_LOAD_IMAGE_COLOR)

        cv2.namedWindow("image")
        cv2.setMouseCallback("image", _click)
         
        # keep looping until the 'q' key is pressed
        while True:
            # display the image and wait for a keypress
            cv2.imshow("image", image)

            key = cv2.waitKey(1) & 0xFF
         
            # if the 'r' key is pressed, remove last click, display white box
            if key == ord("r"):
                if positive_examples and (len(refPt) > 0):
                    remove_coords = refPt[-1]
                    refPt = refPt[:-1]
                elif (not positive_examples) and (len(neg_refPt) > 0):
                    remove_coords = neg_refPt[-1]
                    neg_refPt = neg_refPt[:-1]
                else:
                    remove_coords = False

                if remove_coords:
                    upleft_corner = (remove_coords[0] - halfwin_side, \
                                        remove_coords[1] - halfwin_side)
                    lowright_corner = (remove_coords[0] + halfwin_side, \
                                        remove_coords[1] + halfwin_side)
                    cv2.rectangle(image, upleft_corner, lowright_corner, 
                                    (255, 255, 255), 2)

            elif key == ord("p"):
                positive_examples = True
            elif key == ord("n"):
                positive_examples = False
            # if the 'c' key is pressed, break from the loop, move to next image
            elif key == ord("c"):
                break
            elif key == ord("q"):
                quit_called = True
                break

        img_roi_ds.append({'img_file':img_fname, 
                           'positive_points':refPt, 
                           'negative_points':neg_refPt})
        refPt = []
        neg_refPt = []

    return img_roi_ds


def _click(event, x, y, flags, param):
    """
    Helper func.
    Record the pixel location of click on an image and annotate the image with
    a color coded box. Green box: recorded as a "positive example", Blue box: 
    recorded as a "negative example."

    Modified from:
    http://www.pyimagesearch.com/2015/03/09/capturing-mouse-click-events-with-python-and-opencv/
    """
    # grab references to the global variables
    global refPt, neg_refPt, positive_examples
 

    if event == cv2.EVENT_LBUTTONUP:
        # record the ending (x, y) coordinates and indicate that
        # And draw a colored box around the click point.
        if positive_examples:
            refPt.append((x, y))
            rect_color = (0, 255, 0)
        else:
            neg_refPt.append((x, y))
            rect_color = (255, 0, 0)

 
        # draw a rectangle around the region of interest
        upleft_corner = (x - halfwin_side, y - halfwin_side)
        lowright_corner = (x + halfwin_side, y + halfwin_side)
        cv2.rectangle(image, upleft_corner, lowright_corner, rect_color, 2)
        cv2.imshow("image", image)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument('textfile', help="File listing of images using naming convention.")
    ap.add_argument('-p', '--path', help="Path to images listed in textfile")
    json_help = "Path to json file of results, if some of the images in input textfile have been seen."
    ap.add_argument('-j', '--json', help=json_help)

    args = ap.parse_args()
    with open(args.textfile) as fin:
        images_l = [imgname.strip() for imgname in fin.readlines()]

    dirpath = args.path if args.path else ''

    if args.json:
        seen_files_json = json.load(open(args.json))
        seen_files = [x['img_file'] for x in seen_files_json]
    else:
        seen_files = None

    img_rois = batch_image_roi_collector(images_l, dirpath, 
                                            shuffle_files = True, 
                                            seen_files = seen_files)

    #include the previously input results with new output.
    if seen_files:
        img_rois.extend(seen_files_json)

    print json.dumps(img_rois)

