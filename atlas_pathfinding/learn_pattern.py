#!/usr/bin/env python3
"""
Learn the exact pattern by building a lookup table from visible pixels.
Since we have the source (64x64) and partial target (256x64 with masks),
we can learn exactly what transformation happens for each visible position.
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


def is_white(p):
    return p[0] > 200 and p[1] > 200 and p[2] > 200


def is_black(p):
    return p[0] < 50 and p[1] < 50 and p[2] < 50


def pixel_to_char(p):
    if is_red(p):
        return 'R'
    elif is_white(p):
        return 'W'
    elif is_black(p):
        return 'B'
    return '?'


def learn_transformation(source, masked):
    """Learn the transformation by examining visible pixels."""
    src_h, src_w = source.shape[:2]
    tgt_h, tgt_w = masked.shape[:2]
    
    # For each position (x, y), learn if src->tgt is identity or swap
    # We'll store this as a pattern
    
    # Group by local_x, local_y (within tile)
    transformations = defaultdict(list)  # (local_x, local_y) -> list of (is_swapped, tile_idx)
    
    for y in range(tgt_h):
        for x in range(tgt_w):
            mp = tuple(masked[y, x])
            if is_magenta(mp):
                continue
            
            local_x = x % src_w
            local_y = y  # Since y < 64, it's always the same
            tile_idx = x // src_w
            
            sp = tuple(source[local_y, local_x])
            
            if is_red(sp):
                continue  # Red never swaps
            
            is_swapped = mp != sp
            transformations[(local_x, local_y)].append((is_swapped, tile_idx))
    
    # Analyze patterns
    print("Transformation patterns by position:")
    print("=" * 60)
    
    # For each position, show which tiles swap
    swap_by_pos = {}
    for pos, trans_list in sorted(transformations.items()):
        local_x, local_y = pos
        swaps_at = [tile_idx for (is_swapped, tile_idx) in trans_list if is_swapped]
        no_swaps_at = [tile_idx for (is_swapped, tile_idx) in trans_list if not is_swapped]
        
        if swaps_at:
            swap_by_pos[pos] = set(swaps_at)
    
    # Check if swap pattern depends on local coordinates
    print("\nPositions that swap (sample):")
    count = 0
    for pos, swap_tiles in list(swap_by_pos.items())[:50]:
        local_x, local_y = pos
        print(f"  ({local_x:2d},{local_y:2d}): swaps in tiles {sorted(swap_tiles)}")
        count += 1
    
    # See if there's a pattern based on tile AND local position
    print("\n" + "=" * 60)
    print("Checking if pattern depends on (local_x XOR tile_x) relationship:")
    
    # NEW IDEA: Maybe the transformation uses the source pixel pattern itself
    # as part of the XOR mask
    
    # Let's extract the source pattern as a bit field
    source_bits = np.zeros((src_h, src_w), dtype=np.uint8)
    for y in range(src_h):
        for x in range(src_w):
            sp = tuple(source[y, x])
            if is_white(sp):
                source_bits[y, x] = 1
            elif is_black(sp):
                source_bits[y, x] = 0
            else:  # Red
                source_bits[y, x] = 2  # Special
    
    # Check: does the swap happen when source_bits[y, x%64] XOR (tile_idx * something)?
    swap_positions = []
    no_swap_positions = []
    
    for y in range(tgt_h):
        for x in range(tgt_w):
            mp = tuple(masked[y, x])
            if is_magenta(mp):
                continue
            
            local_x = x % src_w
            sp = tuple(source[y, local_x])
            
            if is_red(sp):
                continue
            
            if mp != sp:
                swap_positions.append((x, y))
            else:
                no_swap_positions.append((x, y))
    
    print(f"\nSwap positions: {len(swap_positions)}")
    print(f"No-swap positions: {len(no_swap_positions)}")
    
    # Test: swap when source pixel at (x-64, y) differs from source at (x%64, y)
    # i.e., looking at the "next tile" in source
    print("\n--- Testing if swap relates to neighboring source pixels ---")
    
    for offset in [64, 32, 16, 8, 4, 2, 1]:
        match_swap = 0
        match_no_swap = 0
        
        for x, y in swap_positions:
            local_x = x % src_w
            neighbor_x = (x - offset) % src_w if x >= offset else local_x
            
            src_here = source_bits[y, local_x]
            src_neighbor = source_bits[y, neighbor_x]
            
            if src_here != 2 and src_neighbor != 2:  # Not red
                if src_here != src_neighbor:
                    match_swap += 1
        
        for x, y in no_swap_positions:
            local_x = x % src_w
            neighbor_x = (x - offset) % src_w if x >= offset else local_x
            
            src_here = source_bits[y, local_x]
            src_neighbor = source_bits[y, neighbor_x]
            
            if src_here != 2 and src_neighbor != 2:
                if src_here == src_neighbor:
                    match_no_swap += 1
        
        total = len(swap_positions) + len(no_swap_positions) 
        correct = match_swap + match_no_swap
        if total > 0:
            print(f"  Offset {offset}: {correct}/{total} = {100*correct/total:.1f}%")
    
    return swap_by_pos


def main():
    source, masked = load_images()
    learn_transformation(source, masked)


if __name__ == "__main__":
    main()
