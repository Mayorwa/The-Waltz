#!/usr/bin/env python3
"""
Test bitwise relationship between local_x and y for tile 1 swaps.
Key observations:
- y=7 (binary 0000111): swaps at local_x = 0,1,2,4,8,16,32
  - These are: 0, and powers of 2 up to 32
  - 0 = 000000, 1 = 000001, 2 = 000010, 4 = 000100, 8 = 001000, 16 = 010000, 32 = 100000
  - None of these have MORE than one bit set!
  - So: swap when popcount(local_x) <= 1 ?

Let me verify this pattern.
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


def is_red(p):
    return p[0] > 200 and p[1] < 50 and p[2] < 50


def swap_bw(p):
    r, g, b = p
    if r > 200 and g > 200 and b > 200:
        return (0, 0, 0)
    elif r < 50 and g < 50 and b < 50:
        return (255, 255, 255)
    return tuple(p)


def test_rules(source, masked):
    """Test various bitwise rules."""
    src_h, src_w = source.shape[:2]
    tgt_h, tgt_w = masked.shape[:2]
    
    # Collect tile 1 swaps and no-swaps
    swap_positions = []
    no_swap_positions = []
    
    for y in range(tgt_h):
        for x in range(64, 128):
            mp = tuple(masked[y, x])
            if is_magenta(mp):
                continue
            
            local_x = x % src_w
            sp = tuple(source[y, local_x])
            
            if is_red(sp):
                continue
            
            if mp != sp:
                swap_positions.append((local_x, y))
            else:
                no_swap_positions.append((local_x, y))
    
    print(f"Tile 1: {len(swap_positions)} swaps, {len(no_swap_positions)} no-swaps")
    
    # Test rules
    rules = [
        ("popcount(local_x) == 0", lambda lx, y: bin(lx).count('1') == 0),
        ("popcount(local_x) <= 1", lambda lx, y: bin(lx).count('1') <= 1),
        ("popcount(local_x) <= popcount(y)", lambda lx, y: bin(lx).count('1') <= bin(y).count('1')),
        ("(lx & ~y) == 0", lambda lx, y: (lx & ~y) == 0),  # All bits of lx are in y
        ("popcount(lx & ~y) == 0", lambda lx, y: bin(lx & (~y & 63)).count('1') == 0),  # Same as above
        ("popcount(lx & y) == popcount(lx)", lambda lx, y: bin(lx & y).count('1') == bin(lx).count('1')),
        ("(lx | y) == y", lambda lx, y: (lx | y) == y),  # lx is subset of y bits
        ("lx < y", lambda lx, y: lx < y),
        ("lx <= y", lambda lx, y: lx <= y),
        ("lx == 0 or popcount(lx & y) > 0", lambda lx, y: lx == 0 or bin(lx & y).count('1') > 0),
        ("all bits of lx in y (lx & y == lx)", lambda lx, y: (lx & y) == lx),
    ]
    
    print("\n--- Testing rules ---")
    for name, rule in rules:
        match_swap = sum(1 for lx, y in swap_positions if rule(lx, y))
        match_no_swap = sum(1 for lx, y in no_swap_positions if not rule(lx, y))
        total = len(swap_positions) + len(no_swap_positions)
        correct = match_swap + match_no_swap
        print(f"{name}: {correct}/{total} = {100*correct/total:.1f}% (swap_correct={match_swap}, no_swap_correct={match_no_swap})")
    
    # Let me look at y=7 more carefully
    print("\n--- y=7 analysis ---")
    y = 7
    y_bin = bin(y)
    print(f"y=7 binary: {format(y, '06b')}")
    
    for lx in range(64):
        expected_swap = any((slx, sy) == (lx, y) for slx, sy in swap_positions)
        lx_and_y = lx & y
        lx_bits = bin(lx).count('1')
        y_bits = bin(y).count('1')
        lx_and_y_bits = bin(lx_and_y).count('1')
        lx_subset_y = (lx & y) == lx
        
        if expected_swap or lx < 10:
            print(f"  local_x={lx:2d} ({format(lx, '06b')}): swap={expected_swap}, lx&y={format(lx_and_y, '06b')}, lx_subset_y={lx_subset_y}")


def main():
    source, masked = load_images()
    test_rules(source, masked)


if __name__ == "__main__":
    main()
