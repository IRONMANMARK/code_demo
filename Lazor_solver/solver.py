import os
import numpy as np
from itertools import combinations
from tqdm import tqdm
import math
import time
import profile


def load_file(path, suff="bff"):
    """
    this is the function that load the file in
    :param path: the file folder for that contain the bff files
    :param suff: the suffix of the bff file
    :return: a file name list and a file path list
    """
    name_list = []
    file_list = []
    # this is used to walk though the file folder
    for fpath, dirs, i in os.walk(path):
        for f in i:
            suffix = f.split('.')
            if suffix[1] == suff:
                name_list.append(suffix[0])
                file_list.append(os.path.join(fpath, f))
            else:
                continue
    return name_list, file_list


def function_main(path):
    """
    this is the main function to generate the solution for the game
    :param path: the file folder path
    :return: no return
    """
    name_list, file_list = load_file(path)
    # process a file at a time
    for f in file_list:
        grid = []
        laser = []
        point = []
        block = {}
        fixed_block = []
        possible_position = []
        # read in the grid, laser, point, block, fixed block
        for line in open(f).readlines():
            # process the file
            line = line.strip('\n')
            if line == "GRID START" or line == "GRID STOP" or line == '' or line[0] == '#':
                continue
            elif line[0].isupper():
                line = line.split(" ")
                if line[0] == "L":
                    try:
                        laser.append(
                            ((int(line[1]), int(line[2])), (int(line[1]) + int(line[3]), int(line[2]) + int(line[4]))))
                    except:
                        continue
                elif line[0] == "P":
                    try:
                        point.append((int(line[1]), int(line[2])))
                    except:
                        continue
                else:
                    if line[1].isdigit():
                        block[line[0]] = int(line[1])
                    else:
                        a = []
                        for i in line:
                            if i.isalpha():
                                a.append(i)
                        grid.append(a)
            else:
                a = []
                for i in line:
                    if i.isalpha():
                        a.append(i)
                grid.append(a)
        # process the grid lines
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] == "o":
                    possible_position.append((j, i))
                elif grid[i][j].isupper():
                    fixed_block.append(((j, i), grid[i][j]))
        print("\nsolving " + f + " .....")
        start = time.time()
        # generate the solution
        solution = main_algorithm(possible_position, fixed_block, laser, point, block)
        end = time.time()
        print("solving time is %s seconds." % (end - start))
        out_to_file(f, solution[1], grid)


def out_to_file(file_path, solution, grid):
    """
    this is the function to out put the solution to a text file
    :param file_path: the file path for the bff file
    :param solution: the solution generated
    :param grid: the board for the game
    :return: no return
    """
    out_file = file_path.split('.')[0] + "_solution.txt"
    name = file_path.split('.')[0].split(os.sep)[1]
    ff = open(out_file, "w")
    ff.write("The following is the solution for %s \n" % name)
    for s in solution:
        cord = s[0]
        grid[cord[1]][cord[0]] = s[1]
    for ii in grid:
        for jj in ii:
            ff.write(jj + '\t')
        ff.write('\n')
    ff.close()
    print("solution for %s is in %s. \n" % (name, out_file))


def main_algorithm(possible_position, fixed_block, laser, point, block):
    """
    this is the mian algorithm for generate the solution
    :param possible_position: the position that can put a block
    :param fixed_block: a list contain the fixed block position and type
    :param laser: a list contain all the laser
    :param point: a list contain all the destination
    :param block: a dict that contain the number for eack type of the block
    :return:
    """
    block_total = sum(block.values())
    sub = list(block.values())[0]
    key = list(block.keys())
    key_length = len(block.keys())
    # this is the part generate all possible combination
    for total_item in tqdm(combinations(possible_position, block_total)):
        # process the different kind of the block
        if key_length == 2:
            for item in combinations(total_item, sub):
                block_list = []
                key_1_set = set(total_item) - set(item)
                for i in item:
                    block_list.append((i, key[0]))
                for i in key_1_set:
                    block_list.append((i, key[1]))
                block_list.extend(fixed_block)
                # after generate one of the combination to calculate the solution
                is_solution, solution = core_part(block_list, laser, point)
                if is_solution:
                    return is_solution, solution
        elif key_length == 1:
            block_list = []
            for item in total_item:
                block_list.append((item, key[0]))
            block_list.extend(fixed_block)
            is_solution, solution = core_part(block_list, laser, point)
            if is_solution:
                return is_solution, solution


def core_part(block_list, laser, point):
    """
    this is the core part for the algorithm
    :param block_list: one of the possible block combination for the given level
    :param laser: a list contain all the laser
    :param point: a list that contain all the destination
    :return: return a bool type an the the block list
    """
    test = []
    count22 = 0
    # calculate the laser path and if the laser reached the destination
    while True:
        # trace the laser and update the laser and the destination
        # is the laser reached one of the destination the point list will remove one
        laser_use = []
        for cord in laser:
            point, laser_use, new_laser = sub_core_part(block_list, point, laser_use, cord)
        # determine if the laser reached no blocks and if the current position is the solution
        if len(laser_use) == 0:
            if len(point) == 0:
                return True, block_list
            else:
                try:
                    np.isnan(new_laser[0][1])
                    return False, block_list
                except:
                    laser = laser_use
        elif laser_use == laser:
            if len(point) == 0:
                return True, block_list
            else:
                return False, block_list
        else:
            laser = laser_use
            for i in laser_use:
                if i in test:
                    count22 += 1
                else:
                    test.append(i)
            if count22 > 3:
                return False, block_list
            else:
                pass


def sub_core_part(block_list, point, laser_use, cord):
    """
    this is the sub function for laser tracing
    :param block_list: one of the possible block combination for the given level
    :param point: a list that contain all the destination
    :param laser_use: a list that contain the updated laser
    :param cord: one of the laser need to track
    :return: updated destination list, updated laser list, new laser(i.e the reflect, refract laser)
    """
    count2 = 0
    dis = float("inf")
    final_item = "none"
    # determine the laser intersect a block or not
    for block_item in block_list:
        bl = Block(block_item)
        _, new_laser, count, new_dis = bl.process(cord, point)
        if count > 1:
            if new_dis < dis:
                final_item = block_item
                dis = new_dis
            else:
                pass
        else:
            count2 += 1
    # if there is a block in the laser path calculate the out laser
    if final_item != "none":
        bl = Block(final_item)
        point, new_laser, count, _ = bl.process(cord, point)
        for i in new_laser:
            try:
                len(i[1])
                laser_use.append(i)
            except:
                pass
    else:
        pass
    # find out if the laser intersect a destination point
    if count2 == len(block_list):
        new_point = [i for i in point if not Laser(cord).laser_isintersect(i)]
        point = new_point
    else:
        pass
    return point, laser_use, new_laser


def is_point_between(new_laser, query):
    """
    this is the function that calculate if the query point is between two point
    :param new_laser: the two point given
    :param query: the query point
    :return: bool type
    """
    start = new_laser[0]
    end = new_laser[1]
    if min([start[0], end[0]]) <= query[0] <= max([start[0], end[0]]) \
            and min([start[1], end[1]]) <= query[1] <= max([start[1], end[1]]):
        return True
    else:
        return False


def calculate_distance_between_two_point(point1, point2):
    """
    this is the function that calculate the distance between the two point
    :param point1: point 1
    :param point2: point 2
    :return: the distance between the two points
    """
    x = abs(point1[0] - point2[0])
    y = abs(point1[1] - point2[1])
    dis = math.sqrt(x ** 2 + y ** 2)
    return dis


class Block:
    def __init__(self, block_item):
        """
        :param block_item: contain the block position and the block type
        """
        self.block_position = block_item[0]
        self.block_type = block_item[1]

    def process(self, laser_start_end, destination):
        """
        this is the function that process the laser
        :param laser_start_end: contain laser start point and laser end point
        :param destination: this is the destination list
        :return: new destination point, new laser, the number of the intersection, the distance between laser start and
        the intersection
        """
        # find out if the laser intersect and the intersection point
        intersection, _, _, intersection_num, dis = Block.find_intersection(self, laser_start_end)
        if all(np.isnan(intersection)) or intersection_num == 1:
            return destination, ((np.NaN, np.NaN),), intersection_num, dis
        else:
            replica = []
            if self.block_type == "B":
                new_laser = Block.opaque(self, laser_start_end)
            elif self.block_type == "A":
                new_laser = Block.reflect(self, laser_start_end)
            elif self.block_type == "C":
                new_laser = Block.refract(self, laser_start_end)
            for i in destination:
                if Laser(laser_start_end).laser_isintersect(i) and is_point_between(
                        (laser_start_end[0], intersection), i):
                    pass
                else:
                    replica.append(i)
            return replica, new_laser, intersection_num, dis

    def generate_all_intersection(self):
        """
        this is the function generate all the possible intersection point on a block
        :return: intersection point and a dict that corresponding the point to the surface
        """
        x_cord = 2 * self.block_position[0] + 1
        y_cord = 2 * self.block_position[1] + 1
        intersect_surface = {(x_cord, y_cord - 1): 'up', (x_cord, y_cord + 1): 'down',
                             (x_cord - 1, y_cord): 'left', (x_cord + 1, y_cord): 'right'}
        return ((x_cord, y_cord - 1),
                (x_cord, y_cord + 1),
                (x_cord - 1, y_cord),
                (x_cord + 1, y_cord)), intersect_surface

    def find_intersection(self, laser_start_end):
        """
        this is the function that find the intersection point on the block with the given laser
        :param laser_start_end: laser start and end point
        :return: the intersection point, the surface, the count(if count > 1 means the laser intersect) and the distance
        between the laser start and the intersection point
        """
        dis = float('inf')
        intersect, surface = Block.generate_all_intersection(self)
        a = (np.NaN, np.NaN)
        count = 0
        # find out if there is a intersection
        final = [[i, calculate_distance_between_two_point(laser_start_end[0], i)]
                 for i in intersect if Laser(laser_start_end).laser_isintersect(i)]
        final = sorted(final, key=lambda x: x[1])
        # print(final)
        length = len(final)
        if length != 0:
            a, dis = final[0]
            count = length
        else:
            pass
        return a, surface, intersect, count, dis

    def reflect(self, laser_start_end):
        """
        this is the function that calculate the reflect block
        :param laser_start_end: the laser start end point
        :return: the reflect laser coordinate
        """
        a, surface, intersection, _, _ = Block.find_intersection(self, laser_start_end)
        sur = surface.get(a)
        origin_direction = Laser(laser_start_end).laser_direction()
        if all(np.isnan(a)):
            out = np.NaN
        else:
            if sur == 'left' or sur == "right":
                new_direction = (- origin_direction[0], origin_direction[1])
                out = (a[0] + new_direction[0], a[1] + new_direction[1])
            else:
                new_direction = (origin_direction[0], - origin_direction[1])
                out = (a[0] + new_direction[0], a[1] + new_direction[1])
        return (a, out),

    def refract(self, laser_start_end):
        """
        this is the function that calculate the refract block
        :param laser_start_end: the laser start end point
        :return: the refract laser coordinate
        """
        origin_direction = Laser(laser_start_end).laser_direction()
        reflect_laser = Block.reflect(self, laser_start_end)
        if np.isnan(reflect_laser[0][0][0]):
            return reflect_laser + ((np.NaN, np.NaN),)
        else:
            origin_new = ((reflect_laser[0][0][0] + origin_direction[0], reflect_laser[0][0][1] + origin_direction[1]),
                          (reflect_laser[0][0][0] + 2 * origin_direction[0],
                           reflect_laser[0][0][1] + 2 * origin_direction[1]))
            return reflect_laser + (origin_new,)

    def opaque(self, laser_start_end):
        """
        this is the function that calculate the opaque block
        :param laser_start_end: the laser start end point
        :return: the intersection and set the out coordinate to nan
        """
        a, _, _, _, _ = Block.find_intersection(self, laser_start_end)
        return (a, np.NaN),


class Laser:
    def __init__(self, laser_start_end):
        self.laser_start_end = laser_start_end
        self.start = laser_start_end[0]
        self.end = laser_start_end[1]

    def line(self):
        """
        this is the function to calculate the line k, b
        :return: the k, b for the line
        """
        k = (self.start[1] - self.end[1]) / (self.start[0] - self.end[0])
        b = self.start[1] - k * self.start[0]
        return k, b

    def laser_isintersect(self, query):
        """
        find out if the laser intersect with a query point
        :param query: query point
        :return: bool type
        """
        xx, yy = query
        k, b = Laser.line(self)
        direction = Laser.laser_direction(self)
        dis = k * xx - yy + b
        if query == self.start:
            return True
        else:
            sx, sy = self.start
            query_xv = xx - sx
            query_yv = yy - sy
            abs_xv = abs(query_xv)
            abs_yv = abs(query_yv)
            try:
                query_direction = (query_xv / abs_xv, query_yv / abs_yv)
            except:
                query_direction = (query_xv, query_yv)

            if dis == 0 and query_direction == direction:
                return True
            else:
                return False

    def laser_direction(self):
        """
        generate the laser direction
        :return: laser direction
        """
        return self.end[0] - self.start[0], self.end[1] - self.start[1]


def unit_test():
    """
    this is the unit test
    :return: no return
    """
    print(Block(((0, 1), 'B')).find_intersection(((0, 5), (1, 4))))
    points = [(1, 2), (2, 1), (3, 4)]
    result, new, _ = Block(((0, 1), 'C')).process(((1, 2), (2, 3)), points)
    print(result)
    print(new)
    print(core_part([((0, 0), 'A'), ((0, 2), 'A'), ((2, 0), 'A'), ((1, 2), 'C'), ((1, 0), 'B')], [((4, 5), (3, 4))],
                    [(1, 2), (6, 3)]))
    print(calculate_distance_between_two_point((2, 2), (1, 1)))
    profile.run('function_main("bff_files")')


if __name__ == "__main__":
    folder = input("Please input the file folder contain the .bff files: ")
    start = time.time()
    function_main(folder)
    end = time.time()
    print("total runtime is %0.2f seconds." % (end - start))