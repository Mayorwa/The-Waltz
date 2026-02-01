#!/usr/bin/env python3
"""
Analyze which rows have swaps vs which don't.
"""

from PIL import Image
import numpy as np
from collections import defaultdict


def is_magenta(pixel):
    r, g, b = pixel
    return r > 200 and g < 100 and b > 200


def load_images():
    unmasked_path = "/Users/mayorwa/.gemini/antigravity/brain/b41034ca-7388-4475-ab91-f7cf69e2eae9/uploaded_image_0_1768776289553.png"
    masked_path = "/Users/mayorwa/.gemini/antigravity/brain/b41034ca-7388-4475-ab91-f7cf69e2eae9/uploaded_image_1_1768776289553.png"
    
    source = np.array(Image.open(unmasked_path).convert('RGB'))
    masked = np.array(Image.open(masked_path).convert('RGB'))
    
    return source, masked


def is_red(p):
    return p[0] > 200 and p[1] < 50 and p[2] < 50


def swap_bw(p):
    r, g, b = p
    if r > 200 and g > 200 and b > 200:
        return (0, 0, 0)
    elif r < 50 and g < 50 and b < 50:
        return (255, 255, 255)
    return p


def analyze_by_row(source, masked):
    """Analyze swap pattern for each row."""
    src_h, src_w = source.shape[:2]
    tgt_h, tgt_w = masked.shape[:2]
    
    print("Row-by-row swap analysis:")
    print("=" * 60)
    
    row_has_swap = {}
    
    for y in range(tgt_h):
        swaps = 0
        no_swaps = 0
        red_pixels = 0
        masked_pixels = 0
        
        # Only look at tiles 1-3 (x >= 64) since tile 0 is always direct
        for x in range(64, tgt_w):
            mp = tuple(masked[y, x])
            if is_magenta(mp):
                masked_pixels += 1
                continue
            
            src_x = x % src_w
            sp = tuple(source[y % src_h, src_x])
            
            if is_red(sp):
                red_pixels += 1
                continue
            
            if mp == sp:
                no_swaps += 1
            elif mp == swap_bw(sp):
                swaps += 1
        
        total_bw = swaps + no_swaps
        if total_bw > 0:
            swap_rate = 100 * swaps / total_bw
            row_has_swap[y] = swap_rate > 50
            status = "SWAP" if swap_rate > 50 else ("mixed" if swap_rate > 0 else "direct")
            print(f"Row {y:2d}: {status:6s} swap={swaps:3d} direct={no_swaps:3d} red={red_pixels:2d} masked={masked_pixels:3d} ({swap_rate:5.1f}% swap)")
        else:
            print(f"Row {y:2d}: N/A (all red or masked)")
    
    # Analyze pattern in row indices
    print("\n" + "=" * 60)
    print("Pattern analysis:")
    
    swap_rows = [y for y, has_swap in row_has_swap.items() if has_swap]
    direct_rows = [y for y, has_swap in row_has_swap.items() if not has_swap]
    
    print(f"\nSwap rows: {swap_rows[:20]}...")
    print(f"Direct rows: {direct_rows[:20]}...")
    
    # Check if it's odd/even
    swap_odd = sum(1 for y in swap_rows if y % 2 == 1)
    swap_even = sum(1 for y in swap_rows if y % 2 == 0)
    print(f"\nSwap rows: {swap_odd} odd, {swap_even} even")
    
    # Check binary patterns
    print("\nBit analysis of swap rows:")
    for bit in range(6):
        set_count = sum(1 for y in swap_rows if (y >> bit) & 1)
        clear_count = len(swap_rows) - set_count
        print(f"  Bit {bit}: {set_count} have it set, {clear_count} have it clear")


def main():
    source, masked = load_images()
    analyze_by_row(source, masked)


if __name__ == "__main__":
    main()
