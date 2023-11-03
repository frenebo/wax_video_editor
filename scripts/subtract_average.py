
import os
import numpy  as np
from PIL import Image, ImageFilter

H = 900
W = 600

win_bounds = [int(H*2/5), int(H*3/5), int(W*2/5), int(W*3/5)]


img_dir = r"C:\Users\Bob\Documents\wax_freezing_photos\23-11-03 nov03\1 trial one"
diffed_img_dir = r"C:\Users\Bob\Documents\PROCESSED\23-11-03\1_trialone_avg_subtracted"
os.makedirs(diffed_img_dir, exist_ok=True)

img_filenames = sorted([fn for fn  in os.listdir(img_dir) if fn.endswith(".JPG")])
print(img_filenames)

N_images = len(img_filenames)
N_buf_frames = 20

buffer = np.zeros((N_buf_frames, W, H, 3), dtype=float)

def read_img_as_float_and_resize_and_blur(img_fp):
    pil_img = Image.open(img_fp)
    pil_img = pil_img.resize([H,W], Image.LANCZOS)
    
    # pil_img = pil_img.filter(ImageFilter.GaussianBlur(radius=3))
    return np.array(pil_img).astype(float)


def get_diffed_img(img):
    print("finding past avg")
    print("img shape: {}".format(img.shape))
    avg_past_frames = np.mean(buffer, axis=0)
    print("converting to BW")
    
    # convert this frame, and avg past image, to black and white
    avg_past_bw = np.mean(avg_past_frames, axis=2)
    img_bw = np.mean(img, axis=2)
    
    # Correct average brightness to be equal within  window, to account for flickering
    # past_mean_within_window = np.mean(avg_past_bw[win_bounds[0]:win_bounds[1],win_bounds[2]:win_bounds[3]])
    # current_mean_within_window = np.mean(img_bw[win_bounds[0]:win_bounds[1],win_bounds[2]:win_bounds[3]])
    
    # img_bw *= past_mean_within_window / current_mean_within_window
    
    diff_from_past = (img_bw - avg_past_bw)
    window_diff_from_past = diff_from_past[win_bounds[0]:win_bounds[1],win_bounds[2]:win_bounds[3]]
    
        
    # bw_diff_from_avg =  img_bw - avg_past_bw
    print("finding percentiles")
    
    # selected_window = img_bw_window - avg_past_bw_window
    
    lower_cutoff, upper_cutoff = np.percentile(window_diff_from_past, [1,99])
    if upper_cutoff == lower_cutoff:
        raise Exception("Upper cutoff is same as lower cutoff")
    renormalized = (diff_from_past - lower_cutoff) * 255 / (upper_cutoff -  lower_cutoff)
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
    img_i = read_img_as_float_and_resize_and_blur(os.path.join(img_dir, img_name))
    if i >= N_buf_frames:
        diffed_img_i = get_diffed_img(img_i).astype(np.uint8)
        save_diffed_fp = os.path.join(diffed_img_dir, img_name)
        diffed_pil_img = Image.fromarray(diffed_img_i)
        diffed_pil_img = diffed_pil_img.filter(ImageFilter.MedianFilter(size = 3))
        diffed_pil_img.save(save_diffed_fp)
        
    # print(img_i.shape)
    buffer[i % N_buf_frames] = img_i
    
    