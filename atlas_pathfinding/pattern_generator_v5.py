#!/usr/bin/env python3
"""
Pattern Generator V5 - Uses discovered XOR rule.

Key rule discovered:
- Swap black/white when (x >> 6) ^ (y >> 6) != 0
- Red pixels never change
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
    """Swap black and white, keep red."""
    r, g, b = p
    if r > 200 and g > 200 and b > 200:  # White -> Black
        return (0, 0, 0)
    elif r < 50 and g < 50 and b < 50:  # Black -> White
        return (255, 255, 255)
    return p  # Red stays red


def should_swap(x, y):
    """Determine if black/white should be swapped at position (x, y)."""
    # Key rule: swap when (x >> 6) XOR (y >> 6) != 0
    return ((x >> 6) ^ (y >> 6)) != 0


def generate_output(source, masked, output_path):
    """Generate output using the XOR swap rule."""
    src_h, src_w = source.shape[:2]
    tgt_h, tgt_w = masked.shape[:2]
    
    print(f"Source: {src_w}x{src_h}")
    print(f"Target: {tgt_w}x{tgt_h}")
    
    output = np.zeros((tgt_h, tgt_w, 3), dtype=np.uint8)
    
    for y in range(tgt_h):
        for x in range(tgt_w):
            src_x = x % src_w
            sp = tuple(source[y % src_h, src_x])
            
            if should_swap(x, y) and not is_red(sp):
                output[y, x] = swap_bw(sp)
            else:
                output[y, x] = sp
    
    result = Image.fromarray(output)
    result.save(output_path)
    print(f"Saved: {output_path}")
    
    return output


def verify_output(output, masked):
    """Verify output matches visible pixels."""
    tgt_h, tgt_w = masked.shape[:2]
    
    matches = 0
    mismatches = 0
    mismatch_examples = []
    
    for y in range(tgt_h):
        for x in range(tgt_w):
            mp = tuple(masked[y, x])
            if is_magenta(mp):
                continue
            
            op = tuple(output[y, x])
            
            if mp == op:
                matches += 1
            else:
                mismatches += 1
                if len(mismatch_examples) < 10:
                    mismatch_examples.append((x, y, mp, op))
    
    total = matches + mismatches
    print(f"\nVerification: {matches}/{total} = {100*matches/total:.2f}%")
    
    if mismatch_examples:
        print("\nMismatch examples:")
        for x, y, expected, got in mismatch_examples:
            print(f"  ({x},{y}): expected {expected}, got {got}")
    
    return matches, mismatches


def main():
    source, masked = load_images()
    
    output_path = "/Users/mayorwa/Documents/Personal/The-Waltz/atlas_pathfinding/pattern_output_v5.png"
    output = generate_output(source, masked, output_path)
    verify_output(output, masked)


if __name__ == "__main__":
    main()
