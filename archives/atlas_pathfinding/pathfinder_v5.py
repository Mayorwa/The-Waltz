#!/usr/bin/env python3
"""
Atlas Pathfinding Solution - Version 5
Adjusted to prefer more direct/diagonal paths through terrain centers.
Uses ramp constraints: Sand <-> Mountain only via RAMP.
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
    Sand <-> Mountain requires RAMP.
    """
    if from_terrain == ABYSS or to_terrain == ABYSS:
        return False
    
    # START and END are treated as SAND
    if from_terrain == START:
        from_terrain = SAND
    if from_terrain == END:
        from_terrain = SAND
    if to_terrain == START:
        to_terrain = SAND
    if to_terrain == END:
        to_terrain = SAND
    
    # Same terrain - allowed
    if from_terrain == to_terrain:
        return True
    
    # RAMP connects to anything
    if from_terrain == RAMP or to_terrain == RAMP:
        return True
    
    # Direct SAND <-> MOUNTAIN not allowed
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
    ramp_positions = []
    
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
                ramp_positions.append((x, y))
    
    # Find centers
    start = None
    end = None
    
    if start_points:
        start = (sum(p[0] for p in start_points) // len(start_points),
                 sum(p[1] for p in start_points) // len(start_points))
    
    if end_points:
        end = (sum(p[0] for p in end_points) // len(end_points),
               sum(p[1] for p in end_points) // len(end_points))
    
    # Cluster ramps to find their centers
    ramp_clusters = cluster_ramps(ramp_positions)
    print(f"Found {len(ramp_clusters)} ramp clusters")
    for i, (cx, cy) in enumerate(ramp_clusters):
        print(f"  Ramp {i+1}: ({cx}, {cy})")
    
    return img, terrain_map, start, end, ramp_clusters


def cluster_ramps(positions, threshold=50):
    """Cluster ramp positions to find distinct ramp centers."""
    if not positions:
        return []
    
    clusters = []
    used = set()
    
    for px, py in positions:
        if (px, py) in used:
            continue
        
        # Find all nearby ramp pixels
        cluster = [(px, py)]
        used.add((px, py))
        
        for qx, qy in positions:
            if (qx, qy) in used:
                continue
            if abs(qx - px) < threshold and abs(qy - py) < threshold:
                cluster.append((qx, qy))
                used.add((qx, qy))
        
        # Calculate cluster center
        cx = sum(p[0] for p in cluster) // len(cluster)
        cy = sum(p[1] for p in cluster) // len(cluster)
        clusters.append((cx, cy))
    
    return clusters


def neighbors(x, y, width, height, step=6):
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
    total_cost = 0
    
    for i in range(steps + 1):
        t = i / steps
        x = int(x1 + t * (x2 - x1))
        y = int(y1 + t * (y2 - y1))
        
        if 0 <= x < width and 0 <= y < height:
            curr_terrain = terrain_map[y, x]
            
            if not can_move(prev_terrain, curr_terrain):
                return False, float('inf')
            
            # Cost based on terrain - prefer SAND, then RAMP, then MOUNTAIN
            if curr_terrain == MOUNTAIN:
                total_cost += 1.5
            elif curr_terrain == RAMP:
                total_cost += 0.5  # Prefer using ramps
            else:
                total_cost += 1
            
            prev_terrain = curr_terrain
    
    return True, total_cost


def astar_via_ramps(terrain_map, start, goal, ramp_clusters, step=6):
    """
    A* that prefers going through ramp clusters when transitioning elevations.
    This produces more natural-looking paths.
    """
    height, width = terrain_map.shape
    
    def h(pos):
        # Euclidean distance heuristic
        return math.sqrt((pos[0]-goal[0])**2 + (pos[1]-goal[1])**2)
    
    def ramp_bonus(pos):
        # Give slight preference to positions near ramps
        min_dist = float('inf')
        for rx, ry in ramp_clusters:
            d = math.sqrt((pos[0]-rx)**2 + (pos[1]-ry)**2)
            min_dist = min(min_dist, d)
        # Bonus for being near a ramp (reduces effective cost)
        if min_dist < 30:
            return -0.5
        return 0
    
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
            move_cost = dist + line_cost + ramp_bonus((nx, ny))
            tentative_g = g_score[current] + move_cost
            
            if tentative_g < g_score.get((nx, ny), float('inf')):
                came_from[(nx, ny)] = current
                g_score[(nx, ny)] = tentative_g
                f = tentative_g + h((nx, ny))
                counter += 1
                heapq.heappush(open_set, (f, counter, (nx, ny)))
        
        if len(closed) % 20000 == 0:
            print(f"Explored {len(closed)} nodes...")
    
    print(f"No path found after exploring {len(closed)} nodes")
    return None


def smooth_path(path, terrain_map):
    """Remove unnecessary waypoints while maintaining validity."""
    if len(path) <= 2:
        return path
    
    smoothed = [path[0]]
    i = 0
    
    while i < len(path) - 1:
        # Try to skip ahead as far as possible
        j = len(path) - 1
        while j > i + 1:
            valid, _ = check_line_valid(terrain_map, 
                                        path[i][0], path[i][1],
                                        path[j][0], path[j][1])
            if valid:
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
    
    # Small dots at waypoints
    for p in path:
        r = max(1, width)
        draw.ellipse([p[0]-r, p[1]-r, p[0]+r, p[1]+r], fill=color)
    
    return img


def main(input_path, output_path=None):
    print(f"Loading: {input_path}")
    
    img, terrain_map, start, end, ramp_clusters = load_image(input_path)
    
    print(f"\nStart: {start}, End: {end}")
    
    if not start or not end:
        print("Error: Could not find start or end markers")
        return
    
    print("\nRunning A* with ramp-aware pathfinding...")
    path = astar_via_ramps(terrain_map, start, end, ramp_clusters, step=6)
    
    if not path:
        print("No path found!")
        return
    
    # Smooth the path
    print(f"Smoothing path from {len(path)} waypoints...")
    path = smooth_path(path, terrain_map)
    print(f"Final path: {len(path)} waypoints")
    
    result = draw_path(img, path)
    
    if not output_path:
        output_path = input_path.replace('.png', '_output.png')
    
    result.save(output_path)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pathfinder_v5.py <input> [output]")
        sys.exit(1)
    
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
