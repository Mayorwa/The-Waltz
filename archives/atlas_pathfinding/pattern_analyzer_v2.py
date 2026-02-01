#!/usr/bin/env python3
"""
Pattern Analyzer V2 - Investigates the transformation between tiles.
The pattern might involve XOR, inversion, mirroring, or shifts.
"""

from PIL import Image
import numpy as np

def load_images():
    """Load the source and masked images."""
    unmasked_path = "/Users/mayorwa/.gemini/antigravity/brain/b41034ca-7388-4475-ab91-f7cf69e2eae9/uploaded_image_0_1768776289553.png"
    masked_path = "/Users/mayorwa/.gemini/antigravity/brain/b41034ca-7388-4475-ab91-f7cf69e2eae9/uploaded_image_1_1768776289553.png"
    
    unmasked = np.array(Image.open(unmasked_path).convert('RGB'))
    masked = np.array(Image.open(masked_path).convert('RGB'))
    
    return unmasked, masked


def is_magenta(pixel):
    """Check if a pixel is magenta."""
    r, g, b = pixel
    return r > 200 and g < 100 and b > 200


def analyze_tile_relationship(source, masked):
    """Analyze how tiles relate to the source pattern."""
    height, width = masked.shape[:2]
    src_height, src_width = source.shape[:2]
    
    num_tiles = width // src_width
    print(f"Source: {src_width}x{src_height}")
    print(f"Target: {width}x{height}")
    print(f"Number of horizontal tiles: {num_tiles}")
    
    # Extract visible pixels from each tile
    for tile_idx in range(num_tiles):
        start_x = tile_idx * src_width
        end_x = start_x + src_width
        
        print(f"\n--- Tile {tile_idx} (x: {start_x}-{end_x}) ---")
        
        # Count matches with different transformations
        transformations = {
            'direct': lambda p: p,
            'invert_bw': lambda p: (255 - p[0], 255 - p[1], 255 - p[2]) if p not in [(255, 0, 0)] else p,
            'xor_255': lambda p: (p[0] ^ 255, p[1] ^ 255, p[2] ^ 255),
            'mirror_h': None,  # Will handle separately
            'mirror_v': None,  # Will handle separately
        }
        
        for trans_name in ['direct', 'invert_bw', 'xor_255']:
            trans = transformations[trans_name]
            matches = 0
            total = 0
            
            for y in range(height):
                for x in range(src_width):
                    masked_pixel = tuple(masked[y, start_x + x])
                    
                    if is_magenta(masked_pixel):
                        continue
                    
                    source_pixel = tuple(source[y % src_height, x])
                    transformed = trans(source_pixel)
                    
                    total += 1
                    if masked_pixel == transformed:
                        matches += 1
            
            if total > 0:
                acc = (matches / total) * 100
                print(f"  {trans_name}: {matches}/{total} = {acc:.1f}%")
        
        # Try horizontal mirror
        matches = 0
        total = 0
        for y in range(height):
            for x in range(src_width):
                masked_pixel = tuple(masked[y, start_x + x])
                if is_magenta(masked_pixel):
                    continue
                source_pixel = tuple(source[y % src_height, src_width - 1 - x])
                total += 1
                if masked_pixel == source_pixel:
                    matches += 1
        if total > 0:
            print(f"  mirror_h: {matches}/{total} = {(matches/total)*100:.1f}%")
        
        # Try vertical mirror
        matches = 0
        total = 0
        for y in range(height):
            for x in range(src_width):
                masked_pixel = tuple(masked[y, start_x + x])
                if is_magenta(masked_pixel):
                    continue
                source_pixel = tuple(source[(src_height - 1 - y) % src_height, x])
                total += 1
                if masked_pixel == source_pixel:
                    matches += 1
        if total > 0:
            print(f"  mirror_v: {matches}/{total} = {(matches/total)*100:.1f}%")


def analyze_pixel_patterns(source, masked):
    """Look at specific pixel coordinates to find pattern."""
    height, width = masked.shape[:2]
    src_height, src_width = source.shape[:2]
    
    print("\n--- Pixel-by-pixel comparison at key positions ---")
    
    # Check first few rows across all tiles
    for y in [0, 1, 7, 8]:
        print(f"\nRow {y}:")
        for tile in range(4):
            base_x = tile * src_width
            samples = []
            for dx in [0, 1, 2, 4, 8]:
                x = base_x + dx
                if x < width:
                    mp = tuple(masked[y, x])
                    sp = tuple(source[y % src_height, dx])
                    if is_magenta(mp):
                        samples.append(f"({dx}:M)")
                    else:
                        match = "=" if mp == sp else "!"
                        samples.append(f"({dx}:{match})")
            print(f"  Tile {tile}: {' '.join(samples)}")


def check_row_xor_pattern(source, masked):
    """Check if there's an XOR pattern based on row index."""
    height, width = masked.shape[:2]
    src_height, src_width = source.shape[:2]
    
    print("\n--- Checking if row index affects transformation ---")
    
    for y in range(min(16, height)):
        row_matches = {'direct': 0, 'invert': 0, 'total': 0}
        
        for x in range(width):
            mp = tuple(masked[y, x])
            if is_magenta(mp):
                continue
            
            sp = tuple(source[y % src_height, x % src_width])
            row_matches['total'] += 1
            
            if mp == sp:
                row_matches['direct'] += 1
            elif mp == (255 - sp[0], 255 - sp[1], 255 - sp[2]):
                row_matches['invert'] += 1
        
        if row_matches['total'] > 0:
            d_pct = (row_matches['direct'] / row_matches['total']) * 100
            i_pct = (row_matches['invert'] / row_matches['total']) * 100
            print(f"Row {y:2d}: direct={d_pct:5.1f}%, invert={i_pct:5.1f}%")


def check_column_xor_pattern(source, masked):
    """Check if there's an XOR pattern based on x position within the full image."""
    height, width = masked.shape[:2]
    src_height, src_width = source.shape[:2]
    
    print("\n--- Checking if absolute x position affects transformation ---")
    
    # Check at different x positions
    for test_x in range(0, width, 8):
        matches = {'direct': 0, 'invert': 0, 'total': 0}
        
        for y in range(height):
            mp = tuple(masked[y, test_x])
            if is_magenta(mp):
                continue
            
            sp = tuple(source[y % src_height, test_x % src_width])
            matches['total'] += 1
            
            if mp == sp:
                matches['direct'] += 1
            elif mp == (255 - sp[0], 255 - sp[1], 255 - sp[2]):
                matches['invert'] += 1
        
        if matches['total'] > 0:
            d_pct = (matches['direct'] / matches['total']) * 100
            print(f"x={test_x:3d}: direct={d_pct:5.1f}%, total_visible={matches['total']}")


def main():
    source, masked = load_images()
    
    analyze_tile_relationship(source, masked)
    analyze_pixel_patterns(source, masked)
    check_row_xor_pattern(source, masked)
    check_column_xor_pattern(source, masked)


if __name__ == "__main__":
    main()
