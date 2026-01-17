#!/usr/bin/env python3
"""
Focus on tile 1 only - find exact swap rule.
All 636 swaps occur in tile 1 (x=64-127).
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


def analyze_tile1(source, masked):
    """Analyze only tile 1 swaps."""
    src_h, src_w = source.shape[:2]
    tgt_h, tgt_w = masked.shape[:2]
    
    # Collect all swap and no-swap in tile 1
    swap_positions = []
    no_swap_positions = []
    
    for y in range(tgt_h):
        for x in range(64, 128):  # Tile 1 only
            mp = tuple(masked[y, x])
            if is_magenta(mp):
                continue
            
            local_x = x % src_w
            sp = tuple(source[y, local_x])
            
            if is_red(sp):
                continue
            
            if mp != sp:
                swap_positions.append((x, y, local_x))
            else:
                no_swap_positions.append((x, y, local_x))
    
    print(f"Tile 1: {len(swap_positions)} swaps, {len(no_swap_positions)} no-swaps")
    
    # Analyze by y
    print("\n--- By Y coordinate ---")
    swap_by_y = defaultdict(list)
    no_swap_by_y = defaultdict(list)
    
    for x, y, local_x in swap_positions:
        swap_by_y[y].append(local_x)
    for x, y, local_x in no_swap_positions:
        no_swap_by_y[y].append(local_x)
    
    # Show rows with highest swap rates
    for y in sorted(set(list(swap_by_y.keys()) + list(no_swap_by_y.keys()))):
        swaps = len(swap_by_y[y])
        no_swaps = len(no_swap_by_y[y])
        total = swaps + no_swaps
        if total > 0:
            pct = 100 * swaps / total
            swap_local = sorted(swap_by_y[y])[:10] if swap_by_y[y] else []
            print(f"y={y:2d}: {pct:5.1f}% swap ({swaps:2d}/{total:2d})  swap at local_x={swap_local}")
    
    # The KEY test: swap when local_x < y?
    print("\n--- Testing local_x < y rule ---")
    match = 0
    for x, y, local_x in swap_positions:
        if local_x < y:
            match += 1
    print(f"Swap positions where local_x < y: {match}/{len(swap_positions)}")
    
    match = 0
    for x, y, local_x in no_swap_positions:
        if local_x >= y:
            match += 1
    print(f"No-swap positions where local_x >= y: {match}/{len(no_swap_positions)}")
    
    # Test: swap when local_x & y == local_x (i.e., all bits of local_x are in y)
    print("\n--- Testing (local_x & y) == local_x rule ---")
    match_swap = sum(1 for x, y, lx in swap_positions if (lx & y) == lx)
    match_no_swap = sum(1 for x, y, lx in no_swap_positions if (lx & y) != lx)
    total = len(swap_positions) + len(no_swap_positions)
    correct = match_swap + match_no_swap
    print(f"Accuracy: {correct}/{total} = {100*correct/total:.1f}%")
    
    # Test: swap when local_x <= y
    print("\n--- Testing local_x <= y rule ---")
    match_swap = sum(1 for x, y, lx in swap_positions if lx <= y)
    match_no_swap = sum(1 for x, y, lx in no_swap_positions if lx > y)
    total = len(swap_positions) + len(no_swap_positions)
    correct = match_swap + match_no_swap
    print(f"Accuracy: {correct}/{total} = {100*correct/total:.1f}%")
    
    # Test: swap when (local_x & y) has all bits of local_x
    # i.e., y has all the 1-bits that local_x has
    print("\n--- Testing if y has all bits of local_x ---")
    for thresh in range(7):
        match_swap = sum(1 for x, y, lx in swap_positions 
                        if bin(lx & y).count('1') >= bin(lx).count('1') - thresh)
        match_no_swap = sum(1 for x, y, lx in no_swap_positions 
                          if bin(lx & y).count('1') < bin(lx).count('1') - thresh)
        total = len(swap_positions) + len(no_swap_positions)
        correct = match_swap + match_no_swap
        print(f"popcount(lx & y) >= popcount(lx) - {thresh}: {correct}/{total} = {100*correct/total:.1f}%")


def main():
    source, masked = load_images()
    analyze_tile1(source, masked)


if __name__ == "__main__":
    main()
