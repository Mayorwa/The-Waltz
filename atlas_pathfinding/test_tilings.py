#!/usr/bin/env python3
"""
Pattern Generator V7 - Try different tiling strategies.

Since v2 (simple tiling) is close, let's try:
1. Horizontal mirroring of tiles
2. Vertical shifts
3. Different combinations
"""

from PIL import Image
import numpy as np


def is_magenta(pixel):
    r, g, b = pixel
    return r > 200 and g < 100 and b > 200


def load_images():
    unmasked_path = "/Users/mayorwa/.gemini/antigravity/brain/b41034ca-7388-4475-ab91-f7cf69e2eae9/uploaded_image_0_1768776289553.png"
    masked_path = "/Users/mayorwa/.gemini/antigravity/brain/b41034ca-7388-4475-ab91-f7cf69e2eae9/uploaded_image_1_1768776289553.png"
    
    source = np.array(Image.open(unmasked_path).convert('RGB'))
    masked = np.array(Image.open(masked_path).convert('RGB'))
    
    return source, masked


def try_different_tilings(source, masked):
    """Try different tiling strategies and compare accuracy."""
    src_h, src_w = source.shape[:2]
    height, width = masked.shape[:2]
    
    strategies = []
    
    # Strategy 1: Simple repeat (v2)
    def simple_repeat(x, y):
        return source[y % src_h, x % src_w]
    strategies.append(("simple_repeat", simple_repeat))
    
    # Strategy 2: Horizontal mirror every other tile
    def h_mirror_alt(x, y):
        tile_idx = x // src_w
        local_x = x % src_w
        if tile_idx % 2 == 1:  # Mirror for odd tiles
            local_x = src_w - 1 - local_x
        return source[y % src_h, local_x]
    strategies.append(("h_mirror_alt", h_mirror_alt))
    
    # Strategy 3: Vertical mirror every other tile
    def v_mirror_alt(x, y):
        tile_idx = x // src_w
        local_y = y % src_h
        if tile_idx % 2 == 1:
            local_y = src_h - 1 - local_y
        return source[local_y, x % src_w]
    strategies.append(("v_mirror_alt", v_mirror_alt))
    
    # Strategy 4: Both mirrors for odd tiles
    def both_mirror_alt(x, y):
        tile_idx = x // src_w
        local_x = x % src_w
        local_y = y % src_h
        if tile_idx % 2 == 1:
            local_x = src_w - 1 - local_x
            local_y = src_h - 1 - local_y
        return source[local_y, local_x]
    strategies.append(("both_mirror_alt", both_mirror_alt))
    
    # Strategy 5: Rotate 180 for odd tiles
    def rotate_180_alt(x, y):
        tile_idx = x // src_w
        local_x = x % src_w
        local_y = y % src_h
        if tile_idx % 2 == 1:
            local_x = src_w - 1 - local_x
        return source[local_y, local_x]
    strategies.append(("rotate_180_alt", rotate_180_alt))
    
    # Strategy 6: Shift by half width for odd tiles
    def shift_half(x, y):
        tile_idx = x // src_w
        local_x = x % src_w
        if tile_idx % 2 == 1:
            local_x = (local_x + src_w // 2) % src_w
        return source[y % src_h, local_x]
    strategies.append(("shift_half", shift_half))
    
    # Strategy 7: Use tile index as offset
    def tile_offset(x, y):
        tile_idx = x // src_w
        local_x = (x + tile_idx) % src_w
        return source[y % src_h, local_x]
    strategies.append(("tile_offset", tile_offset))
    
    # Test each strategy
    best_strategy = None
    best_accuracy = 0
    
    print("Testing tiling strategies:")
    print("=" * 60)
    
    for name, func in strategies:
        matches = 0
        total = 0
        
        for y in range(height):
            for x in range(width):
                mp = tuple(masked[y, x])
                if is_magenta(mp):
                    continue
                
                predicted = tuple(func(x, y))
                total += 1
                if mp == predicted:
                    matches += 1
        
        accuracy = matches / total * 100
        print(f"{name}: {matches}/{total} = {accuracy:.2f}%")
        
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_strategy = name
    
    print(f"\nBest: {best_strategy} with {best_accuracy:.2f}%")
    return best_strategy


def main():
    source, masked = load_images()
    try_different_tilings(source, masked)


if __name__ == "__main__":
    main()
