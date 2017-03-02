import argparse
import json
from matplotlib.image import imread, imsave
from numpy import shape
import os

def posneg_dict2roi_images(posneg_d, roi_dims, in_path = ''):
    """
    Load image listed in posneg_d, cut out regions of interest based
    on center points in posneg_d and roi_dims (dimensions).  Return 
    these as arrays in posneg_d with keys: positive/negative_roi_arrs.

    INPUT:
    posneg_d: (dict) of the form:
                {'img_file': 'img-10_-10_36.2198109_-115.201625_zoom18.png',
                 'negative_points': [[396, 548], [710, 455]],
                 'positive_points': [[535, 670], [535, 301], [1056, 664]]}

    in_path: (str) dir path to parent of image 'img_file'
    roi_dims: (pair of ints) pixel dimension of image to cut from image

    OUTPUT
    (dict) A modified posneg_d that includes numpy arrays of the ROIS.
    """
    if (in_path != '') and (not os.path.isdir(in_path)):
        raise Exception("Can't find directory: {0}".format(in_path))

    img_arr = imread(os.path.join(in_path, posneg_d['img_file']))
    col_centdim = roi_dims[0] // 2
    row_centdim = roi_dims[1] // 2
    row_totdim, col_totdim, _ = shape(img_arr)

    for point_key in ['positive_points', 'negative_points']:
        if point_key in posneg_d:
            for col_num, row_num in posneg_d[point_key]:
                
                #check if roi is too close to edge:
                edgechecks = 0
                edgechecks += (row_num < row_centdim)
                edgechecks += (col_num < col_centdim)
                edgechecks += ((row_num + row_centdim) > row_totdim)
                edgechecks += ((col_num + col_centdim) > col_totdim)
                if edgechecks > 0:
                    continue

 
                roi_img = img_arr[(row_num-row_centdim):(row_num+row_centdim), 
                                  (col_num-col_centdim):(col_num+col_centdim), 
                                  :]

                roi_key = point_key.split('_')[0] + "_roi_arrs"
                if roi_key in posneg_d:
                    posneg_d[roi_key][str((col_num,row_num))] = roi_img
                else:
                    posneg_d[roi_key] = {str((col_num,row_num)): roi_img}

    return posneg_d


def batch_roi_writer(posneg_d_l,imgs_path = '', out_path = '', 
                            roi_dims = [48, 48], file_num = 0):
    """
    Given a list of dicts (see posneg_dict2roi_images for dict specifications)
    load images and write region of interest cutout images into 'positive_sample'
    and 'negative_sample' directories.  Use a simple numbering system for the 
    image writes, so add a lookup to posneg_d and return that.

    INPUT:
    posneg_d_l: (list) of posneg_dict2roi_images
    roi_dims: (pair of ints) dimensions of image to cut from image
    imgs_path/out_path: (str) dir path to parent of image 'img_file'/where to 
                        write the sample directories with ROI images. 
    file_num: (int) Initial number to increment to name the sample images.
    
    OUTPUT:
    writes: image cutouts of regions of interest
    returns: (dict) modified posneg_ds
    """ 

    out_dirnames = ['positive_samples', 'negative_samples']
    for out_dir in out_dirnames:
        if (out_path == '') or os.path.isdir(out_path):
            writepath = os.path.join(out_path, out_dir)
            if not os.path.isdir(writepath):
                os.mkdir(writepath)
        else:
            raise Exception("Can't find directory: {0}".format(out_path))

    posneg_d_lredo = []
    new_keys = ['positive_roi_arrs', 'negative_roi_arrs']
    for pn_d in posneg_d_l:
        pn_dcopy = pn_d.copy()
        pn_dcopy = posneg_dict2roi_images(pn_dcopy, roi_dims, 
                                            in_path = imgs_path)
        
        for key, subpath in zip(new_keys, out_dirnames):
            if key in pn_dcopy:
                for tup in pn_dcopy[key]:
                    img_arr = pn_dcopy[key][tup]
                    fname = str(file_num) + '.png'
                    fpath_out = os.path.join(out_path, subpath, fname)

                    imsave(fpath_out, img_arr)
                    pn_dcopy[key][tup] = fpath_out
                    file_num += 1
                    posneg_d_lredo.append(pn_dcopy)

    return posneg_d_lredo


if __name__ == '__main__':
    """
    example usage:
    python cut_and_save_rois.py image_metadata/roi_pixel_info.json \
     -p input/image/dir \
     -o output/rois/dir \
     > output_metadata.json
    """
    ap = argparse.ArgumentParser()
    jsonin_help = "Path to json file of results of running save_image_annotation."
    ap.add_argument('jsonin', help = jsonin_help)
    ap.add_argument('-p', '--path', help="Path to images listed in textfile")
    outpath_help = "Path where positive_samples/negative_samples dirs will be created/added to."
    ap.add_argument('-o', '--outpath', help = outpath_help)
    ap.add_argument('-d', '--dims', help="Side length of cutout (assumed to be square).")
    ap.add_argument('-n', '--number', help="File number to start with.")


    args = ap.parse_args()
    posneg_d_in = json.load(open(args.jsonin))

    in_path = args.path if args.path else ''
    out_path = args.outpath if args.outpath else ''
    roi_dims = [int(args.dims), int(args.dims)] if args.dims else [48, 48]
    file_num = int(args.number) if args.number else 0

    posneg_d_out = batch_roi_writer(posneg_d_in, imgs_path=in_path, out_path=out_path,
                                    roi_dims=roi_dims, file_num=file_num)    