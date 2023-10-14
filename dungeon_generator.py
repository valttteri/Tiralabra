from ctypes import WinDLL, wintypes
import sys
import pygame
from prim import prims_algorithm
from bowyerwatson import bowyer_watson
import tools
import plotting
from classes.roomclass import generate_rooms
from classes.hallwayclass import generate_hallways, plot_hallways

#python -m coverage run -m unittest tests\\test_app.py
#python -m coverage run -m unittest discover tests
#python -m coverage report
#python -m coverage html

GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
LIGHTGRAY = (211, 211, 211)
GRAY = (128, 128, 128)

def dungeon_generator(NODE_COUNT: int, DISPLAY_WIDTH: int, DISPLAY_HEIGHT):
    pygame.init()
    display = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    pygame.display.set_caption("Welcome to the Dungeon")
    clock = pygame.time.Clock()

    """The following forces the pygame window on top"""
    pin_window()

    display.fill((0, 0, 0))

    """Create all essential components"""
    super_coordinates = [(-DISPLAY_WIDTH**2, -DISPLAY_HEIGHT**2), (DISPLAY_WIDTH**2, 0), (0, DISPLAY_HEIGHT**2)]
    coordinates = tools.generate_coordinates(NODE_COUNT, DISPLAY_WIDTH, DISPLAY_HEIGHT)

    if coordinates == 1:
        print("")
        print("Couldn't find a spot for each room")
        print("Reduce the amount of rooms or increase the display size")
        print("")
        return 1

    triangulation = bowyer_watson(coordinates, super_coordinates, display)
    edges = tools.unique_edges(triangulation)

    minimum_spanning_tree = prims_algorithm(triangulation)
    removed_edges = tools.find_removed_edges(minimum_spanning_tree, edges)
    all_edges = minimum_spanning_tree + removed_edges

    dungeon_graph = tools.create_graph(all_edges)
    rooms = generate_rooms(coordinates, display)

    if rooms == 1:
        print("")
        print("Couldn't find a spot for each room")
        print("Reduce the amount of rooms or increase the display size")
        print("")
        return 1

    hallways = generate_hallways(dungeon_graph, rooms, display)

    """Start by plotting the coordinates"""
    for node in coordinates:
        pygame.draw.circle(display, BLUE, node, 4)

    pygame.display.flip()
    pygame.time.wait(1000)

    """Plot Delaunay triangulation"""
    for triangle in triangulation:
        triangle.plot()

    pygame.display.flip()
    pygame.time.wait(1000)
    display.fill((0, 0, 0))

    """Plot the minimum spanning tree"""
    for node in coordinates:
        pygame.draw.circle(display, BLUE, node, 4)
    plotting.plot_mst(minimum_spanning_tree, display, GREEN)

    pygame.display.flip()
    pygame.time.wait(1000)

    """Plot the removed edges"""
    if len(removed_edges) != 0:
        for edge in removed_edges:
            pygame.draw.line(display, GREEN, edge[0], edge[1])

        pygame.display.flip()
        pygame.time.wait(1000)

    """Plot the rooms"""
    for room in rooms:
        room.plot()

    pygame.display.flip()
    pygame.time.wait(1000)
    display.fill((0, 0, 0))

    """Plot the hallways"""
    plot_hallways(display, hallways, rooms)

    while True:
        for action in pygame.event.get():
            if action.type == pygame.QUIT:
                sys.exit()
            if action.type == pygame.KEYDOWN:
                if action.key == pygame.K_1:
                    dungeon_generator(NODE_COUNT, DISPLAY_WIDTH, DISPLAY_HEIGHT)
                if action.key == pygame.K_2:
                    main()
                if action.key == pygame.K_3:
                    sys.exit()

        """Plot the hallways and then plot the rooms on top of them"""
        for room in rooms:
            room.plot()
        pygame.display.flip()
        clock.tick(10)

def pin_window():
    """Each time a pygame window opens, this function forces it on top of other windows"""
    window = pygame.display.get_wm_info()['window']
    user32 = WinDLL("user32")
    user32.SetWindowPos.restype = wintypes.HWND
    user32.SetWindowPos.argtypes = [
        wintypes.HWND,
        wintypes.HWND,
        wintypes.INT,
        wintypes.INT,
        wintypes.INT,
        wintypes.INT,
        wintypes.UINT
    ]
    user32.SetWindowPos(window, -1, 50, 50, 0, 0, 0x0001)