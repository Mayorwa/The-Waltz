#!/usr/bin/env python3
"""
Verify the generated pattern matches the visible areas in the masked image.
"""

from PIL import Image
import numpy as np


def is_magenta(pixel):
    """Check if a pixel is magenta (mask color)."""
    r, g, b = pixel
    return r > 200 and g < 100 and b > 200


def compare_images(output_path, masked_path):
    """Compare output with visible areas of masked image."""
    output_img = Image.open(output_path).convert('RGB')
    masked_img = Image.open(masked_path).convert('RGB')
    
    output = np.array(output_img)
    masked = np.array(masked_img)
    
    height, width = masked.shape[:2]
    
    matches = 0
    mismatches = 0
    masked_count = 0
    mismatch_examples = []
    
    for y in range(height):
        for x in range(width):
            masked_pixel = tuple(masked[y, x])
            
            if is_magenta(masked_pixel):
                masked_count += 1
                continue
            
            output_pixel = tuple(output[y, x])
            
            if masked_pixel == output_pixel:
                matches += 1
            else:
                mismatches += 1
                if len(mismatch_examples) < 10:
                    mismatch_examples.append({
                        'pos': (x, y),
                        'expected': masked_pixel,
                        'got': output_pixel
                    })
    
    total_visible = matches + mismatches
    
    print(f"Results:")
    print(f"  Total pixels: {height * width:,}")
    print(f"  Masked (magenta): {masked_count:,}")
    print(f"  Visible pixels: {total_visible:,}")
    print(f"  Matches: {matches:,}")
    print(f"  Mismatches: {mismatches:,}")
    
    if total_visible > 0:
        accuracy = (matches / total_visible) * 100
        print(f"  Accuracy: {accuracy:.2f}%")
    
    if mismatch_examples:
        print(f"\nMismatch examples:")
        for ex in mismatch_examples:
            print(f"  At {ex['pos']}: expected RGB{ex['expected']}, got RGB{ex['got']}")
    
    return matches, mismatches


def create_diff_image(output_path, masked_path, diff_path):
    """Create an image showing differences."""
    output_img = Image.open(output_path).convert('RGB')
    masked_img = Image.open(masked_path).convert('RGB')
    
    output = np.array(output_img)
    masked = np.array(masked_img)
    
    height, width = masked.shape[:2]
    diff = np.zeros((height, width, 3), dtype=np.uint8)
    
    for y in range(height):
        for x in range(width):
            masked_pixel = tuple(masked[y, x])
            
            if is_magenta(masked_pixel):
                # Show our generated output in masked areas (cyan to indicate generated)
                diff[y, x] = output[y, x]
            else:
                output_pixel = tuple(output[y, x])
                if masked_pixel == output_pixel:
                    # Green for match
                    diff[y, x] = (0, 255, 0)
                else:
                    # Red for mismatch
                    diff[y, x] = (255, 0, 0)
    
    diff_img = Image.fromarray(diff)
    diff_img.save(diff_path)
    print(f"\nSaved diff image: {diff_path}")


def main():
    output_path = "/Users/mayorwa/Documents/Personal/The-Waltz/atlas_pathfinding/pattern_output.png"
    masked_path = "/Users/mayorwa/.gemini/antigravity/brain/b41034ca-7388-4475-ab91-f7cf69e2eae9/uploaded_image_1_1768776289553.png"
    diff_path = "/Users/mayorwa/Documents/Personal/The-Waltz/atlas_pathfinding/pattern_diff.png"
    
    compare_images(output_path, masked_path)
    create_diff_image(output_path, masked_path, diff_path)


if __name__ == "__main__":
    main()
