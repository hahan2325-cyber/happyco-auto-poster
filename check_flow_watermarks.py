import cv2
import numpy as np
from PIL import Image

# Let's inspect the 4 corners and bottom of flow_raw_1.jpg, flow_raw_10.jpg, flow_raw_11.jpg, flow_raw_5.jpg, flow_raw_6.jpg
files = ["flow_raw_1.jpg", "flow_raw_10.jpg", "flow_raw_11.jpg", "flow_raw_5.jpg", "flow_raw_6.jpg"]
base = r"C:\Users\CHAU\.gemini\antigravity\scratch\happyco-cloud-poster\output\flow_images"

for fn in files:
    img = Image.open(f"{base}\\{fn}")
    w, h = img.size
    print(f"\n--- {fn} ({w}x{h}) ---")
    
    # Check bottom-right 120x60
    br = img.crop((w - 120, h - 60, w, h))
    br.save(rf"C:\Users\CHAU\.gemini\antigravity\brain\3a554760-1f55-4a71-9c90-718eb795bd64\br_{fn}.png")
    
    # Check bottom-left 120x60
    bl = img.crop((0, h - 60, 120, h))
    bl.save(rf"C:\Users\CHAU\.gemini\antigravity\brain\3a554760-1f55-4a71-9c90-718eb795bd64\bl_{fn}.png")
    
    # Check top-right 120x60
    tr = img.crop((w - 120, 0, w, 60))
    tr.save(rf"C:\Users\CHAU\.gemini\antigravity\brain\3a554760-1f55-4a71-9c90-718eb795bd64\tr_{fn}.png")

print("\nDone cropping corners.")
