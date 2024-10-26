#! /usr/bin/python3

__author__ = "Pengxu Zheng"
__version__ = "v1.0"
__date__ = "17 March 2022"

import random
import sys
from random import randint

from gdpc import interface as INTF
from gdpc import worldLoader as WL

# Here we read start and end coordinates of our build area
STARTX, STARTY, STARTZ, ENDX, ENDY, ENDZ = INTF.requestBuildArea()  # BUILDAREA

# WORLDSLICE
# Using the start and end coordinates we are generating a world slice
# It contains all manner of information, including heightmaps and biomes
# For further information on what information it contains, see
#     https://minecraft.fandom.com/wiki/Chunk_format
#
# IMPORTANT: Keep in mind that a wold slice is a 'snapshot' of the world,
#   and any changes you make later on will not be reflected in the world slice
WORLDSLICE = WL.WorldSlice(STARTX, STARTZ,
                           ENDX + 1, ENDZ + 1)  # this takes a while

window_types = ["gray_stained_glass_pane",
                "green_stained_glass_pane",
                "glass_pane",
                "pink_stained_glass_pane",
                "magenta_stained_glass_pane",
                "blue_stained_glass_pane",
                "red_stained_glass_pane",
                "orange_stained_glass_pane",
                "yellow_stained_glass_pane",
                "purple_stained_glass_pane",
                "cyan_stained_glass_pane",
                "black_stained_glass_pane",
                "lime_stained_glass_pane",
                ]
furniture_list = ['minecraft:barrel', 'minecraft:chest',
                  'minecraft:bookshelf', 'minecraft:crafting_table', 'minecraft:cartography_table',
                  'minecraft:fletching_table', 'minecraft:smithing_table']
utility_list = ['minecraft:chipped_anvil', 'minecraft:enchanting_table', 'minecraft:campfire',
                'minecraft:brewing_stand', 'minecraft:cauldron', 'minecraft:red_bed', 'minecraft:ender_chest',
                'minecraft:lectern', 'minecraft:furnace', 'minecraft:smoker', 'minecraft:blast_furnace'
                ]
CARPETS = ('minecraft:white_carpet', 'minecraft:orange_carpet',
           'minecraft:magenta_carpet', 'minecraft:light_blue_carpet',
           'minecraft:yellow_carpet', 'minecraft:lime_carpet',
           'minecraft:pink_carpet', 'minecraft:gray_carpet',
           'minecraft:light_gray_carpet', 'minecraft:cyan_carpet',
           'minecraft:purple_carpet', 'minecraft:blue_carpet',
           'minecraft:brown_carpet', 'minecraft:green_carpet',
           'minecraft:red_carpet', 'minecraft:black_carpet')
CARPETS_PRIMARY = ('minecraft:orange_carpet', 'minecraft:yellow_carpet', 'minecraft:red_carpet')

torches = ('minecraft:torch', 'minecraft:torch', 'minecraft:torch', 'minecraft:torch', 'minecraft:torch',
           'minecraft:torch', 'minecraft:torch', 'minecraft:torch', 'minecraft:torch', 'minecraft:torch')


def buildhouse(altitude, STARTX, STARTZ, ENDX, ENDZ, biome, ratio):
    xaxis = int((STARTX + ENDX) / 2)
    zaxis = int((STARTZ + ENDZ) / 2)

    y_base = altitude

    # randomizing house height
    house_height = randint(6, 12)

    print("STARTX = " + str(STARTX) + "  |  ENDX = " + str(ENDX))
    print("STARTZ = " + str(STARTZ) + "  |  ENDZ = " + str(ENDZ))
    print("xaxis = " + str(xaxis) + "  |  zaxis = " + str(zaxis))
    print("house_height = " + str(house_height))

    # somehow the height got messed up, but +2 saves it :)
    house_height += 2

    # introducing randomness into building size
    rand_x_building = 0
    rand_z_building = 0
    while rand_x_building == rand_z_building:
        rand_x_building = randint(11, 21)
        rand_z_building = randint(11, 16)
    print("Randomized building length in X: " + str(rand_x_building))
    print("Randomized building length in Z: " + str(rand_z_building))
    biome_ratio = ratio
    print("The current biome (the most frequent block): ", biome, "at a ratio of: ", biome_ratio)

    # calculating surface block mode and ratio right under the house, and if the mode is different then overwrite biome

    house_surface_biome_list = []
    possible_biome_itr = y_base - 1



    for xx in range(xaxis, xaxis + rand_x_building + 1):
        for zz in range(zaxis, zaxis + rand_z_building + 1):
            type = INTF.getBlock(xx, possible_biome_itr, zz)
            possible_biome_itr = y_base - 1
            if type is 'minecraft:air':
                while INTF.getBlock(xx, possible_biome_itr - 1, zz) is 'minecraft:air':
                    possible_biome_itr -= 1
                type = INTF.getBlock(xx, possible_biome_itr - 1, zz)
            house_surface_biome_list.append(type)

    possible_biome = max(set(house_surface_biome_list), key=house_surface_biome_list.count)
    possible_biome_ratio = house_surface_biome_list.count(possible_biome) / len(house_surface_biome_list)
    print("possible biome under the house: ", possible_biome, "at ratio: ", possible_biome_ratio)

    if ((possible_biome_ratio >= biome_ratio and possible_biome != biome) or \
            (biome_ratio > 1 and biome == 'minecraft:water')) and \
            ("snow" not in biome and "ice" not in biome and "mycelium" not in biome and "air" not in possible_biome):
        print("overwriting previous biome: ", biome, "to", possible_biome)
        biome = possible_biome

    # just a patch..
    if "mycelium" in house_surface_biome_list:
        biome = 'minecraft:mycelium'

    main_building_material = 'tnt'
    # determine the main building material using biome
    if "grass" in str(biome):
        main_building_material = random.choice(['minecraft:lime_terracotta',
                                                'minecraft:lime_glazed_terracotta', 'minecraft:green_concrete',
                                                'minecraft:green_glazed_terracotta', 'minecraft:green_terracotta',
                                                'minecraft:melon'])
    elif "water" in str(biome):
        main_building_material = random.choice(['minecraft:light_blue_concrete', 'minecraft:light_blue_terracotta',
                                                'minecraft:light_blue_glazed_terracotta', 'minecraft:blue_concrete',
                                                'minecraft:blue_glazed_terracotta', 'minecraft:blue_terracotta'])
    elif "stone" in str(biome):
        main_building_material = random.choice(['minecraft:stone', 'minecraft:stone_bricks', 'minecraft:smooth_stone',
                                                'minecraft:infested_mossy_stone_bricks',
                                                'minecraft:infested_cobblestone',
                                                'minecraft:polished_andesite', 'minecraft:gray_glazed_terracotta',
                                                'minecraft:gray_concrete',
                                                'minecraft:gray_terracotta', 'minecraft:light_gray_terracotta',
                                                'minecraft:light_gray_concrete',
                                                'minecraft:light_gray_glazed_terracotta'
                                                ])
    elif "ice" in str(biome) or "snow" in str(biome):
        main_building_material = random.choice(
            ['minecraft:snow_block', 'minecraft:quartz_block', 'minecraft:white_glazed_terracotta',
             'minecraft:white_terracotta', 'minecraft:white_concrete',
             'minecraft:ice', 'minecraft:packed_ice', 'minecraft:blue_ice'])
    elif "sand" in str(biome) or "terracotta" in biome:
        main_building_material = random.choice(['minecraft:yellow_concrete', 'minecraft:yellow_terracotta',
                                                'minecraft:yellow_glazed_terracotta', 'minecraft:orange_concrete',
                                                'minecraft:orange_glazed_terracotta', 'minecraft:orange_terracotta'])
    elif "mycelium" in str(biome):
        main_building_material = random.choice(['minecraft:purple_concrete', 'minecraft:purple_terracotta',
                                                'minecraft:purple_glazed_terracotta'])
    else:
        print("oops! what's this biome's color? ", biome)
        main_building_material = random.choice(['minecraft:acacia_log', 'minecraft:jungle_log', 'minecraft:spruce_log',
                                                'minecraft:oak_log'])
    print("The main building material: ", main_building_material)


    # fill the 3D structure as the basis for the walls
    print("Building a hollow cube with the main building material: ", main_building_material, "...")
    for y_house in range(y_base, y_base + house_height):
        for x_house in range(xaxis, xaxis + rand_x_building):
            for z_house in range(zaxis, zaxis + rand_z_building):
                INTF.placeBlock(x_house, y_house, z_house, main_building_material)

    # making empty space in the house
    for y_air in range(y_base + 1, y_base + house_height - 1):
        for x_air in range(xaxis + 1, xaxis + rand_x_building - 1):
            for z_air in range(zaxis + 1, zaxis + rand_z_building - 1):
                INTF.placeBlock(x_air, y_air, z_air, "air")

    # roof
    print("Building a roof...")
    roof = ['glowstone', 'sea_lantern']
    for layer in range(0, randint(3, int(house_height / 2))):
        for x in range(xaxis + layer, xaxis + rand_x_building - layer):
            for z in range(zaxis + layer, zaxis + rand_z_building - layer):
                if len(roof) > 0:
                    INTF.placeBlock(x, y_base + house_height - 1 + layer, z, roof.pop(0))
                else:
                    roof = ['glowstone', 'sea_lantern']
                    INTF.placeBlock(x, y_base + house_height - 1 + layer, z, roof.pop(0))
                # print("layer: " + str(layer) + " | x: " + str(x) + " | z: " + str(z))

    # window
    print("randomizing window allocation...")
    rand_y_bottom = 0
    rand_y_top = 0
    if rand_y_top <= rand_y_bottom:
        rand_y_bottom = randint(1, 3) + y_base
        rand_y_top = y_base + house_height - randint(1, 3)
    if rand_y_top >= y_base + house_height - 1:
        rand_y_top -= 1

    rand_x_start = 0
    rand_x_end = 0

    rand_z_start = 0
    rand_z_end = 0

    # make sure the sizes of the window on different sides of walls are different
    while abs(rand_x_end - rand_x_start) == abs(rand_z_end - rand_z_start) or \
            rand_x_start == rand_z_start or \
            rand_x_end == rand_z_end or \
            abs(rand_x_end - rand_x_start) < 2 or abs(rand_x_end - rand_x_start) > 4 or \
            abs(rand_z_end - rand_z_start) < 2 or abs(rand_z_end - rand_z_start) > 4:
        # seems randint(a, b) is inclusive
        rand_x_start = xaxis + randint(1, 2)
        rand_x_end = rand_x_start + randint(2, 4)

        rand_z_start = zaxis + randint(1, 2)
        rand_z_end = rand_z_start + randint(2, 4)

    if rand_y_top - rand_y_bottom <= 3:
        if y_base + house_height - rand_y_top >= 3:
            rand_y_top += 1
        if rand_y_bottom - y_base >= 3:
            rand_y_bottom -= 1

    # print("rand_y_bottom: " + str(rand_y_bottom) + " |  rand_y_top: " + str(rand_y_top))
    # print("rand_x_start: " + str(rand_x_start) + " |  rand_x_end: " + str(rand_x_end))
    # print("rand_z_start: " + str(rand_z_start) + " |  rand_z_end: " + str(rand_z_end))
    # print("y_base: ", y_base)

    # make windows
    for i in range(rand_x_start, rand_x_end):
        for j in range(rand_y_bottom, rand_y_top):
            INTF.placeBlock(i, j, zaxis + rand_z_building - 1, random.choice(window_types))

    for i in range(rand_x_start, rand_x_end):
        for j in range(rand_y_bottom, rand_y_top):
            INTF.placeBlock(i, j, zaxis, random.choice(window_types))

    for i in range(rand_z_start, rand_z_end):
        for j in range(rand_y_bottom, rand_y_top):
            INTF.placeBlock(xaxis, j, i, random.choice(window_types))

    for i in range(rand_z_start, rand_z_end):
        for j in range(rand_y_bottom, rand_y_top):
            INTF.placeBlock(xaxis + rand_x_building - 1, j, i, random.choice(window_types))

    curr_x_window_length = rand_x_end - rand_x_start
    prev_x_window_end = rand_x_end
    next_x_window_start = prev_x_window_end + (rand_x_start - xaxis)
    next_x_window_end = prev_x_window_end
    num_x_windows = 1

    curr_z_window_length = rand_z_end - rand_z_start
    prev_z_window_end = rand_z_end
    next_z_window_start = prev_z_window_end + (rand_z_start - zaxis)
    next_z_window_end = prev_z_window_end
    num_z_windows = 1

    # build multiple windows on x axis
    while next_x_window_end + curr_x_window_length + (rand_x_start - xaxis) <= xaxis + rand_x_building:

        # print("next x window start: ", next_x_window_start)
        # print("next x window end: ", next_x_window_end)
        # print("prev x window end: ", prev_x_window_end)
        # print("current x window length: ", curr_x_window_length)
        # print("side x length", rand_x_start - xaxis)
        # print("num x windows before building", num_x_windows)
        if num_x_windows * (curr_x_window_length + (rand_x_start - xaxis)) + (rand_x_start - xaxis) > rand_x_building:
            break
        next_x_window_start = prev_x_window_end + (rand_x_start - xaxis)
        next_x_window_end = next_x_window_start + curr_x_window_length

        for i in range(next_x_window_start, next_x_window_end):
            for j in range(rand_y_bottom, rand_y_top):
                INTF.placeBlock(i, j, zaxis + rand_z_building - 1, random.choice(window_types))

        for i in range(next_x_window_start, next_x_window_end):
            for j in range(rand_y_bottom, rand_y_top):
                INTF.placeBlock(i, j, zaxis, random.choice(window_types))

        num_x_windows += 1
        prev_x_window_end = next_x_window_end

    # build multiple windows on z axis
    while next_z_window_end + curr_z_window_length + (rand_z_start - zaxis) <= zaxis + rand_z_building:

        # print("next z window start: ", next_z_window_start)
        # print("next z window end: ", next_z_window_end)
        # print("prev z window end: ", prev_z_window_end)
        # print("current z window length: ", curr_z_window_length)
        # print("side z length", rand_z_start - zaxis)
        # print("num z windows before building", num_z_windows)
        if num_z_windows * (curr_z_window_length + (rand_z_start - zaxis)) + (
                rand_z_start - zaxis) > rand_z_building:
            break
        next_z_window_start = prev_z_window_end + (rand_z_start - zaxis)
        next_z_window_end = next_z_window_start + curr_z_window_length

        for i in range(next_z_window_start, next_z_window_end):
            for j in range(rand_y_bottom, rand_y_top):
                INTF.placeBlock(xaxis, j, i, random.choice(window_types))

        for i in range(next_z_window_start, next_z_window_end):
            for j in range(rand_y_bottom, rand_y_top):
                INTF.placeBlock(xaxis + rand_x_building - 1, j, i, random.choice(window_types))

        num_z_windows += 1
        prev_z_window_end = next_z_window_end

    # fill the gap between house and ground
    max_gap = 0
    print("Filling gap between floor and surface...")
    for x_gap in range(xaxis, xaxis + rand_x_building):
        for z_gap in range(zaxis, zaxis + rand_z_building):
            y_gap = y_base - 1
            gap_ctr = 0
            while INTF.getBlock(x_gap, y_gap, z_gap) == 'minecraft:air' or \
                    INTF.getBlock(x_gap, y_gap, z_gap) == 'minecraft:tall_grass' or \
                    INTF.getBlock(x_gap, y_gap, z_gap) == 'minecraft:grass' or \
                    INTF.getBlock(x_gap, y_gap, z_gap) == 'minecraft:lily_pad':
                gap_ctr += 1
                y_gap -= 1
            if gap_ctr > 0:
                if gap_ctr > max_gap:
                    max_gap = gap_ctr
                for g in range(1, gap_ctr + 1):
                    INTF.placeBlock(x_gap, y_base - g, z_gap, main_building_material)
    print("maximum gap from floor to surface: ", max_gap)

    # build doors
    door_types = ('minecraft:iron_door', 'minecraft:oak_door', 'minecraft:spruce_door', 'minecraft:birch_door',
                  'minecraft:jungle_door', 'minecraft:acacia_door', 'minecraft:dark_oak_door', 'minecraft:crimson_door')
    building_z_mid = int(zaxis + (rand_z_building - 1) / 2)
    building_x_mid = int(xaxis + (rand_x_building - 1) / 2)
    door_coords = [(xaxis, y_base, building_z_mid), (xaxis + rand_x_building - 1, y_base, building_z_mid),
                   (building_x_mid, y_base, zaxis), (building_x_mid, y_base, zaxis + rand_z_building - 1)]

    door_built_flag = False
    final_door_coord = []
    x_door_flag = False
    z_door_flag = False
    for i_door in door_coords:
        if i_door[2] == building_z_mid:
            if INTF.getBlock(i_door[0] + 1, y_base + 1, i_door[2]) != 'minecraft:air' or \
                    INTF.getBlock(i_door[0] - 1, y_base + 1, i_door[2]) != 'minecraft:air':
                print("obstacle near X wall while building door, skipping")
            # ok to build a door
            print("building a door on X axis")
            type_door = random.choice(door_types)
            INTF.placeBlock(i_door[0], y_base + 1, i_door[2], 'minecraft:air')
            INTF.placeBlock(i_door[0], y_base + 2, i_door[2], 'minecraft:air')
            INTF.placeBlock(i_door[0], y_base + 1, i_door[2], type_door)
            INTF.placeBlock(i_door[0], y_base + 2, i_door[2], type_door)
            door_built_flag = True
            x_door_flag = True

            # successfully built a door, now build an entrance beside the door
            # first find the "outside" of the building - don't build the entrance inside
            if INTF.getBlock(i_door[0] - 1, y_base, i_door[2]) == main_building_material:
                # that's inside, build on the other side

                # one side of fence
                INTF.placeBlock(i_door[0] + 1, y_base + 1, i_door[2] - 1, "oak_fence")
                INTF.placeBlock(i_door[0] + 2, y_base + 1, i_door[2] - 1, "oak_fence")
                INTF.placeBlock(i_door[0] + 2, y_base + 2, i_door[2] - 1, "oak_fence")
                INTF.placeBlock(i_door[0] + 1, y_base + 2, i_door[2] - 1, "torch")
                # other side
                INTF.placeBlock(i_door[0] + 1, y_base + 1, i_door[2] + 1, "oak_fence")
                INTF.placeBlock(i_door[0] + 2, y_base + 1, i_door[2] + 1, "oak_fence")
                INTF.placeBlock(i_door[0] + 2, y_base + 2, i_door[2] + 1, "oak_fence")
                INTF.placeBlock(i_door[0] + 1, y_base + 2, i_door[2] + 1, "torch")
                # a small roof of the entrance on top
                for x_entrance in range(i_door[0], i_door[0] + 2):
                    for z_entrance in range(i_door[2] - 1, i_door[2] + 2):
                        # print("building smooth stone for entrance on ", x_entrance, y_base + 3, z_entrance)
                        INTF.placeBlock(x_entrance, y_base + 3, z_entrance, "jack_o_lantern")
                for x_entrance in range(i_door[0], i_door[0] + 2):
                    for z_entrance in range(i_door[2] - 1, i_door[2] + 2):
                        # print("building glowstone for entrance on ", x_entrance, y_base, z_entrance)
                        INTF.placeBlock(x_entrance, y_base, z_entrance, "glowstone")
                # fill gap for entrance
                print("filling gap for entrance...")
                for zg in range(i_door[2] - 1, i_door[2] + 2):
                    for gg in range(1, max_gap + 2):
                        INTF.placeBlock(i_door[0] + 2 + gg, y_base - gg, zg, 'glowstone')

            else:
                # that's outside, build on this side

                # one side of fence
                INTF.placeBlock(i_door[0] - 1, y_base + 1, i_door[2] - 1, "oak_fence")
                INTF.placeBlock(i_door[0] - 2, y_base + 1, i_door[2] - 1, "oak_fence")
                INTF.placeBlock(i_door[0] - 2, y_base + 2, i_door[2] - 1, "oak_fence")
                INTF.placeBlock(i_door[0] - 1, y_base + 2, i_door[2] - 1, "torch")
                # other side
                INTF.placeBlock(i_door[0] - 1, y_base + 1, i_door[2] + 1, "oak_fence")
                INTF.placeBlock(i_door[0] - 2, y_base + 1, i_door[2] + 1, "oak_fence")
                INTF.placeBlock(i_door[0] - 2, y_base + 2, i_door[2] + 1, "oak_fence")
                INTF.placeBlock(i_door[0] - 1, y_base + 2, i_door[2] + 1, "torch")
                # a small roof of the entrance on top
                for x_entrance in range(i_door[0] - 2, i_door[0]):
                    for z_entrance in range(i_door[2] - 1, i_door[2] + 2):
                        # print("building smooth stone for entrance on ", x_entrance, y_base + 3, z_entrance)
                        INTF.placeBlock(x_entrance, y_base + 3, z_entrance, "jack_o_lantern")
                for x_entrance in range(i_door[0] - 2, i_door[0]):
                    for z_entrance in range(i_door[2] - 1, i_door[2] + 2):
                        # print("building glowstone for entrance on ", x_entrance, y_base, z_entrance)
                        INTF.placeBlock(x_entrance, y_base, z_entrance, "glowstone")
                # fill gap for entrance
                print("filling gap for entrance...")
                for zg in range(i_door[2] - 1, i_door[2] + 2):
                    for gg in range(1, max_gap + 2):
                        INTF.placeBlock(i_door[0] - 2 - gg, y_base - gg, zg, 'glowstone')

        if i_door[0] == building_x_mid:
            if INTF.getBlock(i_door[0], y_base + 1, i_door[2] + 1) != 'minecraft:air' or \
                    INTF.getBlock(i_door[0], y_base + 1, i_door[2] - 1) != 'minecraft:air':
                print("obstacle near Z wall while building door, skipping")
            # ok to build a door
            print("building a door on Z axis")
            type_door = random.choice(door_types)
            INTF.placeBlock(i_door[0], y_base + 1, i_door[2], 'minecraft:air')
            INTF.placeBlock(i_door[0], y_base + 2, i_door[2], 'minecraft:air')
            INTF.placeBlock(i_door[0], y_base + 1, i_door[2], type_door)
            INTF.placeBlock(i_door[0], y_base + 2, i_door[2], type_door)
            door_built_flag = True
            z_door_flag = True

            # successfully built a door, now build an entrance beside the door
            # first find the "outside" of the building - don't build the entrance inside
            if INTF.getBlock(i_door[0], y_base, i_door[2] - 1) == main_building_material:
                # that's inside, build on the other side

                # one side of fence
                INTF.placeBlock(i_door[0] - 1, y_base + 1, i_door[2] + 1, "oak_fence")
                INTF.placeBlock(i_door[0] - 1, y_base + 1, i_door[2] + 2, "oak_fence")
                INTF.placeBlock(i_door[0] - 1, y_base + 2, i_door[2] + 2, "oak_fence")
                INTF.placeBlock(i_door[0] - 1, y_base + 2, i_door[2] + 1, "torch")
                # other side
                INTF.placeBlock(i_door[0] + 1, y_base + 1, i_door[2] + 1, "oak_fence")
                INTF.placeBlock(i_door[0] + 1, y_base + 1, i_door[2] + 2, "oak_fence")
                INTF.placeBlock(i_door[0] + 1, y_base + 2, i_door[2] + 2, "oak_fence")
                INTF.placeBlock(i_door[0] + 1, y_base + 2, i_door[2] + 1, "torch")
                # a small roof of the entrace on top
                for x_entrance in range(i_door[0] - 1, i_door[0] + 2):
                    for z_entrance in range(i_door[2], i_door[2] + 2):
                        # print("building smooth stone for entrance on ", x_entrance, y_base + 3, z_entrance)
                        INTF.placeBlock(x_entrance, y_base + 3, z_entrance, "jack_o_lantern")
                for x_entrance in range(i_door[0] - 1, i_door[0] + 2):
                    for z_entrance in range(i_door[2], i_door[2] + 2):
                        # print("building glowstone for entrance on ", x_entrance, y_base, z_entrance)
                        INTF.placeBlock(x_entrance, y_base, z_entrance, 'minecraft:glowstone')
                # fill gap for entrance
                print("filling gap for entrance...")
                for xg in range(i_door[0] - 1, i_door[0] + 2):
                    for gg in range(1, max_gap + 2):
                        INTF.placeBlock(xg, y_base - gg, i_door[2] + 2 + gg, 'glowstone')
            else:
                # that's outside, build on this side

                # one side of fence
                INTF.placeBlock(i_door[0] - 1, y_base + 1, i_door[2] - 1, "oak_fence")
                INTF.placeBlock(i_door[0] - 1, y_base + 1, i_door[2] - 2, "oak_fence")
                INTF.placeBlock(i_door[0] - 1, y_base + 2, i_door[2] - 2, "oak_fence")
                INTF.placeBlock(i_door[0] - 1, y_base + 2, i_door[2] - 1, "torch")
                # other side
                INTF.placeBlock(i_door[0] + 1, y_base + 1, i_door[2] - 1, "oak_fence")
                INTF.placeBlock(i_door[0] + 1, y_base + 1, i_door[2] - 2, "oak_fence")
                INTF.placeBlock(i_door[0] + 1, y_base + 2, i_door[2] - 2, "oak_fence")
                INTF.placeBlock(i_door[0] + 1, y_base + 2, i_door[2] - 1, "torch")
                # a small roof of the entrace on top
                for x_entrance in range(i_door[0] - 1, i_door[0] + 2):
                    for z_entrance in range(i_door[2] - 2, i_door[2]):
                        # print("building smooth stone for entrance on ", x_entrance, y_base + 3, z_entrance)
                        INTF.placeBlock(x_entrance, y_base + 3, z_entrance, "jack_o_lantern")
                for x_entrance in range(i_door[0] - 1, i_door[0] + 2):
                    for z_entrance in range(i_door[2] - 2, i_door[2]):
                        # print("building glowstone for entrance on ", x_entrance, y_base, z_entrance)
                        INTF.placeBlock(x_entrance, y_base, z_entrance, 'minecraft:glowstone')
                # fill gap for entrance
                print("filling gap for entrance...")
                for xg in range(i_door[0] - 1, i_door[0] + 2):
                    for gg in range(1, max_gap + 2):
                        INTF.placeBlock(xg, y_base - gg, i_door[2] - 2 - gg, 'glowstone')

        if door_built_flag:
            final_door_coord = [i_door[0], i_door[2]]
            break

    # finally. furniture
    print("randomizing furniture allocation...")

    old_fur_list = furniture_list

    furniture_list.extend(old_fur_list)
    furniture_list.extend(utility_list)

    for _ in range(0, 9):
        furniture_list.extend(CARPETS_PRIMARY)

    old_fur_list = furniture_list
    furniture_list.extend(old_fur_list)

    # print("length of appended furniture list: ", len(furniture_list), "\n\n\n")
    for x_fur in range(xaxis + 1, xaxis + rand_x_building - 1):
        for z_fur in range(zaxis + 1, zaxis + rand_z_building - 1):
            if (x_door_flag and z_fur in range(final_door_coord[1] - 2, final_door_coord[1] + 3)) or \
                    (z_door_flag and x_fur in range(final_door_coord[0] - 2, final_door_coord[0] + 3)):
                # leave the doopstep open
                INTF.placeBlock(x_fur, y_base + 1, z_fur, random.choice(CARPETS))
                continue
            random.shuffle(furniture_list)
            if len(furniture_list) > 0:
                if INTF.getBlock(x_fur, y_base, z_fur) != main_building_material:
                    print("current floor occupied at ", x_fur, z_fur, " by ", INTF.getBlock(x_fur, y_base, z_fur),
                          " == ", main_building_material)
                    continue
                item = furniture_list.pop(-1)
                # print("placing a furniture, length of furniture list: ", len(furniture_list))
                INTF.placeBlock(x_fur, y_base + 1, z_fur, item)
            else:
                print("ran out of furniture to place! placing carpets instead")
                space_filler = ['glowstone', 'sea_lantern']
                space_filler.extend(CARPETS_PRIMARY)
                INTF.placeBlock(x_fur, y_base + 1, z_fur, random.choice(space_filler))

    # sugarcane decoration
    print("building a sugarcane lamp...")

    sugarcane_coords = [[building_x_mid - 1, building_z_mid], [building_x_mid + 1, building_z_mid],
                        [building_x_mid, building_z_mid - 1], [building_x_mid, building_z_mid + 1]]
    sugarcane_height_list = []
    for s in range(3, house_height - 3):
        sugarcane_height_list.append(s)

    INTF.placeBlock(building_x_mid, y_base, building_z_mid, 'water')
    INTF.placeBlock(building_x_mid, y_base + 1, building_z_mid, 'air')
    INTF.placeBlock(building_x_mid, y_base + 1, building_z_mid, 'minecraft:lily_pad')

    prev_sugarcane_height = 0
    for sugarcane in range(0, 4):
        INTF.placeBlock(sugarcane_coords[sugarcane][0], y_base, sugarcane_coords[sugarcane][1], 'grass_block')
        random.shuffle(sugarcane_height_list)
        if len(sugarcane_height_list) > 0:
            sugarcane_height = sugarcane_height_list.pop(-1)
            prev_sugarcane_height = sugarcane_height
        else:
            sugarcane_height = prev_sugarcane_height

        if sugarcane_height < 2:
            sugarcane_height = 2

        for itr_sgr in range(y_base + 1, y_base + sugarcane_height + 1):
            INTF.placeBlock(sugarcane_coords[sugarcane][0], itr_sgr, sugarcane_coords[sugarcane][1],
                            'minecraft:sugar_cane')
        INTF.placeBlock(sugarcane_coords[sugarcane][0], y_base + sugarcane_height + 1, sugarcane_coords[sugarcane][1],
                        'glowstone')
        INTF.placeBlock(sugarcane_coords[sugarcane][0], y_base + sugarcane_height + 2, sugarcane_coords[sugarcane][1],
                        'minecraft:oak_leaves')

    # adding extra illumination
    print("adding torches to increase illumination")
    max_torches = 20
    for x_floor in range(xaxis + 1, xaxis + rand_x_building - 2):
        for z_floor in range(zaxis + 1, zaxis + rand_z_building - 2):
            if max_torches == 0:
                print("reached maximum number of torches")
                break
            if "carpet" not in str(INTF.getBlock(x_floor, y_base + 1, z_floor)) and \
                    INTF.getBlock(x_floor, y_base + 1, z_floor) != 'minecraft:sugar_cane':
                # 50% change to get a torch on top of furniture
                if randint(0, 10) % 2 == 0:
                    INTF.placeBlock(x_floor, y_base + 2, z_floor, 'torch')
                    max_torches -= 1


if __name__ == '__main__':
    # NOTE: It is a good idea to keep this bit of the code as simple as
    #     possible so you can find mistakes more easily

    try:
        height = WORLDSLICE.heightmaps["MOTION_BLOCKING"][(STARTX, STARTY)]
        INTF.runCommand(f"tp @a {STARTX} {height} {STARTZ}")
        print(f"/tp @a {STARTX} {height} {STARTZ}")
        INTF.runCommand("time set day")

        # tune this to adjust the search area
        search_area = 60

        surface = []
        surface_type = []
        # search for build area
        print("Searching for a suitable terrain to start building...")
        for x in range(int(STARTX - search_area / 2), int(STARTX + search_area / 2), 2):
            for z in range(int(STARTZ - search_area / 2), int(STARTX + search_area / 2), 2):
                surface_height = height
                water_flag = False
                if INTF.getBlock(x, height, z) == 'minecraft:air':
                    # print("in mid air")
                    while surface_height > 0:
                        block_type = INTF.getBlock(x, surface_height - 1, z)
                        if block_type != 'minecraft:air':
                            if block_type == 'minecraft:water' or block_type == 'minecraft:lily_pad':
                                print("touched water downward! skipping the current block", x, surface_height - 1, z)
                                water_flag = True
                                surface_type.append('minecraft:water')
                            surface_type.append(block_type)
                            break
                        else:
                            surface_height -= 1
                    #     print(surface_height)
                    #     print(block_type)
                    #     print(INTF.getBlock(x, surface_height - 1, z))

                    if not water_flag:
                        surface.append([x, surface_height - 1, z])
                        print("found surface downward: ", x, surface_height - 1, z)
                else:
                    # print("underground")
                    while surface_height < 180:
                        curr = INTF.getBlock(x, surface_height, z)
                        block_type = INTF.getBlock(x, surface_height + 1, z)
                        if block_type == 'minecraft:air':
                            if curr == 'minecraft:water' or curr == 'minecraft:lily_pad':
                                print("touched water upward! skipping the current block", x, surface_height + 1, z)
                                water_flag = True
                            break
                        else:
                            surface_height += 1
                        # print(surface_height)
                        # print(block_type)
                        # print(INTF.getBlock(x, surface_height + 1, z))
                    if not water_flag:
                        surface.append([x, surface_height + 1, z])
                        print("found surface upward: ", x, surface_height + 1, z)

        print("surface: ", surface)
        if len(surface) == 0:
            print("ERROR! NO AVAILABLE TERRAIN WITHIN +/-", int(search_area / 2), "BLOCKS OF SPAWN POINT. PLEASE CHOOSE ANOTHER MAP!")
            exit("Exiting program due to no suitable terrain")


        # finding the biome
        biome = max(set(surface_type), key=surface_type.count)
        biome_ratio = surface_type.count(biome) / len(surface)

        # set the build area
        terrain_heights = []
        terrain_heights_rounded = []
        for i in surface:
            terrain_heights.append(i[1])

        # round the height to nearest 3's
        print("terrain height before rounding: ", terrain_heights)
        for i in terrain_heights:
            terrain_heights_rounded.append(3 * round(i / 3))
        print("terrain height after rounding: ", terrain_heights_rounded)

        # find the mode of rounded heights
        mode = max(set(terrain_heights_rounded), key=terrain_heights.count)

        # find how many times does this mode appear in the rounded list
        times_mode_occur = 0
        for i in terrain_heights_rounded:
            if i == mode:
                times_mode_occur += 1
        print("Mode of rounded List height: ", mode, ", appeared ", times_mode_occur, " times.")

        # find the middle occurrence of the mode
        mid_occurrence = randint(int(times_mode_occur * (1/3)), int(times_mode_occur * (2/3)))
        print("The randomized middle occurrence of the mode from its 1/3 ~ 2/3 distribution of in the rounded height list: ", mid_occurrence)

        # find the index of the mid-located mode item in rounded height list
        index = 0
        idx_ctr = 0
        for i in terrain_heights_rounded:
            if idx_ctr >= mid_occurrence:
                # print("mid occurrence reached! exiting loop")
                break
            if i == mode:
                idx_ctr += 1
            index += 1
        best_fit_coord = surface[index]
        print("found the best fit coordinate for build area: ", best_fit_coord, ", at surface list's index: ", index)

        # tune this to adjust build area size
        build_area_size = 70
        build_height = 20

        # updating new STARTX, STARTY, STARTZ, ENDX, ENDY, ENDZ
        STARTX = int(best_fit_coord[0] - (build_area_size / 2))
        STARTY = int(best_fit_coord[1] - build_height)
        STARTZ = int(best_fit_coord[2] - (build_area_size / 2))
        ENDX = int(best_fit_coord[0] + (build_area_size / 2))
        ENDY = int(best_fit_coord[1] + build_height)
        ENDZ = int(best_fit_coord[2] + (build_area_size / 2))

        # make sure the selected coordinate is at the center of the new build area
        INTF.setBuildArea(STARTX, STARTY, STARTZ, ENDX, ENDY, ENDZ)

        # building the actual house
        buildhouse(altitude=best_fit_coord[1], STARTX=STARTX, STARTZ=STARTZ, ENDX=ENDX, ENDZ=ENDZ, biome=biome, ratio=biome_ratio)

        # teleport to the house
        INTF.runCommand(f"tp @a {best_fit_coord[0]} {best_fit_coord[1] + 20} {best_fit_coord[2]}")
        print(f"/tp @a {best_fit_coord[0]} {best_fit_coord[1] + 20} {best_fit_coord[2]}")

        print("Done!")
    except KeyboardInterrupt:  # useful for aborting a run-away program
        print("Pressed Ctrl-C to kill program.")
