#!/usr/bin/env python3
"""
Pattern Generator V3 - Creates output by:
1. Keeping all visible pixels from the masked image as-is
2. Filling magenta areas using the source pattern tile
"""

from PIL import Image
import numpy as np


def is_magenta(pixel):
    """Check if a pixel is magenta (mask color)."""
    r, g, b = pixel
    return r > 200 and g < 100 and b > 200


def generate_output():
    """Generate the final output image."""
    unmasked_path = "/Users/mayorwa/.gemini/antigravity/brain/b41034ca-7388-4475-ab91-f7cf69e2eae9/uploaded_image_0_1768776289553.png"
    masked_path = "/Users/mayorwa/.gemini/antigravity/brain/b41034ca-7388-4475-ab91-f7cf69e2eae9/uploaded_image_1_1768776289553.png"
    output_path = "/Users/mayorwa/Documents/Personal/The-Waltz/atlas_pathfinding/pattern_output_v2.png"
    
    source = np.array(Image.open(unmasked_path).convert('RGB'))
    masked = np.array(Image.open(masked_path).convert('RGB'))
    
    src_height, src_width = source.shape[:2]
    height, width = masked.shape[:2]
    
    print(f"Source: {src_width}x{src_height}")
    print(f"Target: {width}x{height}")
    
    # Create output starting with a tiled source
    output = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Fill with tiled source pattern first
    for y in range(height):
        for x in range(width):
            output[y, x] = source[y % src_height, x % src_width]
    
    # Count replacements
    visible_count = 0
    magenta_count = 0
    
    # Now overlay visible pixels from masked image
    for y in range(height):
        for x in range(width):
            mp = tuple(masked[y, x])
            if is_magenta(mp):
                magenta_count += 1
                # Keep the tiled value
            else:
                visible_count += 1
                # Use the visible pixel from masked image
                output[y, x] = masked[y, x]
    
    print(f"Visible pixels copied: {visible_count}")
    print(f"Magenta pixels filled from source: {magenta_count}")
    
    result = Image.fromarray(output)
    result.save(output_path)
    print(f"Saved: {output_path}")
    
    return output_path


def verify_output(output_path, masked_path):
    """Verify the output matches all visible pixels."""
    output = np.array(Image.open(output_path).convert('RGB'))
    masked = np.array(Image.open(masked_path).convert('RGB'))
    
    height, width = masked.shape[:2]
    matches = 0
    total = 0
    
    for y in range(height):
        for x in range(width):
            mp = tuple(masked[y, x])
            if is_magenta(mp):
                continue
            
            op = tuple(output[y, x])
            total += 1
            if mp == op:
                matches += 1
    
    print(f"\nVerification: {matches}/{total} visible pixels match ({100*matches/total:.1f}%)")


def main():
    output_path = generate_output()
    
    masked_path = "/Users/mayorwa/.gemini/antigravity/brain/b41034ca-7388-4475-ab91-f7cf69e2eae9/uploaded_image_1_1768776289553.png"
    verify_output(output_path, masked_path)


if __name__ == "__main__":
    main()
