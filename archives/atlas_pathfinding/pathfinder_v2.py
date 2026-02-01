#!/usr/bin/env python3
"""
Atlas Pathfinding Solution - Version 2
Finds a path from S (start) to E (end) on a terrain map using A* algorithm.
Updated with correct color values from image analysis.
"""

import heapq
import math
from PIL import Image, ImageDraw
import numpy as np
from collections import defaultdict
import sys

# Actual terrain colors from image analysis (RGB)
SAND_COLOR = (149, 139, 96)      # Walkable - 47%
MOUNTAIN_COLOR = (97, 80, 0)     # Dark brown - obstacles - 32%
ABYSS_COLOR = (0, 0, 0)          # Black - impassable - 18%
GRAY_MARKER = (116, 116, 116)    # Gray markers - 1%
END_COLOR = (255, 0, 0)          # Red "E" - 0.87%
START_COLOR = (0, 255, 41)       # Green "S" - 0.77%

# Path drawing color (magenta/pink)
PATH_COLOR = (255, 0, 255)


def color_distance(c1, c2):
    """Calculate Euclidean distance between two RGB colors."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))


def classify_pixel(rgb):
    """Classify a pixel based on its RGB color."""
    r, g, b = rgb[:3]  # Handle RGBA
    
    # Check for start marker (bright green)
    if g > 200 and b < 100:
        return 'START', 1
    
    # Check for end marker (bright red)
    if r > 200 and g < 100 and b < 100:
        return 'END', 1
    
    # Check for gray markers (passable but higher cost)
    if abs(r - g) < 20 and abs(g - b) < 20 and 100 < r < 140:
        return 'GRAY', 3
    
    # Check for abyss (black) - impassable
    if r < 30 and g < 30 and b < 30:
        return 'ABYSS', float('inf')
    
    # Check for sand/walkable terrain (light olive/tan color)
    sand_dist = color_distance((r, g, b), SAND_COLOR)
    if sand_dist < 40:
        return 'SAND', 1
    
    # Check for mountain (dark brown/olive) - impassable or very high cost
    mountain_dist = color_distance((r, g, b), MOUNTAIN_COLOR)
    if mountain_dist < 40:
        return 'MOUNTAIN', float('inf')
    
    # Default: check if color is lighter (more walkable)
    brightness = (r + g + b) / 3
    if brightness > 100:
        return 'UNKNOWN_WALKABLE', 2
    else:
        return 'UNKNOWN_OBSTACLE', float('inf')


def load_and_classify_image(image_path):
    """Load image and create terrain classification map with costs."""
    img = Image.open(image_path).convert('RGB')
    pixels = np.array(img)
    height, width = pixels.shape[:2]
    
    cost_map = np.full((height, width), float('inf'))
    terrain_map = np.empty((height, width), dtype=object)
    start_points = []
    end_points = []
    
    for y in range(height):
        for x in range(width):
            rgb = tuple(pixels[y, x])
            terrain, cost = classify_pixel(rgb)
            terrain_map[y, x] = terrain
            cost_map[y, x] = cost
            
            if terrain == 'START':
                start_points.append((x, y))
            elif terrain == 'END':
                end_points.append((x, y))
    
    # Calculate center of start and end markers
    start_center = None
    end_center = None
    
    if start_points:
        avg_x = sum(p[0] for p in start_points) // len(start_points)
        avg_y = sum(p[1] for p in start_points) // len(start_points)
        start_center = (avg_x, avg_y)
    
    if end_points:
        avg_x = sum(p[0] for p in end_points) // len(end_points)
        avg_y = sum(p[1] for p in end_points) // len(end_points)
        end_center = (avg_x, avg_y)
    
    return img, terrain_map, cost_map, start_center, end_center


def get_neighbors(x, y, width, height, step=8):
    """Get valid neighboring positions."""
    neighbors = []
    # 8-directional movement
    directions = [(-step, 0), (step, 0), (0, -step), (0, step),
                  (-step, -step), (-step, step), (step, -step), (step, step)]
    
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < width and 0 <= ny < height:
            neighbors.append((nx, ny))
    return neighbors


def heuristic(pos, goal):
    """A* heuristic: Euclidean distance."""
    return math.sqrt((pos[0] - goal[0])**2 + (pos[1] - goal[1])**2)


def get_path_cost(cost_map, x1, y1, x2, y2):
    """Get the cost of moving from (x1, y1) to (x2, y2), checking along the path."""
    height, width = cost_map.shape
    
    # Sample points along the line
    dist = max(abs(x2 - x1), abs(y2 - y1))
    if dist == 0:
        return cost_map[y2, x2]
    
    max_cost = 0
    samples = max(3, dist // 2)
    
    for i in range(samples + 1):
        t = i / samples
        sx = int(x1 + t * (x2 - x1))
        sy = int(y1 + t * (y2 - y1))
        
        if 0 <= sx < width and 0 <= sy < height:
            cost = cost_map[sy, sx]
            if cost == float('inf'):
                return float('inf')
            max_cost = max(max_cost, cost)
    
    return max_cost


def a_star_pathfind(cost_map, start, goal, step=8):
    """A* pathfinding algorithm with improved cost calculation."""
    height, width = cost_map.shape
    
    print(f"Pathfinding from {start} to {goal}")
    print(f"Map size: {width}x{height}")
    
    # Priority queue: (f_score, counter, position)
    counter = 0
    open_set = [(0, counter, start)]
    came_from = {}
    
    g_score = defaultdict(lambda: float('inf'))
    g_score[start] = 0
    
    f_score = defaultdict(lambda: float('inf'))
    f_score[start] = heuristic(start, goal)
    
    closed_set = set()
    iterations = 0
    max_iterations = 500000
    
    while open_set and iterations < max_iterations:
        iterations += 1
        _, _, current = heapq.heappop(open_set)
        
        if current in closed_set:
            continue
        
        # Check if we're close enough to goal
        dist_to_goal = heuristic(current, goal)
        if dist_to_goal < step * 2:
            print(f"Goal reached after {iterations} iterations")
            # Reconstruct path
            path = [current, goal]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return path[::-1]
        
        closed_set.add(current)
        
        for neighbor in get_neighbors(current[0], current[1], width, height, step):
            if neighbor in closed_set:
                continue
            
            path_cost = get_path_cost(cost_map, current[0], current[1], 
                                       neighbor[0], neighbor[1])
            if path_cost == float('inf'):
                continue
            
            move_dist = heuristic(current, neighbor)
            move_cost = move_dist * (1 + path_cost * 0.5)
            tentative_g = g_score[current] + move_cost
            
            if tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                counter += 1
                heapq.heappush(open_set, (f_score[neighbor], counter, neighbor))
    
    print(f"No path found after {iterations} iterations")
    print(f"Explored {len(closed_set)} nodes")
    return None


def smooth_path(path, cost_map, max_iterations=3):
    """Smooth the path by removing unnecessary waypoints."""
    if len(path) <= 2:
        return path
    
    for _ in range(max_iterations):
        new_path = [path[0]]
        i = 0
        
        while i < len(path) - 1:
            # Try to skip intermediate points
            j = len(path) - 1
            while j > i + 1:
                # Check if direct path is valid
                cost = get_path_cost(cost_map, path[i][0], path[i][1],
                                     path[j][0], path[j][1])
                if cost < float('inf'):
                    break
                j -= 1
            
            new_path.append(path[j])
            i = j
        
        if len(new_path) == len(path):
            break
        path = new_path
    
    return path


def draw_path(image, path, color=PATH_COLOR, width=10):
    """Draw the path on the image."""
    img_copy = image.copy()
    draw = ImageDraw.Draw(img_copy)
    
    # Draw path as connected lines
    for i in range(len(path) - 1):
        p1 = path[i]
        p2 = path[i + 1]
        draw.line([p1, p2], fill=color, width=width)
    
    # Draw circles at waypoints
    for point in path:
        x, y = point
        r = width // 2 + 2
        draw.ellipse([x-r, y-r, x+r, y+r], fill=color)
    
    return img_copy


def main(input_path, output_path=None):
    """Main function to run pathfinding."""
    print(f"Loading image: {input_path}")
    
    # Load and classify the image
    img, terrain_map, cost_map, start_center, end_center = load_and_classify_image(input_path)
    
    print(f"Start marker center: {start_center}")
    print(f"End marker center: {end_center}")
    
    if start_center is None:
        print("Error: Could not find start position (S)")
        return None
    
    if end_center is None:
        print("Error: Could not find end position (E)")
        return None
    
    # Find path using A*
    print("Finding path using A* algorithm...")
    path = a_star_pathfind(cost_map, start_center, end_center, step=8)
    
    if path is None:
        print("No path found!")
        return None
    
    print(f"Raw path has {len(path)} waypoints")
    
    # Smooth the path
    path = smooth_path(path, cost_map)
    print(f"Smoothed path has {len(path)} waypoints")
    
    # Draw path on image
    result_img = draw_path(img, path)
    
    # Save output
    if output_path is None:
        output_path = input_path.replace('.png', '_output.png')
    
    result_img.save(output_path)
    print(f"Output saved to: {output_path}")
    
    return path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pathfinder_v2.py <input_image> [output_image]")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    main(input_path, output_path)
