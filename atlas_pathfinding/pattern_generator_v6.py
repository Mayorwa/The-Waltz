#!/usr/bin/env python3
"""
Pattern Generator V6 - Building on V2 with smarter masked area filling.

V2 approach:
1. Keep all visible pixels from masked image exactly
2. Fill magenta areas with tiled source pattern

V6 improvements:
- Analyze the neighborhood around each masked pixel to infer the best fill
- Use visible pixels to determine if any local transformation is applied
"""

from PIL import Image
import numpy as np


def is_magenta(pixel):
    r, g, b = pixel
    return r > 200 and g < 100 and b > 200


def is_red(p):
    return p[0] > 200 and p[1] < 50 and p[2] < 50


def is_white(p):
    return p[0] > 200 and p[1] > 200 and p[2] > 200


def is_black(p):
    return p[0] < 50 and p[1] < 50 and p[2] < 50


def swap_bw(p):
    """Swap black and white."""
    if is_white(p):
        return (0, 0, 0)
    elif is_black(p):
        return (255, 255, 255)
    return tuple(p)


def load_images():
    unmasked_path = "/Users/mayorwa/.gemini/antigravity/brain/b41034ca-7388-4475-ab91-f7cf69e2eae9/uploaded_image_0_1768776289553.png"
    masked_path = "/Users/mayorwa/.gemini/antigravity/brain/b41034ca-7388-4475-ab91-f7cf69e2eae9/uploaded_image_1_1768776289553.png"
    
    source = np.array(Image.open(unmasked_path).convert('RGB'))
    masked = np.array(Image.open(masked_path).convert('RGB'))
    
    return source, masked


def check_local_transformation(source, masked, x, y, src_w):
    """
    Check nearby visible pixels to see if there's a transformation applied.
    Returns True if we should swap B/W, False otherwise.
    """
    height, width = masked.shape[:2]
    
    # Look at neighboring visible pixels and compare with source
    swap_votes = 0
    no_swap_votes = 0
    
    # Check neighbors in a small window
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            if dx == 0 and dy == 0:
                continue
            
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                mp = tuple(masked[ny, nx])
                if is_magenta(mp):
                    continue
                
                # Get source pixel
                src_x = nx % src_w
                sp = tuple(source[ny, src_x])
                
                if is_red(sp):
                    continue
                
                # Check if this neighbor is swapped or not
                if mp == sp:
                    no_swap_votes += 1
                elif mp == swap_bw(sp):
                    swap_votes += 1
    
    # If more neighbors are swapped, swap this pixel too
    return swap_votes > no_swap_votes


def generate_output_v6(source, masked, output_path):
    """Generate output with contextual filling."""
    src_h, src_w = source.shape[:2]
    height, width = masked.shape[:2]
    
    print(f"Source: {src_w}x{src_h}")
    print(f"Target: {width}x{height}")
    
    output = np.zeros((height, width, 3), dtype=np.uint8)
    
    filled_simple = 0
    filled_swapped = 0
    visible_copied = 0
    
    for y in range(height):
        for x in range(width):
            mp = tuple(masked[y, x])
            
            if is_magenta(mp):
                # This is a masked pixel - need to fill it
                src_x = x % src_w
                sp = tuple(source[y % src_h, src_x])
                
                # Check if neighborhood suggests a swap
                if not is_red(sp) and check_local_transformation(source, masked, x, y, src_w):
                    output[y, x] = swap_bw(sp)
                    filled_swapped += 1
                else:
                    output[y, x] = sp
                    filled_simple += 1
            else:
                # Visible pixel - copy exactly
                output[y, x] = masked[y, x]
                visible_copied += 1
    
    print(f"Visible copied: {visible_copied}")
    print(f"Masked filled (simple): {filled_simple}")
    print(f"Masked filled (swapped): {filled_swapped}")
    
    result = Image.fromarray(output)
    result.save(output_path)
    print(f"Saved: {output_path}")
    
    return output


def verify_output(output, masked):
    """Verify visible pixels match."""
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
    
    print(f"\nVerification: {matches}/{total} visible pixels match ({100*matches/total:.2f}%)")


def main():
    source, masked = load_images()
    
    output_path = "/Users/mayorwa/Documents/Personal/The-Waltz/atlas_pathfinding/pattern_output_v6.png"
    output = generate_output_v6(source, masked, output_path)
    verify_output(output, masked)


if __name__ == "__main__":
    main()
