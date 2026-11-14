import cv2
import numpy as np
from PIL import Image

# Inpaint watermark in corner (bottom-right region: w-160 to w-20, h-120 to h-20)
def remove_flow_star(img_bgr):
    h, w = img_bgr.shape[:2]
    
    # Extract bottom right patch
    x1, y1 = max(0, w - 180), max(0, h - 140)
    x2, y2 = w - 10, h - 10
    patch = img_bgr[y1:y2, x1:x2]
    
    # The Flow watermark star is semi-transparent whitish/lighter than background
    gray_patch = cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY)
    
    # Adaptive threshold / morphological top-hat to isolate the star
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    tophat = cv2.morphologyEx(gray_patch, cv2.MORPH_TOPHAT, kernel)
    
    # Threshold the tophat
    _, mask = cv2.threshold(tophat, 18, 255, cv2.THRESH_BINARY)
    
    # Dilate mask slightly to cover edges of the star
    dilated_mask = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)), iterations=2)
    
    # Inpaint patch
    inpainted_patch = cv2.inpaint(patch, dilated_mask, 5, cv2.INPAINT_TELEA)
    
    # Put back
    res = img_bgr.copy()
    res[y1:y2, x1:x2] = inpainted_patch
    return res

# Test on flow_raw_5.jpg and flow_raw_6.jpg
for fn in ["flow_raw_5.jpg", "flow_raw_6.jpg"]:
    img = cv2.imread(rf"C:\Users\CHAU\.gemini\antigravity\scratch\happyco-cloud-poster\output\flow_images\{fn}")
    clean = remove_flow_star(img)
    out_p = rf"C:\Users\CHAU\.gemini\antigravity\brain\3a554760-1f55-4a71-9c90-718eb795bd64\clean_{fn}"
    cv2.imwrite(out_p, clean)
    print(f"Cleaned {fn} saved to {out_p}")
