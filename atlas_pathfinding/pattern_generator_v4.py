#!/usr/bin/env python3
"""
Pattern Generator V4 - Uses XOR pattern discovery.

Key findings:
- At row 7, mismatches occur at local_x = 0,1,2,4,8,16,32 (powers of 2 pattern!)
- At row 15, ALL white/black are swapped in tiles 1-2
- Red pixels never change
- The XOR pattern seems based on some bit manipulation of x and y

Let me check if: for non-red pixels, the swap happens when:
(x XOR y) has certain bits set, or
(x AND y) matches a pattern
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
    """Swap black and white, keep red."""
    r, g, b = p
    if r > 200 and g < 50 and b < 50:  # Red
        return p
    elif r > 200 and g > 200 and b > 200:  # White -> Black
        return (0, 0, 0)
    elif r < 50 and g < 50 and b < 50:  # Black -> White
        return (255, 255, 255)
    return p


def analyze_xor_condition(source, masked):
    """Find the XOR condition that triggers B/W swap."""
    src_h, src_w = source.shape[:2]
    tgt_h, tgt_w = masked.shape[:2]
    
    # Collect all swaps and non-swaps for B/W pixels
    swap_positions = []
    no_swap_positions = []
    
    for y in range(tgt_h):
        for x in range(tgt_w):
            mp = tuple(masked[y, x])
            if is_magenta(mp):
                continue
            
            src_x = x % src_w
            sp = tuple(source[y, src_x])
            
            # Skip red pixels
            if is_red(sp) or is_red(mp):
                continue
            
            if mp == sp:
                no_swap_positions.append((x, y))
            elif mp == swap_bw(sp):
                swap_positions.append((x, y))
    
    print(f"Swap positions: {len(swap_positions)}")
    print(f"No-swap positions: {len(no_swap_positions)}")
    
    # Analyze what they have in common
    print("\n--- Analyzing swap conditions ---")
    
    # Test various XOR conditions
    conditions = [
        ("x & y", lambda x, y: x & y),
        ("x ^ y", lambda x, y: x ^ y),
        ("(x ^ y) & 63", lambda x, y: (x ^ y) & 63),
        ("(x + y) & 63", lambda x, y: (x + y) & 63),
        ("x & 63", lambda x, y: x & 63),
        ("y & 63", lambda x, y: y & 63),
        ("(x >> 6) ^ (y >> 6)", lambda x, y: (x >> 6) ^ (y >> 6)),
    ]
    
    for name, func in conditions:
        swap_values = set(func(x, y) for x, y in swap_positions)
        no_swap_values = set(func(x, y) for x, y in no_swap_positions)
        
        only_swap = swap_values - no_swap_values
        only_no_swap = no_swap_values - swap_values
        
        if only_swap or only_no_swap:
            print(f"\n{name}:")
            if only_swap:
                print(f"  Only in SWAP: {sorted(only_swap)[:20]}")
            if only_no_swap:
                print(f"  Only in NO-SWAP: {sorted(only_no_swap)[:20]}")
    
    # Check if popcount (number of 1 bits) in x^y determines swap
    print("\n--- Checking popcount(x ^ y) ---")
    for popcount_threshold in range(8):
        swap_correct = 0
        no_swap_correct = 0
        
        for x, y in swap_positions:
            if bin(x ^ y).count('1') >= popcount_threshold:
                swap_correct += 1
        
        for x, y in no_swap_positions:
            if bin(x ^ y).count('1') < popcount_threshold:
                no_swap_correct += 1
        
        total = len(swap_positions) + len(no_swap_positions)
        correct = swap_correct + no_swap_correct
        print(f"  popcount >= {popcount_threshold}: {correct}/{total} = {100*correct/total:.1f}%")
    
    # Check specific bit patterns
    print("\n--- Checking if (x & y) has specific bits ---")
    for bit in range(8):
        mask = 1 << bit
        swap_match = sum(1 for x, y in swap_positions if (x & y) & mask)
        no_swap_match = sum(1 for x, y in no_swap_positions if (x & y) & mask)
        
        print(f"  bit {bit}: swap has it {100*swap_match/len(swap_positions):.1f}%, no-swap has it {100*no_swap_match/len(no_swap_positions):.1f}%")
    
    return swap_positions, no_swap_positions


def check_position_pattern(swap_positions:list, no_swap_positions:list):
    """Further analysis of position patterns."""
    print("\n" + "=" * 60)
    print("DETAILED POSITION ANALYSIS")
    print("=" * 60)
    
    # Group by y
    swap_by_y = defaultdict(list)
    for x, y in swap_positions:
        swap_by_y[y].append(x)
    
    print("\nRows with swaps (x values):")
    for y in sorted(swap_by_y.keys())[:20]:
        xs = sorted(swap_by_y[y])
        print(f"  y={y:2d}: {xs[:15]}{'...' if len(xs) > 15 else ''}")
        
        # Check if xs follow a pattern
        if len(xs) > 1:
            diffs = [xs[i+1] - xs[i] for i in range(len(xs)-1)]
            if len(set(diffs)) == 1:
                print(f"         Constant diff: {diffs[0]}")


def main():
    source, masked = load_images()
    swap_pos, no_swap_pos = analyze_xor_condition(source, masked)
    check_position_pattern(swap_pos, no_swap_pos)


if __name__ == "__main__":
    main()
