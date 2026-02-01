#!/usr/bin/env python3
"""
Deep Pattern Analysis - Compare source to visible pixels in each tile.
Look for patterns like:
- XOR with x coordinate
- XOR with y coordinate
- XOR with (x + y)
- XOR with tile index
- Bit patterns based on position
"""

from PIL import Image
import numpy as np
from collections import Counter, defaultdict


def is_magenta(pixel):
    """Check if a pixel is magenta (mask color)."""
    r, g, b = pixel
    return r > 200 and g < 100 and b > 200


def load_images():
    """Load the source and masked images."""
    unmasked_path = "/Users/mayorwa/.gemini/antigravity/brain/b41034ca-7388-4475-ab91-f7cf69e2eae9/uploaded_image_0_1768776289553.png"
    masked_path = "/Users/mayorwa/.gemini/antigravity/brain/b41034ca-7388-4475-ab91-f7cf69e2eae9/uploaded_image_1_1768776289553.png"
    
    source = np.array(Image.open(unmasked_path).convert('RGB'))
    masked = np.array(Image.open(masked_path).convert('RGB'))
    
    return source, masked


def pixel_to_symbol(pixel):
    """Convert RGB pixel to a symbol for easier analysis."""
    r, g, b = pixel
    if r > 200 and g < 50 and b < 50:
        return 'R'  # Red
    elif r > 200 and g > 200 and b > 200:
        return 'W'  # White
    elif r < 50 and g < 50 and b < 50:
        return 'B'  # Black
    elif r > 200 and g < 100 and b > 200:
        return 'M'  # Magenta (mask)
    else:
        return '?'


def compare_rows(source, masked):
    """Compare each row between source and visible masked pixels."""
    src_h, src_w = source.shape[:2]
    tgt_h, tgt_w = masked.shape[:2]
    
    print("=" * 80)
    print("ROW-BY-ROW COMPARISON")
    print("=" * 80)
    
    # For each row, compare source to each visible tile position
    for y in range(min(20, tgt_h)):
        print(f"\n--- Row {y} ---")
        
        # Show source row
        src_row = ''.join(pixel_to_symbol(tuple(source[y, x])) for x in range(src_w))
        print(f"Source: {src_row}")
        
        # Show target row (with masking)
        tgt_row = ''.join(pixel_to_symbol(tuple(masked[y, x])) for x in range(tgt_w))
        print(f"Target: {tgt_row}")
        
        # Compare tile by tile
        for tile in range(tgt_w // src_w):
            start_x = tile * src_w
            tile_row = ''.join(pixel_to_symbol(tuple(masked[y, start_x + x])) for x in range(src_w))
            
            # Calculate difference
            diffs = []
            for x in range(src_w):
                src_sym = pixel_to_symbol(tuple(source[y, x]))
                tgt_sym = pixel_to_symbol(tuple(masked[y, start_x + x]))
                if tgt_sym == 'M':
                    diffs.append('.')
                elif src_sym == tgt_sym:
                    diffs.append('=')
                else:
                    diffs.append(f'{src_sym}>{tgt_sym}')
            
            # Count mismatches
            non_masked = [d for d in diffs if d != '.']
            mismatches = [d for d in non_masked if d != '=']
            if non_masked:
                match_rate = (len(non_masked) - len(mismatches)) / len(non_masked) * 100
                print(f"  Tile {tile}: {match_rate:.0f}% match, diffs: {mismatches[:5]}")


def analyze_xor_patterns(source, masked):
    """Check various XOR patterns."""
    src_h, src_w = source.shape[:2]
    tgt_h, tgt_w = masked.shape[:2]
    
    print("\n" + "=" * 80)
    print("XOR PATTERN ANALYSIS")
    print("=" * 80)
    
    # Map colors to values for XOR analysis
    # Red=0, White=1, Black=2
    color_map = {
        (255, 0, 0): 0,    # Red
        (255, 255, 255): 1,  # White
        (0, 0, 0): 2,      # Black
    }
    
    # Test: source[y][x] XOR (x // src_w)
    # Test: source[y][x] XOR (x)
    # Test: source[y][x] XOR (y)
    
    xor_tests = {
        'tile_idx': lambda x, y: x // src_w,
        'x_mod_2': lambda x, y: x % 2,
        'y_mod_2': lambda x, y: y % 2,
        'x_plus_y': lambda x, y: (x + y) % 2,
        'x_mod_8': lambda x, y: (x % 8),
        'x_div_8': lambda x, y: (x // 8) % 2,
    }
    
    for test_name, xor_func in xor_tests.items():
        matches = 0
        total = 0
        
        for y in range(tgt_h):
            for x in range(tgt_w):
                mp = tuple(masked[y, x])
                if is_magenta(mp):
                    continue
                
                sp = tuple(source[y % src_h, x % src_w])
                
                if sp not in color_map or mp not in color_map:
                    continue
                
                src_val = color_map[sp]
                tgt_val = color_map[mp]
                xor_val = xor_func(x, y)
                
                # Check if target = source XOR something
                predicted = (src_val + xor_val) % 3  # Try modular arithmetic
                
                total += 1
                if predicted == tgt_val:
                    matches += 1
        
        if total > 0:
            print(f"{test_name}: {matches}/{total} = {100*matches/total:.1f}%")


def find_transformation_by_position(source, masked):
    """For each position, find what transformation is applied."""
    src_h, src_w = source.shape[:2]
    tgt_h, tgt_w = masked.shape[:2]
    
    print("\n" + "=" * 80)
    print("POSITION-BASED TRANSFORMATION")
    print("=" * 80)
    
    # For each absolute x position, check what transformation maps source to target
    transformations = defaultdict(Counter)
    
    for x in range(tgt_w):
        src_x = x % src_w
        for y in range(tgt_h):
            mp = tuple(masked[y, x])
            if is_magenta(mp):
                continue
            
            sp = tuple(source[y, src_x])
            
            # Record the transformation
            trans = f"{pixel_to_symbol(sp)}->{pixel_to_symbol(mp)}"
            transformations[x][trans] += 1
    
    print("\nTransformations by x position (first 128):")
    for x in range(min(128, tgt_w)):
        if transformations[x]:
            most_common = transformations[x].most_common(3)
            trans_str = ', '.join(f"{t}:{c}" for t, c in most_common)
            print(f"  x={x:3d}: {trans_str}")


def analyze_bit_patterns(source, masked):
    """Analyze if transformations correlate with bit patterns of coordinates."""
    src_h, src_w = source.shape[:2]
    tgt_h, tgt_w = masked.shape[:2]
    
    print("\n" + "=" * 80)
    print("BIT PATTERN ANALYSIS")
    print("=" * 80)
    
    # Check if bit 6 of x (i.e., x >= 64) triggers transformation
    for bit in range(8):
        mask_bit = 1 << bit
        
        matches_when_set = 0
        total_when_set = 0
        matches_when_clear = 0
        total_when_clear = 0
        
        for x in range(tgt_w):
            src_x = x % src_w
            bit_is_set = (x & mask_bit) != 0
            
            for y in range(tgt_h):
                mp = tuple(masked[y, x])
                if is_magenta(mp):
                    continue
                
                sp = tuple(source[y, src_x])
                
                if bit_is_set:
                    total_when_set += 1
                    if mp == sp:
                        matches_when_set += 1
                else:
                    total_when_clear += 1
                    if mp == sp:
                        matches_when_clear += 1
        
        if total_when_set > 0 and total_when_clear > 0:
            pct_set = 100 * matches_when_set / total_when_set
            pct_clear = 100 * matches_when_clear / total_when_clear
            print(f"Bit {bit} (mask {mask_bit:3d}): set={pct_set:5.1f}% match, clear={pct_clear:5.1f}% match")


def extract_exact_differences(source, masked):
    """Extract the exact differences for each mismatch."""
    src_h, src_w = source.shape[:2]
    tgt_h, tgt_w = masked.shape[:2]
    
    print("\n" + "=" * 80)
    print("EXACT MISMATCH DETAILS (first 50)")
    print("=" * 80)
    
    count = 0
    for y in range(tgt_h):
        for x in range(tgt_w):
            mp = tuple(masked[y, x])
            if is_magenta(mp):
                continue
            
            src_x = x % src_w
            sp = tuple(source[y, src_x])
            
            if mp != sp:
                tile = x // src_w
                print(f"  ({x:3d},{y:2d}) tile={tile} local_x={src_x:2d}: src={pixel_to_symbol(sp)} tgt={pixel_to_symbol(mp)}")
                count += 1
                if count >= 50:
                    return


def main():
    source, masked = load_images()
    
    # Run analyses
    compare_rows(source, masked)
    extract_exact_differences(source, masked)
    analyze_bit_patterns(source, masked)
    analyze_xor_patterns(source, masked)


if __name__ == "__main__":
    main()
