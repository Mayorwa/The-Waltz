#!/usr/bin/env python3
"""
Atlas Pathfinding Solution
Finds a path from S (start) to E (end) on a terrain map using A* algorithm.
"""

import heapq
import math
from PIL import Image
import numpy as np
from collections import defaultdict
import sys

# Terrain color definitions (RGB)
TERRAIN_COLORS = {
    'RAMP': (183, 156, 168),
    'SAND': (149, 106, 80),
    'MOUNTAIN': (97, 88, 0),
    'ABYSS': (0, 0, 0),
    'TIGHT': (0, 205, 43),
    'ROAD': (255, 0, 0),
    'WATER': (0, 0, 200),
}

# Special markers
START_COLOR = (0, 255, 0)  # Green "S"
END_COLOR = (255, 0, 0)    # Red "E"

# Path drawing color (magenta/pink)
PATH_COLOR = (255, 0, 255)

# Terrain costs (lower = easier to traverse)
# Impassable terrains have cost of infinity
TERRAIN_COSTS = {
    'RAMP': 2,
    'SAND': 1,      # Walkable
    'MOUNTAIN': float('inf'),  # Impassable
    'ABYSS': float('inf'),     # Impassable
    'TIGHT': 3,
    'ROAD': 0.5,    # Easy to walk
    'WATER': float('inf'),     # Impassable
    'UNKNOWN': 1,   # Default walkable
    'START': 1,
    'END': 1,
    'GRAY': 5,      # Gray markers - higher cost but passable
}


def color_distance(c1, c2):
    """Calculate Euclidean distance between two RGB colors."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))


def classify_pixel(rgb):
    """Classify a pixel based on its RGB color."""
    r, g, b = rgb[:3]  # Handle RGBA
    
    # Check for start marker (bright green)
    if g > 200 and r < 100 and b < 100:
        return 'START'
    
    # Check for end marker (bright red)
    if r > 200 and g < 100 and b < 100:
        return 'END'
    
    # Check for gray markers
    if abs(r - g) < 30 and abs(g - b) < 30 and 100 < r < 180:
        return 'GRAY'
    
    # Check for abyss (black)
    if r < 20 and g < 20 and b < 20:
        return 'ABYSS'
    
    # Find closest terrain color
    min_dist = float('inf')
    closest_terrain = 'UNKNOWN'
    
    for terrain, color in TERRAIN_COLORS.items():
        dist = color_distance((r, g, b), color)
        if dist < min_dist:
            min_dist = dist
            closest_terrain = terrain
    
    # If close enough, return the terrain type
    if min_dist < 50:
        return closest_terrain
    
    return 'UNKNOWN'


def load_and_classify_image(image_path):
    """Load image and create terrain classification map."""
    img = Image.open(image_path).convert('RGB')
    pixels = np.array(img)
    height, width = pixels.shape[:2]
    
    terrain_map = np.empty((height, width), dtype=object)
    start_pos = None
    end_pos = None
    
    for y in range(height):
        for x in range(width):
            rgb = tuple(pixels[y, x])
            terrain = classify_pixel(rgb)
            terrain_map[y, x] = terrain
            
            if terrain == 'START':
                if start_pos is None:
                    start_pos = (x, y)
            elif terrain == 'END':
                if end_pos is None:
                    end_pos = (x, y)
    
    return img, terrain_map, start_pos, end_pos


def find_marker_center(terrain_map, marker_type):
    """Find the center of a marker region."""
    height, width = terrain_map.shape
    points = []
    
    for y in range(height):
        for x in range(width):
            if terrain_map[y, x] == marker_type:
                points.append((x, y))
    
    if not points:
        return None
    
    avg_x = sum(p[0] for p in points) // len(points)
    avg_y = sum(p[1] for p in points) // len(points)
    return (avg_x, avg_y)


def get_neighbors(x, y, width, height, step=5):
    """Get valid neighboring positions with a larger step size for efficiency."""
    neighbors = []
    for dx in [-step, 0, step]:
        for dy in [-step, 0, step]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                neighbors.append((nx, ny))
    return neighbors


def heuristic(pos, goal):
    """A* heuristic: Euclidean distance."""
    return math.sqrt((pos[0] - goal[0])**2 + (pos[1] - goal[1])**2)


def get_terrain_cost(terrain_map, x, y, step=5):
    """Get the cost of moving through a region around (x, y)."""
    height, width = terrain_map.shape
    max_cost = 0
    
    # Check a small region to avoid obstacles
    for dx in range(-step//2, step//2 + 1):
        for dy in range(-step//2, step//2 + 1):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                terrain = terrain_map[ny, nx]
                cost = TERRAIN_COSTS.get(terrain, 1)
                if cost == float('inf'):
                    return float('inf')
                max_cost = max(max_cost, cost)
    
    return max_cost


def a_star_pathfind(terrain_map, start, goal, step=5):
    """A* pathfinding algorithm."""
    height, width = terrain_map.shape
    
    # Priority queue: (f_score, counter, position)
    counter = 0
    open_set = [(0, counter, start)]
    came_from = {}
    
    g_score = defaultdict(lambda: float('inf'))
    g_score[start] = 0
    
    f_score = defaultdict(lambda: float('inf'))
    f_score[start] = heuristic(start, goal)
    
    closed_set = set()
    
    while open_set:
        _, _, current = heapq.heappop(open_set)
        
        if current in closed_set:
            continue
        
        # Check if we're close enough to goal
        if heuristic(current, goal) < step * 2:
            # Reconstruct path
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return path[::-1]
        
        closed_set.add(current)
        
        for neighbor in get_neighbors(current[0], current[1], width, height, step):
            if neighbor in closed_set:
                continue
            
            terrain_cost = get_terrain_cost(terrain_map, neighbor[0], neighbor[1], step)
            if terrain_cost == float('inf'):
                continue
            
            move_cost = heuristic(current, neighbor) * terrain_cost
            tentative_g = g_score[current] + move_cost
            
            if tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                counter += 1
                heapq.heappush(open_set, (f_score[neighbor], counter, neighbor))
    
    return None  # No path found


def draw_path(image, path, color=PATH_COLOR, width=8):
    """Draw the path on the image."""
    from PIL import ImageDraw
    
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
        r = width // 2
        draw.ellipse([x-r, y-r, x+r, y+r], fill=color)
    
    return img_copy


def main(input_path, output_path=None):
    """Main function to run pathfinding."""
    print(f"Loading image: {input_path}")
    
    # Load and classify the image
    img, terrain_map, start_pos, end_pos = load_and_classify_image(input_path)
    
    # Find center of markers
    start_center = find_marker_center(terrain_map, 'START')
    end_center = find_marker_center(terrain_map, 'END')
    
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
    path = a_star_pathfind(terrain_map, start_center, end_center, step=10)
    
    if path is None:
        print("No path found!")
        return None
    
    print(f"Path found with {len(path)} waypoints")
    
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
        print("Usage: python pathfinder.py <input_image> [output_image]")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    main(input_path, output_path)
