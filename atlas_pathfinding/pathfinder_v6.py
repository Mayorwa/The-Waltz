#!/usr/bin/env python3
"""
Atlas Pathfinding Solution - Version 6
Optimized to find shortest path, preferring direct routes.
Uses ramp constraints: Sand <-> Mountain only via RAMP.
"""

import heapq
import math
from PIL import Image, ImageDraw
import numpy as np
from collections import defaultdict
import sys

# Terrain types
SAND = 'SAND'
MOUNTAIN = 'MOUNTAIN'
RAMP = 'RAMP'
ABYSS = 'ABYSS'
START = 'START'
END = 'END'

PATH_COLOR = (57, 47, 89)


def classify_pixel(r, g, b):
    """Classify a pixel into terrain type."""
    
    if g > 200 and r < 100 and b < 100:
        return START
    
    if r > 200 and g < 100 and b < 100:
        return END
    
    if abs(r - g) < 20 and abs(g - b) < 20 and 100 <= r <= 140:
        return RAMP
    
    if r < 25 and g < 25 and b < 25:
        return ABYSS
    
    brightness = (int(r) + int(g) + int(b)) / 3
    
    if brightness > 110:
        return SAND
    
    if brightness > 25:
        return MOUNTAIN
    
    return ABYSS


def can_move(from_terrain, to_terrain):
    """Check if movement between terrain types is allowed."""
    if from_terrain == ABYSS or to_terrain == ABYSS:
        return False
    
    if from_terrain == START:
        from_terrain = SAND
    if from_terrain == END:
        from_terrain = SAND
    if to_terrain == START:
        to_terrain = SAND
    if to_terrain == END:
        to_terrain = SAND
    
    if from_terrain == to_terrain:
        return True
    
    if from_terrain == RAMP or to_terrain == RAMP:
        return True
    
    if (from_terrain == SAND and to_terrain == MOUNTAIN) or \
       (from_terrain == MOUNTAIN and to_terrain == SAND):
        return False
    
    return True


def load_image(image_path):
    """Load image and create terrain map."""
    img = Image.open(image_path).convert('RGB')
    pixels = np.array(img)
    height, width = pixels.shape[:2]
    
    terrain_map = np.empty((height, width), dtype=object)
    start_points = []
    end_points = []
    
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[y, x]
            terrain = classify_pixel(r, g, b)
            terrain_map[y, x] = terrain
            
            if terrain == START:
                start_points.append((x, y))
            elif terrain == END:
                end_points.append((x, y))
    
    start = None
    end = None
    
    if start_points:
        start = (sum(p[0] for p in start_points) // len(start_points),
                 sum(p[1] for p in start_points) // len(start_points))
    
    if end_points:
        end = (sum(p[0] for p in end_points) // len(end_points),
               sum(p[1] for p in end_points) // len(end_points))
    
    return img, terrain_map, start, end


def neighbors(x, y, width, height, step=5):
    """Get 8-directional neighbors."""
    for dx, dy in [(-step,0), (step,0), (0,-step), (0,step),
                   (-step,-step), (-step,step), (step,-step), (step,step)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < width and 0 <= ny < height:
            yield nx, ny


def check_line_valid(terrain_map, x1, y1, x2, y2):
    """Check if movement along a line is valid."""
    height, width = terrain_map.shape
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    steps = max(dx, dy, 1)
    
    prev_terrain = terrain_map[y1, x1]
    
    for i in range(steps + 1):
        t = i / steps
        x = int(x1 + t * (x2 - x1))
        y = int(y1 + t * (y2 - y1))
        
        if 0 <= x < width and 0 <= y < height:
            curr_terrain = terrain_map[y, x]
            
            if not can_move(prev_terrain, curr_terrain):
                return False
            
            prev_terrain = curr_terrain
    
    return True


def astar(terrain_map, start, goal, step=5):
    """
    A* with pure Euclidean distance - finds shortest valid path.
    """
    height, width = terrain_map.shape
    
    def h(pos):
        return math.sqrt((pos[0]-goal[0])**2 + (pos[1]-goal[1])**2)
    
    open_set = [(h(start), 0, start)]
    came_from = {}
    g_score = {start: 0}
    closed = set()
    counter = 0
    
    while open_set:
        _, _, current = heapq.heappop(open_set)
        
        if current in closed:
            continue
        
        if h(current) < step * 2:
            path = [goal, current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            print(f"Path found: {len(path)} waypoints")
            return path[::-1]
        
        closed.add(current)
        
        for nx, ny in neighbors(current[0], current[1], width, height, step):
            if (nx, ny) in closed:
                continue
            
            if not check_line_valid(terrain_map, current[0], current[1], nx, ny):
                continue
            
            # Pure distance cost - no terrain preference
            dist = math.sqrt((nx-current[0])**2 + (ny-current[1])**2)
            tentative_g = g_score[current] + dist
            
            if tentative_g < g_score.get((nx, ny), float('inf')):
                came_from[(nx, ny)] = current
                g_score[(nx, ny)] = tentative_g
                f = tentative_g + h((nx, ny))
                counter += 1
                heapq.heappush(open_set, (f, counter, (nx, ny)))
        
        if len(closed) % 20000 == 0:
            print(f"Explored {len(closed)} nodes...")
    
    print(f"No path found")
    return None


def smooth_path(path, terrain_map):
    """Remove unnecessary waypoints."""
    if len(path) <= 2:
        return path
    
    smoothed = [path[0]]
    i = 0
    
    while i < len(path) - 1:
        j = len(path) - 1
        while j > i + 1:
            if check_line_valid(terrain_map, path[i][0], path[i][1],
                               path[j][0], path[j][1]):
                break
            j -= 1
        
        smoothed.append(path[j])
        i = j
    
    return smoothed


def draw_path(image, path, color=PATH_COLOR, width=1):
    """Draw path on image."""
    img = image.copy()
    draw = ImageDraw.Draw(img)
    
    for i in range(len(path) - 1):
        draw.line([path[i], path[i+1]], fill=color, width=width)
    
    return img


def main(input_path, output_path=None):
    print(f"Loading: {input_path}")
    
    img, terrain_map, start, end = load_image(input_path)
    
    print(f"Start: {start}, End: {end}")
    
    if not start or not end:
        print("Error: Could not find start or end markers")
        return
    
    print("Running A* (shortest path)...")
    path = astar(terrain_map, start, end, step=5)
    
    if not path:
        print("No path found!")
        return
    
    path = smooth_path(path, terrain_map)
    print(f"Smoothed: {len(path)} waypoints")
    
    # Print waypoints for debugging
    print("\nPath waypoints:")
    for i, (x, y) in enumerate(path):
        terrain = terrain_map[y, x]
        print(f"  {i+1}: ({x}, {y}) - {terrain}")
    
    result = draw_path(img, path)
    
    if not output_path:
        output_path = input_path.replace('.png', '_output.png')
    
    result.save(output_path)
    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pathfinder_v6.py <input> [output]")
        sys.exit(1)
    
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
