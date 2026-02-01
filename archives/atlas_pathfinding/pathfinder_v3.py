#!/usr/bin/env python3
"""
Atlas Pathfinding Solution - Version 3
Based on color analysis: dark brown is passable, only black is impassable.
"""

import heapq
import math
from PIL import Image, ImageDraw
import numpy as np
from collections import defaultdict
import sys

# Colors from analysis:
# RGB(149, 139, 96) - 47% - Light terrain (sand) - easy to walk
# RGB(97, 80, 0) - 32% - Dark terrain (mountain) - walkable but harder
# RGB(0, 0, 0) - 18% - Black (abyss) - IMPASSABLE
# RGB(116, 116, 116) - Gray markers - walkable
# RGB(255, 0, 0) - End marker
# RGB(0, 255, 41) - Start marker

PATH_COLOR = (255, 0, 255)  # Magenta


def get_pixel_cost(r, g, b):
    """Get movement cost for a pixel based on its color."""
    
    # Start/End markers - walkable
    if g > 200 and b < 100:  # Green (start)
        return 1
    if r > 200 and g < 100 and b < 100:  # Red (end)
        return 1
    
    # Gray markers - walkable
    if abs(r - g) < 25 and abs(g - b) < 25 and 90 < r < 150:
        return 2
    
    # Black (abyss) - IMPASSABLE
    if r < 25 and g < 25 and b < 25:
        return float('inf')
    
    # Calculate brightness - lighter is better
    brightness = (r + g + b) / 3
    
    # Light terrain (sand-like) - easy
    if brightness > 110:
        return 1
    
    # Dark terrain (mountain-like) - harder but passable
    if brightness > 30:
        return 3
    
    return float('inf')


def load_image(image_path):
    """Load image and create cost map."""
    img = Image.open(image_path).convert('RGB')
    pixels = np.array(img)
    height, width = pixels.shape[:2]
    
    cost_map = np.zeros((height, width), dtype=np.float32)
    start_points = []
    end_points = []
    
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[y, x]
            cost = get_pixel_cost(r, g, b)
            cost_map[y, x] = cost
            
            # Detect start (green)
            if g > 200 and r < 100 and b < 100:
                start_points.append((x, y))
            # Detect end (red)
            elif r > 200 and g < 100 and b < 100:
                end_points.append((x, y))
    
    # Find centers
    start = None
    end = None
    
    if start_points:
        start = (sum(p[0] for p in start_points) // len(start_points),
                 sum(p[1] for p in start_points) // len(start_points))
    
    if end_points:
        end = (sum(p[0] for p in end_points) // len(end_points),
               sum(p[1] for p in end_points) // len(end_points))
    
    print(f"Cost map stats: min={cost_map[cost_map < float('inf')].min():.1f}, "
          f"max={cost_map[cost_map < float('inf')].max():.1f}")
    passable = np.sum(cost_map < float('inf'))
    total = height * width
    print(f"Passable: {passable}/{total} ({100*passable/total:.1f}%)")
    
    return img, cost_map, start, end


def neighbors(x, y, width, height, step=6):
    """Get 8-directional neighbors."""
    for dx, dy in [(-step,0), (step,0), (0,-step), (0,step),
                   (-step,-step), (-step,step), (step,-step), (step,step)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < width and 0 <= ny < height:
            yield nx, ny


def line_cost(cost_map, x1, y1, x2, y2):
    """Get max cost along a line using Bresenham-like sampling."""
    height, width = cost_map.shape
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    steps = max(dx, dy, 1)
    
    max_cost = 0
    for i in range(steps + 1):
        t = i / steps
        x = int(x1 + t * (x2 - x1))
        y = int(y1 + t * (y2 - y1))
        if 0 <= x < width and 0 <= y < height:
            c = cost_map[y, x]
            if c == float('inf'):
                return float('inf')
            max_cost = max(max_cost, c)
    
    return max_cost


def astar(cost_map, start, goal, step=6):
    """A* pathfinding."""
    height, width = cost_map.shape
    
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
            print(f"Found path! Length: {len(path)}")
            return path[::-1]
        
        closed.add(current)
        
        for nx, ny in neighbors(current[0], current[1], width, height, step):
            if (nx, ny) in closed:
                continue
            
            lc = line_cost(cost_map, current[0], current[1], nx, ny)
            if lc == float('inf'):
                continue
            
            dist = math.sqrt((nx-current[0])**2 + (ny-current[1])**2)
            move_cost = dist * (1 + lc * 0.3)
            tentative_g = g_score[current] + move_cost
            
            if tentative_g < g_score.get((nx, ny), float('inf')):
                came_from[(nx, ny)] = current
                g_score[(nx, ny)] = tentative_g
                f = tentative_g + h((nx, ny))
                counter += 1
                heapq.heappush(open_set, (f, counter, (nx, ny)))
        
        if len(closed) % 10000 == 0:
            print(f"Explored {len(closed)} nodes...")
    
    print(f"No path found after exploring {len(closed)} nodes")
    return None


def draw_path(image, path, color=PATH_COLOR, width=10):
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
    
    img, cost_map, start, end = load_image(input_path)
    
    print(f"Start: {start}, End: {end}")
    
    if not start or not end:
        print("Error: Could not find start or end markers")
        return
    
    print("Running A*...")
    path = astar(cost_map, start, end, step=6)
    
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
        print("Usage: python pathfinder_v3.py <input> [output]")
        sys.exit(1)
    
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
