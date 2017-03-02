# Image collection, labeling, segmentation.

To collect images from the Google Maps API. Modify and run the main block of google_satellite_images.py. 

To save the pixel locations of regions of interest in these images, run save_image_annotation.py.
This file is meant to be run with arguments. Calling instructions are available via: `python save_image_annotation.py -h`
Example usage: `python save_image_annotation.py listing_of_image_filenames.txt -p path/to/images/directory > image_annotation.json`

When running this program, a user clicks on the regions of interest in a batch of images. Both "positive examples" and "negative examples" can be saved by hitting the "p" key or the "n" key, respectively, before clicking. All hot keys used are:  
    KEYBOARD USAGE:
    p: Set next clicks to be recorded as Positive Examples. Displays green box.
    n: Set next clicks to be recorded as Negative Examples. Displays blue box.
    r: Remove last clicked pixel from saved list. (i.e. if clicked accidentally
        or with wrong labeling of Pos/Neg). Displays white box.
    c: Move on to next image in the batch.
    q: Quit. 

Note: save_image_annotation.py requires OpenCV.