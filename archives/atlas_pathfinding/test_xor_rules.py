#!/usr/bin/env python3
"""
Deep XOR bit analysis - find the exact bit rule for swapping.
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
    return p


def test_xor_rules(source, masked):
    """Test various XOR bit rules."""
    src_h, src_w = source.shape[:2]
    tgt_h, tgt_w = masked.shape[:2]
    
    # Collect swap and no-swap positions
    swap_positions = []
    no_swap_positions = []
    
    for y in range(tgt_h):
        for x in range(tgt_w):
            mp = tuple(masked[y, x])
            if is_magenta(mp):
                continue
            
            src_x = x % src_w
            sp = tuple(source[y % src_h, src_x])
            
            if is_red(sp):
                continue
            
            if mp == sp:
                no_swap_positions.append((x, y))
            elif mp == swap_bw(sp):
                swap_positions.append((x, y))
    
    print(f"Swap: {len(swap_positions)}, No-swap: {len(no_swap_positions)}")
    
    # Test rules of form: swap when (x & mask_x) CONDITION (y & mask_y)
    # Condition = XOR, AND, etc.
    print("\n" + "=" * 60)
    print("Testing XOR bit combinations")
    print("=" * 60)
    
    # Test: swap when popcount(x & y) has specific parity
    for parity in [0, 1]:
        match_swap = sum(1 for x, y in swap_positions if bin(x & y).count('1') % 2 == parity)
        match_no_swap = sum(1 for x, y in no_swap_positions if bin(x & y).count('1') % 2 != parity)
        total = len(swap_positions) + len(no_swap_positions)
        correct = match_swap + match_no_swap
        print(f"popcount(x & y) % 2 == {parity}: {correct}/{total} = {100*correct/total:.1f}%")
    
    # Test: swap when popcount(x ^ y) has specific parity
    for parity in [0, 1]:
        match_swap = sum(1 for x, y in swap_positions if bin(x ^ y).count('1') % 2 == parity)
        match_no_swap = sum(1 for x, y in no_swap_positions if bin(x ^ y).count('1') % 2 != parity)
        total = len(swap_positions) + len(no_swap_positions)
        correct = match_swap + match_no_swap
        print(f"popcount(x ^ y) % 2 == {parity}: {correct}/{total} = {100*correct/total:.1f}%")
    
    # Test: swap when (x & y) has bit N set
    for bit in range(8):
        match_swap = sum(1 for x, y in swap_positions if (x & y) & (1 << bit))
        match_no_swap = sum(1 for x, y in no_swap_positions if not ((x & y) & (1 << bit)))
        total = len(swap_positions) + len(no_swap_positions)
        correct = match_swap + match_no_swap
        print(f"(x & y) bit {bit} set: {correct}/{total} = {100*correct/total:.1f}%")
    
    # Test: swap when (x ^ y) has bit N set
    print("\n--- Swap when (x ^ y) has bit N set ---")
    for bit in range(8):
        match_swap = sum(1 for x, y in swap_positions if (x ^ y) & (1 << bit))
        match_no_swap = sum(1 for x, y in no_swap_positions if not ((x ^ y) & (1 << bit)))
        total = len(swap_positions) + len(no_swap_positions)
        correct = match_swap + match_no_swap
        print(f"(x ^ y) bit {bit} set: {correct}/{total} = {100*correct/total:.1f}%")
    
    # Test: the AND of multiple bits
    print("\n--- Testing multiple bit conditions ---")
    # Swap when (x ^ y) has BOTH bit 6 and bit N set
    for bit in range(6):
        match_swap = sum(1 for x, y in swap_positions 
                        if ((x ^ y) & (1 << 6)) and ((x ^ y) & (1 << bit)))
        match_no_swap = sum(1 for x, y in no_swap_positions 
                          if not (((x ^ y) & (1 << 6)) and ((x ^ y) & (1 << bit))))
        total = len(swap_positions) + len(no_swap_positions)
        correct = match_swap + match_no_swap
        print(f"(x ^ y) bits 6 AND {bit} set: {correct}/{total} = {100*correct/total:.1f}%")
    
    # Test: x_tile AND y relationship
    print("\n--- Testing tile-based rules ---")
    # tile = x // 64
    for rule_name, rule_func in [
        ("tile & y bit 0", lambda x, y: ((x // 64) & (y & 1)) != 0),
        ("tile & (y >> 1)", lambda x, y: ((x // 64) & (y >> 1)) != 0),
        ("tile & y", lambda x, y: ((x // 64) & y) != 0),
        ("popcount(tile & y) odd", lambda x, y: bin((x // 64) & y).count('1') % 2 == 1),
        ("tile * y odd", lambda x, y: ((x // 64) * y) % 2 == 1),
        ("(x // 64) & (y // 8) odd", lambda x, y: ((x // 64) & (y // 8)) % 2 == 1),
    ]:
        match_swap = sum(1 for x, y in swap_positions if rule_func(x, y))
        match_no_swap = sum(1 for x, y in no_swap_positions if not rule_func(x, y))
        total = len(swap_positions) + len(no_swap_positions)
        correct = match_swap + match_no_swap
        print(f"{rule_name}: {correct}/{total} = {100*correct/total:.1f}%")
    
    # THE KEY TEST: if source pixel value XOR with something = target
    print("\n--- Check if pattern depends on source pixel color ---")
    # Get black-only and white-only positions
    black_swap = []
    white_swap = []
    black_no_swap = []
    white_no_swap = []
    
    for x, y in swap_positions:
        src_x = x % src_w
        sp = tuple(source[y, src_x])
        if sp == (0, 0, 0):
            black_swap.append((x, y))
        elif sp == (255, 255, 255):
            white_swap.append((x, y))
    
    for x, y in no_swap_positions:
        src_x = x % src_w
        sp = tuple(source[y, src_x])
        if sp == (0, 0, 0):
            black_no_swap.append((x, y))
        elif sp == (255, 255, 255):
            white_no_swap.append((x, y))
    
    print(f"Black pixels: {len(black_swap)} swap, {len(black_no_swap)} no-swap")
    print(f"White pixels: {len(white_swap)} swap, {len(white_no_swap)} no-swap")


def main():
    source, masked = load_images()
    test_xor_rules(source, masked)


if __name__ == "__main__":
    main()
