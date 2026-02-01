#!/usr/bin/env python3
"""
Atlas Pathfinding Solution - Version 4
Enforces that transitions between SAND and MOUNTAIN can ONLY happen via RAMPS.
RAMP color: (116, 116, 116) - gray markers
"""

import heapq
import math
from PIL import Image, ImageDraw
import numpy as np
from collections import defaultdict
import sys

# Terrain types
SAND = 'SAND'           # Light terrain (149, 139, 96)
MOUNTAIN = 'MOUNTAIN'   # Dark terrain (97, 80, 0)
RAMP = 'RAMP'           # Gray markers (116, 116, 116) - transition points
ABYSS = 'ABYSS'         # Black (0, 0, 0) - impassable
START = 'START'         # Green
END = 'END'             # Red

PATH_COLOR = (57, 47, 89)  # Dark purple


def classify_pixel(r, g, b):
    """Classify a pixel into terrain type."""
    
    # Start marker (bright green)
    if g > 200 and r < 100 and b < 100:
        return START
    
    # End marker (bright red)
    if r > 200 and g < 100 and b < 100:
        return END
    
    # Ramp - gray markers (116, 116, 116) - allow some tolerance
    if abs(r - g) < 20 and abs(g - b) < 20 and 100 <= r <= 140:
        return RAMP
    
    # Black (abyss) - impassable
    if r < 25 and g < 25 and b < 25:
        return ABYSS
    
    # Calculate brightness to distinguish sand vs mountain
    brightness = (int(r) + int(g) + int(b)) / 3
    
    # Sand (light terrain) - brightness > ~120
    if brightness > 110:
        return SAND
    
    # Mountain (dark terrain)
    if brightness > 25:
        return MOUNTAIN
    
    return ABYSS


def can_move(from_terrain, to_terrain):
    """
    Check if movement between terrain types is allowed.
    Rules:
    - SAND <-> SAND: allowed
    - MOUNTAIN <-> MOUNTAIN: allowed
    - SAND <-> RAMP: allowed
    - MOUNTAIN <-> RAMP: allowed
    - SAND <-> MOUNTAIN: NOT allowed (must go through RAMP)
    - Anything <-> ABYSS: NOT allowed
    """
    if from_terrain == ABYSS or to_terrain == ABYSS:
        return False
    
    # START and END are treated as SAND for movement purposes
    if from_terrain == START:
        from_terrain = SAND
    if from_terrain == END:
        from_terrain = SAND
    if to_terrain == START:
        to_terrain = SAND
    if to_terrain == END:
        to_terrain = SAND
    
    # Same terrain type - always allowed
    if from_terrain == to_terrain:
        return True
    
    # RAMP can connect to anything (except ABYSS)
    if from_terrain == RAMP or to_terrain == RAMP:
        return True
    
    # Direct SAND <-> MOUNTAIN is NOT allowed
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
    ramp_count = 0
    
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[y, x]
            terrain = classify_pixel(r, g, b)
            terrain_map[y, x] = terrain
            
            if terrain == START:
                start_points.append((x, y))
            elif terrain == END:
                end_points.append((x, y))
            elif terrain == RAMP:
                ramp_count += 1
    
    # Find centers
    start = None
    end = None
    
    if start_points:
        start = (sum(p[0] for p in start_points) // len(start_points),
                 sum(p[1] for p in start_points) // len(start_points))
    
    if end_points:
        end = (sum(p[0] for p in end_points) // len(end_points),
               sum(p[1] for p in end_points) // len(end_points))
    
    # Count terrain types
    unique, counts = np.unique(terrain_map, return_counts=True)
    print("Terrain distribution:")
    for t, c in zip(unique, counts):
        print(f"  {t}: {c} pixels ({100*c/(height*width):.1f}%)")
    
    print(f"\nFound {ramp_count} RAMP pixels")
    
    return img, terrain_map, start, end


def neighbors(x, y, width, height, step=4):
    """Get 8-directional neighbors with smaller step for precision."""
    for dx, dy in [(-step,0), (step,0), (0,-step), (0,step),
                   (-step,-step), (-step,step), (step,-step), (step,step)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < width and 0 <= ny < height:
            yield nx, ny


def check_line_valid(terrain_map, x1, y1, x2, y2):
    """
    Check if movement along a line is valid according to terrain rules.
    Returns (valid, cost) tuple.
    """
    height, width = terrain_map.shape
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    steps = max(dx, dy, 1)
    
    prev_terrain = terrain_map[y1, x1]
    total_cost = 0
    
    for i in range(steps + 1):
        t = i / steps
        x = int(x1 + t * (x2 - x1))
        y = int(y1 + t * (y2 - y1))
        
        if 0 <= x < width and 0 <= y < height:
            curr_terrain = terrain_map[y, x]
            
            # Check if this transition is allowed
            if not can_move(prev_terrain, curr_terrain):
                return False, float('inf')
            
            # Add cost based on terrain
            if curr_terrain == MOUNTAIN:
                total_cost += 2
            elif curr_terrain == RAMP:
                total_cost += 1.5
            else:
                total_cost += 1
            
            prev_terrain = curr_terrain
    
    return True, total_cost


def astar(terrain_map, start, goal, step=4):
    """A* pathfinding with terrain transition constraints."""
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
            # Reconstruct path
            path = [goal, current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            print(f"Found path! Length: {len(path)} waypoints")
            return path[::-1]
        
        closed.add(current)
        
        for nx, ny in neighbors(current[0], current[1], width, height, step):
            if (nx, ny) in closed:
                continue
            
            valid, line_cost = check_line_valid(terrain_map, 
                                                 current[0], current[1], 
                                                 nx, ny)
            if not valid:
                continue
            
            dist = math.sqrt((nx-current[0])**2 + (ny-current[1])**2)
            move_cost = dist + line_cost
            tentative_g = g_score[current] + move_cost
            
            if tentative_g < g_score.get((nx, ny), float('inf')):
                came_from[(nx, ny)] = current
                g_score[(nx, ny)] = tentative_g
                f = tentative_g + h((nx, ny))
                counter += 1
                heapq.heappush(open_set, (f, counter, (nx, ny)))
        
        if len(closed) % 20000 == 0:
            print(f"Explored {len(closed)} nodes, open set: {len(open_set)}")
    
    print(f"No path found after exploring {len(closed)} nodes")
    return None


def draw_path(image, path, color=PATH_COLOR, width=1):
    """Draw path on image."""
    img = image.copy()
    draw = ImageDraw.Draw(img)
    
    for i in range(len(path) - 1):
        draw.line([path[i], path[i+1]], fill=color, width=width)
    
    for p in path:
        r = width // 2 + 2
        draw.ellipse([p[0]-r, p[1]-r, p[0]+r, p[1]+r], fill=color)
    
    return img


def main(input_path, output_path=None):
    print(f"Loading: {input_path}")
    
    img, terrain_map, start, end = load_image(input_path)
    
    print(f"\nStart: {start}, End: {end}")
    
    if not start or not end:
        print("Error: Could not find start or end markers")
        return
    
    print("\nRunning A* with elevation constraints...")
    print("(Sand <-> Mountain transitions only allowed via RAMP)")
    path = astar(terrain_map, start, end, step=4)
    
    if not path:
        print("No path found!")
        return
    
    result = draw_path(img, path)
    
    if not output_path:
        output_path = input_path.replace('.png', '_output.png')
    
    result.save(output_path)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pathfinder_v4.py <input> [output]")
        sys.exit(1)
    
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
