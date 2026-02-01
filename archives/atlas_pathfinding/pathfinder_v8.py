#!/usr/bin/env python3
"""
Atlas Pathfinding Solution - Version 8
Uses 4-directional movement (cardinal only) to match reference path pattern.
Creates angular paths with horizontal/vertical segments.
"""

import heapq
import math
from PIL import Image, ImageDraw
import numpy as np
import sys

SAND = 'SAND'
MOUNTAIN = 'MOUNTAIN'
RAMP = 'RAMP'
ABYSS = 'ABYSS'
START = 'START'
END = 'END'

PATH_COLOR = (0, 0, 255)  # Blue


def classify_pixel(r, g, b):
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


def can_move(from_t, to_t):
    if from_t == ABYSS or to_t == ABYSS:
        return False
    
    if from_t == START: from_t = SAND
    if from_t == END: from_t = SAND
    if to_t == START: to_t = SAND
    if to_t == END: to_t = SAND
    
    if from_t == to_t:
        return True
    if from_t == RAMP or to_t == RAMP:
        return True
    return False


def load_image(image_path):
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


def neighbors_cardinal(x, y, width, height, step=8):
    """4-directional movement only (up, down, left, right)."""
    for dx, dy in [(-step, 0), (step, 0), (0, -step), (0, step)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < width and 0 <= ny < height:
            yield nx, ny


def check_line_valid(terrain_map, x1, y1, x2, y2):
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


def astar_cardinal(terrain_map, start, goal, step=8):
    """A* with 4-directional movement for angular paths."""
    height, width = terrain_map.shape
    
    def h(pos):
        # Manhattan distance heuristic for cardinal movement
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
    
    open_set = [(h(start), 0, start)]
    came_from = {}
    g_score = {start: 0}
    closed = set()
    counter = 0
    
    while open_set:
        _, _, current = heapq.heappop(open_set)
        
        if current in closed:
            continue
        
        # Check if close to goal
        if abs(current[0] - goal[0]) < step * 2 and abs(current[1] - goal[1]) < step * 2:
            path = [goal, current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            print(f"Path found: {len(path)} waypoints")
            return path[::-1]
        
        closed.add(current)
        
        for nx, ny in neighbors_cardinal(current[0], current[1], width, height, step):
            if (nx, ny) in closed:
                continue
            
            if not check_line_valid(terrain_map, current[0], current[1], nx, ny):
                continue
            
            # Cost is just the step distance
            move_cost = step
            tentative_g = g_score[current] + move_cost
            
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


def smooth_path_cardinal(path, terrain_map):
    """Aggressively smooth path to create minimal waypoints with long segments."""
    if len(path) <= 2:
        return path
    
    height, width = terrain_map.shape
    
    # Convert path to a simpler representation
    result = [path[0]]
    i = 0
    
    while i < len(path) - 1:
        current = result[-1]
        
        # Try to find the furthest reachable point with a horizontal line
        best_horiz = None
        best_horiz_j = -1
        for j in range(len(path) - 1, i, -1):
            target = path[j]
            # Create horizontal line at current Y
            test_point = (target[0], current[1])
            if 0 <= test_point[0] < width:
                # Check if horizontal line to test_point is valid
                if check_line_valid(terrain_map, current[0], current[1], test_point[0], test_point[1]):
                    # Check if vertical line from test_point to target is valid
                    if check_line_valid(terrain_map, test_point[0], test_point[1], target[0], target[1]):
                        best_horiz = test_point
                        best_horiz_j = j
                        break
        
        # Try to find the furthest reachable point with a vertical line
        best_vert = None
        best_vert_j = -1
        for j in range(len(path) - 1, i, -1):
            target = path[j]
            # Create vertical line at current X
            test_point = (current[0], target[1])
            if 0 <= test_point[1] < height:
                # Check if vertical line to test_point is valid
                if check_line_valid(terrain_map, current[0], current[1], test_point[0], test_point[1]):
                    # Check if horizontal line from test_point to target is valid
                    if check_line_valid(terrain_map, test_point[0], test_point[1], target[0], target[1]):
                        best_vert = test_point
                        best_vert_j = j
                        break
        
        # Choose the option that reaches further
        if best_horiz_j > best_vert_j and best_horiz is not None:
            result.append(best_horiz)
            i = best_horiz_j
        elif best_vert is not None:
            result.append(best_vert)
            i = best_vert_j
        else:
            # Fallback: just move to next point
            i += 1
            if i < len(path):
                result.append(path[i])
        
        # Add the target point if we've reached a good intermediate
        if i < len(path) - 1 and len(result) > 1:
            # Check if we can reach the final target directly
            target = path[-1]
            last = result[-1]
            if check_line_valid(terrain_map, last[0], last[1], target[0], target[1]):
                result.append(target)
                break
    
    # Add final point if not already there
    if result[-1] != path[-1]:
        result.append(path[-1])
    
    return result


def draw_path(image, path, color=PATH_COLOR, width=1):
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
    
    print("Running A* with cardinal movement...")
    path = astar_cardinal(terrain_map, start, end, step=8)
    
    if not path:
        print("No path found!")
        return
    
    # Smooth while keeping angular pattern
    path = smooth_path_cardinal(path, terrain_map)
    print(f"Smoothed: {len(path)} waypoints")
    
    # Trim to edges of S and E
    start_edge = None
    for i, (x, y) in enumerate(path):
        terrain = terrain_map[y, x]
        if terrain != START:
            if i > 0:
                px, py = path[i-1]
                dx, dy = x - px, y - py
                dist = max(abs(dx), abs(dy), 1)
                for t in range(dist):
                    ex = int(px + (dx * t / dist))
                    ey = int(py + (dy * t / dist))
                    if 0 <= ex < terrain_map.shape[1] and 0 <= ey < terrain_map.shape[0]:
                        if terrain_map[ey, ex] != START:
                            start_edge = (ex, ey)
                            break
            if start_edge is None:
                start_edge = (x, y)
            break
    
    end_edge = None
    for i in range(len(path) - 1, -1, -1):
        x, y = path[i]
        terrain = terrain_map[y, x]
        if terrain != END:
            if i < len(path) - 1:
                nx, ny = path[i+1]
                dx, dy = nx - x, ny - y
                dist = max(abs(dx), abs(dy), 1)
                for t in range(dist):
                    ex = int(x + (dx * t / dist))
                    ey = int(y + (dy * t / dist))
                    if 0 <= ex < terrain_map.shape[1] and 0 <= ey < terrain_map.shape[0]:
                        if terrain_map[ey, ex] == END:
                            end_edge = (int(x + (dx * (t-1) / dist)), int(y + (dy * (t-1) / dist)))
                            break
            if end_edge is None:
                end_edge = (x, y)
            break
    
    trimmed_path = []
    started = False
    for x, y in path:
        terrain = terrain_map[y, x]
        if not started:
            if terrain != START:
                if start_edge:
                    trimmed_path.append(start_edge)
                    started = True
                    if (x, y) != start_edge:
                        trimmed_path.append((x, y))
                else:
                    trimmed_path.append((x, y))
                    started = True
        elif terrain == END:
            if end_edge and end_edge not in trimmed_path:
                trimmed_path.append(end_edge)
            break
        else:
            trimmed_path.append((x, y))
    
    if len(trimmed_path) < 2:
        trimmed_path = path
    
    print(f"Final path: {len(trimmed_path)} waypoints")
    
    result = draw_path(img, trimmed_path)
    
    if not output_path:
        output_path = input_path.replace('.png', '_output.png')
    
    result.save(output_path)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pathfinder_v8.py <input> [output]")
        sys.exit(1)
    
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
