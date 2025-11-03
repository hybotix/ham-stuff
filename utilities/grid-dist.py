#!/usr/bin/env python3
import math

print()
print("Grid distance calculator")
print()

#
#   Put your grid here
#
my_grid = "DM12JT"

import sys

my_grid = sys.argv[1].upper()
their_grid = sys.argv[2].upper()

def km_to_miles(km):
    return km * 0.621371

def grid_to_latlon(grid):
    """Convert 4-char Maidenhead to center lat/lon"""
    grid = grid.upper()
    lon = (ord(grid[0]) - ord('A')) * 20 - 180 + 10
    lat = (ord(grid[1]) - ord('A')) * 10 - 90 + 5
    lon += (int(grid[2])) * 2 + 1
    lat += (int(grid[3])) * 1 + 0.5
    return lat, lon

def grid_distance(grid1, grid2):
    """Calculate distance between two grid squares in km"""
    lat1, lon1 = grid_to_latlon(grid1)
    lat2, lon2 = grid_to_latlon(grid2)

    # Haversine formula
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

print(f"My Grid: {my_grid}")
print(f"Their Grid: {their_grid}")

distance_km = int(grid_distance(my_grid, their_grid))
distance_miles = int(km_to_miles(distance_km))

print()
print(f"It is {distance_miles} miles ({distance_km} Km) from grid {my_grid} to grid {their_grid}")
