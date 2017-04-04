## Neural Nets Practice
I collected a sample of about 1200 satellite images for playing around with neural net packages. For classification I settled on identifying swimming pools as my goal. I hand labeled about 500 images of pools in the Las Vegas area taken from Google Maps using the image_prep pipeline with a standard zoom level. I also collected about 700 examples of images that do not contain pools. Using these images as a training dataset, I tested out some packages.

### Nolearn.
See nolearn.py.  Mostly based on the tutorial notebook found in the Nolearn repo: https://github.com/dnouri/nolearn 
I get about 80% accuracy on a hold out set after 50 backpropagation iterations.