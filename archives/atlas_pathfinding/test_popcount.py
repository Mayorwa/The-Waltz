#!/usr/bin/env python3
"""
Test popcount(x & y) based rule.
The swap happens when the number of 1 bits in (x AND y) is odd.
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


def should_swap_popcount(x, y):
    """Swap when popcount(x & y) is odd."""
    return bin(x & y).count('1') % 2 == 1


def generate_and_verify(source, masked, rule_func, rule_name, output_path):
    """Generate output using a rule and verify."""
    src_h, src_w = source.shape[:2]
    tgt_h, tgt_w = masked.shape[:2]
    
    output = np.zeros((tgt_h, tgt_w, 3), dtype=np.uint8)
    
    for y in range(tgt_h):
        for x in range(tgt_w):
            src_x = x % src_w
            sp = tuple(source[y % src_h, src_x])
            
            if rule_func(x, y) and not is_red(sp):
                output[y, x] = swap_bw(sp)
            else:
                output[y, x] = sp
    
    # Verify
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
                if len(mismatch_examples) < 5:
                    mismatch_examples.append((x, y, mp, op))
    
    total = matches + mismatches
    print(f"{rule_name}: {matches}/{total} = {100*matches/total:.2f}%")
    if mismatch_examples:
        for x, y, expected, got in mismatch_examples:
            print(f"  ({x},{y}): expected {expected}, got {got}")
    
    # Save
    result = Image.fromarray(output)
    result.save(output_path)
    print(f"  Saved: {output_path}")
    
    return matches / total


def main():
    source, masked = load_images()
    
    # Test multiple rules
    rules = [
        ("popcount(x & y) odd", lambda x, y: bin(x & y).count('1') % 2 == 1),
        ("popcount(x ^ y) odd", lambda x, y: bin(x ^ y).count('1') % 2 == 1),
        ("popcount(x | y) odd", lambda x, y: bin(x | y).count('1') % 2 == 1),
        ("popcount(x) ^ popcount(y) = 1", lambda x, y: (bin(x).count('1') + bin(y).count('1')) % 2 == 1),
        ("(x >> 6) & 1 and popcount(y) odd", lambda x, y: ((x >> 6) & 1) and (bin(y).count('1') % 2 == 1)),
        ("(x >= 64) and popcount(y) odd", lambda x, y: (x >= 64) and (bin(y).count('1') % 2 == 1)),
        ("popcount(x & y) >= 2", lambda x, y: bin(x & y).count('1') >= 2),
        ("popcount(x & y) >= 3", lambda x, y: bin(x & y).count('1') >= 3),
        ("popcount(x & y) >= 4", lambda x, y: bin(x & y).count('1') >= 4),
    ]
    
    base_path = "/Users/mayorwa/Documents/Personal/The-Waltz/atlas_pathfinding"
    
    best_rule = None
    best_acc = 0
    
    for rule_name, rule_func in rules:
        output_path = f"{base_path}/test_output.png"
        acc = generate_and_verify(source, masked, rule_func, rule_name, output_path)
        if acc > best_acc:
            best_acc = acc
            best_rule = rule_name
    
    print(f"\nBest rule: {best_rule} with {100*best_acc:.2f}% accuracy")


if __name__ == "__main__":
    main()
