# imports
import math

# constants
PI = math.pi

# fuunctions
def area_circle(radius):
    return PI * radius * radius

# main loop
def main():
    r = 10
    print(f"Area of a circle with radius {r}", area_circle(r))

# script entry point
if __name__ == "__main__":
    main()