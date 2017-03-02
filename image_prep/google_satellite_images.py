import math
import os
import requests
from utils import spiral_stepper

class SatImageCollector(object):
    """
    Given a latitude, longitude and some other constraints (like zoom level) the 
    object can collect satellite images from the Google Maps API in spiral steps 
    around the initial location.
    """

    def __init__(self, latitude, longitude, max_tiles = 2500, zoom = 17, 
                    image_size = 640, scale = 2, save_dir = None, step_coords = None):
        """
        INPUT:
        latitude, longitude: (float) location on earth in decimal degrees.
        max_tiles: (int) Maximum number of images to collect from API
        zoom: (int) Google Maps API zoom level 
              (level 0 is ~entire Earth on 256x256 tile)
        image_size: (int) API call image pixel dimensions. 
                    True image dimensions of save files are scale * image_size
        scale: (int) Google Maps API scale param. Limited to 2 in free tier.
        save_dir: (str) Location on disk to save images
        step_coords: (list of pairs of ints) of translation steps to take 
                     from initial lat/lng. e.g.:
                     step_coords = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)]
                     would get images in a cross pattern.
                     If None, use spiral_stepper from utils.py.



        OUTPUT:
        None
        """

        self.init_lat = latitude
        self.init_lng = longitude
        self.max_tiles = max_tiles
        self.zoom = zoom
        self.image_size = image_size
        self.scale = scale
        self.save_dir = save_dir #if None, save in local directory

        #Google uses powers of 2 to define zoom, thus a scale of 2 represents zoom += 1 
        self.effective_zoom = self.zoom + math.log(self.scale, 2)
        if step_coords is None:
            self.step_coords = spiral_stepper(max_steps = self.max_tiles, 
                                    step_size = 1)

        self.image_info = None





    def setup_calls(self, image_overlap = 0.1):
        """
        Build a list for making calls to Google Maps API to get satellite coverage
        of an area around the initial lat/lng in a spiral pattern.
        INPUT:
        image_overlap: (float) Fraction of image to be repeated on the adjacent image.

        OUTPUT:
        (list of pairs) of the form [(file name, Google Maps url)], with form:
            'img_{xstep}_{ystep}_{latitude}_{longitude}_zoom{true zoom amount}.png',
            http://maps.googlemapsapis.com/... / WITHOUT the API KEY INCLUDED!
            


        """
        #how many pixels to move for adjacent image. should be 1152 with defaults set.
        pixel_step = math.floor((1.0 - image_overlap) * self.scale * self.image_size)
        center_pix = (self.scale * self.image_size) / 2.0
        lat0 = self.init_lat
        lng0 = self.init_lng

        fnames_urls = []
        fname_template = 'img{0}_{1}_{2}_{3}_zoom{4}.png'  
        maps_url1 = 'http://maps.googleapis.com/maps/api/staticmap?'
        maps_url2 = 'zoom={0}&size={1}x{1}&scale={2}&maptype=satellite&center={3},{4}'
        for x_trans, y_trans in self.step_coords:
            pix_x = center_pix + x_trans * pixel_step
            pix_y = center_pix + y_trans * pixel_step

            #requires square images
            lat1, lng1 = self._pix2latlng(pix_x, pix_y)

            fname = fname_template.format(x_trans, y_trans, 
                            lat1, lng1, int(self.effective_zoom))
            url_params = maps_url2.format(self.zoom, self.image_size, 
                            self.scale, lat1, lng1)
            fnames_urls.append( [fname, maps_url1 + url_params] )

        self.image_info = fnames_urls


    def get_images(self, api_key = None, verbose = True):
        """
        Make repeated calls to the Google Maps API to download a series
        of satellite images. 
        """

        if self.image_info is None:
            p_str1 = "Generating {0} API calls".format(int(self.max_tiles)) 
            p_str2 = """Overlap set to 10 percent. \n 
                        Adjust with: self.setup_calls(image_overlap = ?)."""
            print p_str1
            print p_str2

            self.setup_calls(image_overlap = 0.1)

        for img_fname, img_url in self.image_info:
            #first check if file is saved.
            fpath = os.path.join(self.save_dir, img_fname)
            if os.path.exists(fpath): 
                continue
            else:
                if api_key is not None:
                    img_url += '&key=' + api_key
                map_req = requests.get(img_url)

                if map_req.status_code != 200:
                    except_s = "Received a {0} error when requesting img: {1}"
                    raise Exception(except_s.format(map_req.status_code, fname))

                with open(fpath, 'wb') as fout:
                    fout.write(map_req.content)





    def _pix2latlng(self, pix_x, pix_y):
        """
        Given an x,y pixel location on a Google Map image (with known center lat/lng
        and zoom level) return the latitude and longitude of the pixel.
        Uses "Web Mercator" projection.

        pix_x, pix_y: pixel coordinate values (float)
        zoom:  (int)
        dim_x, dim_y: pixel dimensions of image


        Returns (lat, lng) tuple as floats.
        """

        imcenterlat = self.init_lat
        imcenterlng = self.init_lng
        dim = self.scale * self.image_size
        #Google uses powers of 2 to define zoom, thus a scale of 2 represents zoom += 1 
        zoom = self.effective_zoom
        


        ## Assumes pixel coordinates are centered so center of image 
        ## (with even-numbered dimensions) is 0.5 pix from dim / 2
        ## with zero-indexing subtract this factor
        center = (dim // 2.0) - 0.5

        scalefact = 128.0 * math.pow(2, zoom) / math.pi

        center_abs_x = scalefact * math.pi * ((imcenterlng / 180.) + 1.)
        y_term = (math.pi - math.log(math.tan(math.pi * (0.25 + imcenterlat/360.0))))
        center_abs_y = scalefact * y_term

        abs_pix_x = center_abs_x + (pix_x - center)
        abs_pix_y = center_abs_y + (pix_y - center)
        
        exp_term = math.exp(math.pi - (abs_pix_y/scalefact))
        lat = 180./math.pi * (2. * math.atan(exp_term) - (math.pi/2.0))
        lng = 180./math.pi * ((abs_pix_x/scalefact) - math.pi)

        return lat, lng








if __name__ == '__main__':
    # testing
    # #imgs_obj = SatImageCollector(36.1699390347, -115.139826918, max_tiles = 2500)
    # imgs_obj = SatImageCollector(29.7604243716,-95.3698001178, max_tiles = 2500)
    
    # for imgfile in [x[0] for x in imgs_obj.setup_calls()][-10:]:
    #     print imgfile

    # imgs_obj = SatImageCollector(29.7604243716,-95.3698001178, max_tiles = 5, save_dir = 'tmp')
    # import datetime
    # print datetime.datetime.now()
    # imgs_obj.get_images()
    # print datetime.datetime.now()


