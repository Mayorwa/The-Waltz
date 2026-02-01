#!/usr/bin/env python3
"""
Pattern Analyzer - Analyzes the pattern in images and generates output.
"""

from PIL import Image
import numpy as np
from collections import Counter

def analyze_image(image_path):
    """Analyze an image and return statistics about it."""
    img = Image.open(image_path).convert('RGB')
    pixels = np.array(img)
    
    print(f"Image: {image_path}")
    print(f"Size: {img.size} (width x height)")
    print(f"Shape: {pixels.shape}")
    
    # Count unique colors
    flat_pixels = pixels.reshape(-1, 3)
    color_tuples = [tuple(p) for p in flat_pixels]
    color_counts = Counter(color_tuples)
    
    print(f"\nTop 20 colors:")
    for color, count in color_counts.most_common(20):
        pct = (count / len(color_tuples)) * 100
        print(f"  RGB{color}: {count:,} pixels ({pct:.2f}%)")
    
    return img, pixels, color_counts


def find_magenta_mask(pixels):
    """Find pixels that are magenta (the mask color)."""
    # Magenta is typically (255, 0, 255) or close
    r, g, b = pixels[:,:,0], pixels[:,:,1], pixels[:,:,2]
    
    # Check for magenta-like colors (high R, low G, high B)
    magenta_mask = (r > 200) & (g < 100) & (b > 200)
    
    return magenta_mask


def analyze_pattern(pixels, mask=None):
    """Analyze repeating pattern in the image."""
    if mask is not None:
        # Only analyze non-masked pixels
        valid_pixels = pixels[~mask]
    else:
        valid_pixels = pixels.reshape(-1, 3)
    
    color_tuples = [tuple(p) for p in valid_pixels]
    color_counts = Counter(color_tuples)
    
    print("\nNon-masked pixel analysis:")
    for color, count in color_counts.most_common(10):
        print(f"  RGB{color}: {count:,} pixels")
    
    return color_counts


def find_horizontal_pattern(pixels, mask=None):
    """Detect horizontal repeating pattern period."""
    height, width = pixels.shape[:2]
    
    # Check for pattern repetition by comparing columns
    # Look at first non-masked row
    for row in range(height):
        if mask is not None and np.any(~mask[row]):
            sample_row = pixels[row]
            valid_cols = ~mask[row] if mask is not None else np.ones(width, dtype=bool)
            
            # Find potential periods
            for period in range(1, width // 2):
                matches = 0
                total = 0
                for col in range(width - period):
                    if valid_cols[col] and valid_cols[col + period]:
                        if np.array_equal(sample_row[col], sample_row[col + period]):
                            matches += 1
                        total += 1
                
                if total > 0 and matches / total > 0.95:
                    print(f"Potential horizontal period: {period} (row {row}, {matches}/{total} matches)")
                    return period
            break
    
    return None


def find_vertical_pattern(pixels, mask=None):
    """Detect vertical repeating pattern period."""
    height, width = pixels.shape[:2]
    
    # Check first column
    for col in range(width):
        if mask is not None and np.any(~mask[:, col]):
            sample_col = pixels[:, col]
            valid_rows = ~mask[:, col] if mask is not None else np.ones(height, dtype=bool)
            
            for period in range(1, height // 2):
                matches = 0
                total = 0
                for row in range(height - period):
                    if valid_rows[row] and valid_rows[row + period]:
                        if np.array_equal(sample_col[row], sample_col[row + period]):
                            matches += 1
                        total += 1
                
                if total > 0 and matches / total > 0.95:
                    print(f"Potential vertical period: {period} (col {col}, {matches}/{total} matches)")
                    return period
            break
    
    return None


def generate_output(unmasked_img, masked_img, output_path):
    """Generate output by repeating the pattern."""
    unmasked = np.array(unmasked_img.convert('RGB'))
    masked = np.array(masked_img.convert('RGB'))
    
    target_height, target_width = masked.shape[:2]
    src_height, src_width = unmasked.shape[:2]
    
    print(f"\nSource size: {src_width}x{src_height}")
    print(f"Target size: {target_width}x{target_height}")
    
    # Find the magenta mask
    magenta_mask = find_magenta_mask(masked)
    masked_count = np.sum(magenta_mask)
    print(f"Magenta masked pixels: {masked_count:,}")
    
    # Analyze pattern in unmasked areas
    analyze_pattern(masked, magenta_mask)
    
    # Try to detect repeating pattern
    h_period = find_horizontal_pattern(masked, magenta_mask)
    v_period = find_vertical_pattern(masked, magenta_mask)
    
    # Create output by tiling the source pattern
    output = np.zeros((target_height, target_width, 3), dtype=np.uint8)
    
    for y in range(target_height):
        for x in range(target_width):
            # Map to source coordinates
            src_y = y % src_height
            src_x = x % src_width
            output[y, x] = unmasked[src_y, src_x]
    
    result = Image.fromarray(output)
    result.save(output_path)
    print(f"\nSaved output: {output_path}")
    
    return result


def main():
    # Paths to uploaded images
    unmasked_path = "/Users/mayorwa/.gemini/antigravity/brain/b41034ca-7388-4475-ab91-f7cf69e2eae9/uploaded_image_0_1768776289553.png"
    masked_path = "/Users/mayorwa/.gemini/antigravity/brain/b41034ca-7388-4475-ab91-f7cf69e2eae9/uploaded_image_1_1768776289553.png"
    output_path = "/Users/mayorwa/Documents/Personal/The-Waltz/atlas_pathfinding/pattern_output.png"
    
    print("=" * 60)
    print("ANALYZING UNMASKED IMAGE")
    print("=" * 60)
    unmasked_img, unmasked_pixels, _ = analyze_image(unmasked_path)
    
    print("\n" + "=" * 60)
    print("ANALYZING MASKED IMAGE")
    print("=" * 60)
    masked_img, masked_pixels, _ = analyze_image(masked_path)
    
    print("\n" + "=" * 60)
    print("GENERATING OUTPUT")
    print("=" * 60)
    generate_output(unmasked_img, masked_img, output_path)


if __name__ == "__main__":
    main()
