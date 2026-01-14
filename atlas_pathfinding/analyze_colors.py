#!/usr/bin/env python3
"""Analyze colors in the terrain image to understand the terrain types."""

from PIL import Image
import numpy as np
from collections import Counter

def analyze_image(image_path):
    img = Image.open(image_path).convert('RGB')
    pixels = np.array(img)
    height, width = pixels.shape[:2]
    
    # Collect unique colors and their counts
    color_counts = Counter()
    
    for y in range(height):
        for x in range(width):
            rgb = tuple(pixels[y, x])
            color_counts[rgb] += 1
    
    # Get the most common colors
    print("Most common colors in the image:")
    for color, count in color_counts.most_common(20):
        percentage = (count / (height * width)) * 100
        print(f"  RGB{color}: {count} pixels ({percentage:.2f}%)")
    
    return color_counts

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        analyze_image(sys.argv[1])
