
import os
import numpy  as np
from PIL import Image

N_images = 90
N_buf_frames = 20
W = 4896
H = 3264

buffer = np.zeros((N_buf_frames, H, W, 3), dtype=float)

img_dir = r"/Users/paulkreymborg/Downloads/sep26_trialthree_tilted"
diffed_img_dir = r"/Users/paulkreymborg/Downloads/sep26_trialthree_tilted_DIFFED"

img_filenames = sorted([fn for fn  in os.listdir(img_dir) if fn.endswith(".JPG")])
print(img_filenames)

def read_img_as_float(img_fp):
    return np.array(Image.open(img_fp)).astype(float)


def get_diffed_img(img):
    print("finding past median")
    print("img shape: {}".format(img.shape))
    median_past_frames = np.median(buffer, axis=0)
    print("converting to BW")
    median_past_bw = np.mean(median_past_frames, axis=2)
    img_bw = np.mean(img, axis=2)
    bw_diff_from_median =  img_bw - median_past_bw
    print("finding percentiles")
    
    selected_window = bw_diff_from_median[2*H // 5:3* H // 5, 2*W // 5:3*W // 5]
    lower_cutoff, upper_cutoff = np.percentile(selected_window, [1,99])
    if upper_cutoff == lower_cutoff:
        raise Exception("Upper cutoff is same as lower cutoff")
    renormalized = (bw_diff_from_median - lower_cutoff) * 255 / (upper_cutoff -  lower_cutoff)
    print("renormalizing")
    # Reproduce original, with color tint the same
    pixel_wise_brightness_scaling = np.divide(renormalized, img_bw, out=np.zeros_like(renormalized), where=img_bw!=0)
    diffed_img = img * pixel_wise_brightness_scaling[:,:, np.newaxis]
    diffed_img[diffed_img < 0] = 0
    diffed_img[diffed_img >  255] = 255
    
    return  diffed_img
    # img_R, img_G, img_B = img[:,:,0], img[:,:,1], img[:,:,2]
    # img_R *= pixel_wise_brightness_scaling
    # img_G *= pixel_wise_brightness_scaling
    # img_B *= pixel_wise_brightness_scaling
    
    # img * 
    # renormalized / img_bw
    # img 
    

for i in range(N_images):
    print("i={}".format(i))
    img_name = img_filenames[i]
    img_i = read_img_as_float(os.path.join(img_dir, img_name))
    if i >= N_buf_frames:
        diffed_img_i = get_diffed_img(img_i).astype(np.uint8)
        save_diffed_fp = os.path.join(diffed_img_dir, img_name)
        Image.fromarray(diffed_img_i).save(save_diffed_fp)
        
    # print(img_i.shape)
    buffer[i % N_buf_frames] = img_i
    
    