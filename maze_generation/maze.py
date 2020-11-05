from PIL import Image
import numpy as np
import cv2
import random
import tkinter as tk
import tkinter.filedialog as tkf
import json
import threading


def get_color():
    """
    This is the function that define the color and corresponding values
    :return: a dict link colors to values
    """
    WALL = 0
    PATH = 1
    VALID_PATH = 2
    INVALID_PATH = 3
    ENDPOINT = 4
    COLORS = {
        WALL: (0, 0, 0),
        PATH: (255, 255, 255),
        VALID_PATH: (0, 255, 0),
        INVALID_PATH: (255, 0, 0),
        ENDPOINT: (0, 0, 255),
    }
    return COLORS


def generate_maze(width, height, name, fps, start=(0, 0), blocksize=20):
    """
    This is the function that generate the maze, output the generation video and the final maze picture
    :param width: the width of the maze
    :param height: the length of the maze
    :param name:the basename you want to name the out put
    :param fps: the fps for the video
    :param start:the start point of the generation
    :param blocksize:the block size of the the final maze picture
    :return:no return
    """
    # create two list that one is the real maze the other is the oversize maze to reduce the complexity of generation
    maze = [[0 for _ in range(width)] for _ in range(height)]
    oversize_maze = [[0 for _ in range(width + 1)] for _ in range(height + 1)]
    current_position = [start]
    next_move = [(0, 1), (0, -1), (-1, 0), (1, 0)]
    x, y = current_position[-1]
    maze[x][y] = 1
    oversize_maze[x][y] = 1
    # create a new image
    img = Image.new("RGB", (blocksize * height, blocksize * width), color=0)
    # using opencv to create a video writer
    frame_size = (blocksize * height, blocksize * width)
    video_writer = cv2.VideoWriter(name+".avi", cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), fps, frame_size)
    img = save_maze(start, blocksize, img, maze, name)
    # create a list to contain each frame of the generation process
    frames = [img]
    next_direction = random.sample(next_move, 1)
    jump = []
    count = 0
    while len(current_position) > 0:
        x += next_direction[0][0]
        y += next_direction[0][1]
        # if the new coordinate is in the range of the maze
        if x in range(height) and y in range(width):
            # determine if can make the new move
            verify = oversize_maze[x][y] + oversize_maze[x - 1][y] + oversize_maze[x + 1][y] \
                     + oversize_maze[x][y - 1] + oversize_maze[x][y + 1]
            # if can make the move then change the value of the maze and add a frame to the frame list
            # if can not make the move then bake to the last move
            if verify == 1:
                maze[x][y] = 1
                oversize_maze[x][y] = 1
                current_position.append((x, y))
                frames.append(img)
                img = save_maze(current_position[-1], blocksize, img, maze, name)
                next_direction = random.sample(next_move, 1)
            else:
                [x, y] = current_position[-1]
                next_direction = random.sample(next_move, 1)
        # if cannot make the move then back to the last move
        else:
            x -= next_direction[0][0]
            y -= next_direction[0][1]
            next_direction = random.sample(next_move, 1)
        # this part is to determine if the generation has moved to a dead end
        length = len(current_position)
        if length in jump:
            count += 1
        else:
            count = 0
            jump.append(length)
        # if the generation has moved to a dead end then pop one coordinate and move to a new branch
        if count == 10:
            jump = []
            count = 0
            current_position.pop()
            if current_position:
                [x, y] = current_position[-1]
                next_direction = random.sample(next_move, 1)
            else:
                continue
        else:
            continue
        # this is the part to create the video
        for frame in frames:
            i = cv2.cvtColor(np.asarray(frame), cv2.COLOR_RGB2BGR)
            video_writer.write(i)
        frames = []
    # this is the part save the final maze picture
    save_maze(current_position, blocksize, img, maze, name, save_video=False)


def save_maze(position, blocksize, img, maze, name, save_video=True):
    """
    This is the function to save the final picture or return a updated image object
    :param position: if choose to save video then this argument is the coordinate that need to update to the image
    :param blocksize: the size of the block in the image
    :param img: if choose save video then this is a image object that will be updated
    :param maze: the maze list
    :param name: the name for the maze
    :param save_video: a bool argument that will let you choose to update video frame image object or just save a picture
    :return: if choose to save video then return a updated image object else no return
    """
    width = len(maze[0])
    height = len(maze)
    if save_video:
        # this part will triggered if choose to save video
        # this part just update the changing part of the frame so it will run super fast
        pixels = img.load()
        xx = position[0]
        yy = position[1]
        x = xx * blocksize
        y = yy * blocksize
        for i in range(blocksize):
            for j in range(blocksize):
                pixels[x + i, y + j] = get_color()[maze[xx][yy]]
        img = img.copy()
        return img
    else:
        img = Image.new("RGB", (blocksize * height, blocksize * width), color=0)
        pixels = img.load()
        for xx in range(height):
            for yy in range(width):
                x = xx * blocksize
                y = yy * blocksize
                for i in range(blocksize):
                    for j in range(blocksize):
                        pixels[x + i, y + j] = get_color()[maze[xx][yy]]
        if ".png" not in name:
            name += ".png"
        img.save("%d_%d_%d_%s" % (width, height, blocksize, name))


def load_maze(filename, blocksize=20):
    """
    this is the function for the solving part, load a maze from a picture directly
    :param filename: the maze picture file
    :param blocksize: the block size of the maze picture
    :return:a list and an image object
    """
    img = Image.open(filename)
    height1, width1 = img.size
    height = height1 // blocksize
    width = width1 // blocksize
    pixels = img.load()
    maze = [[0 for _ in range(width)] for _ in range(height)]
    color_dic = {i: j for j, i in get_color().items()}
    for i, x in enumerate(range(0, height1, blocksize)):
        for j, y in enumerate(range(0, width1, blocksize)):
            maze[i][j] = color_dic[pixels[x, y]]
    return maze, img


def solve_maze(maze, img, end, name, fps, start=(0, 0), blocksize=20):
    """
    this is the function that will solve the maze, and output to a video and a final solution image
    :param maze: the list that is the maze
    :param img: an image object that loaded from the maze picture
    :param end: the end point you want to end
    :param name: the base name for the solution video and the picture
    :param fps: the fps for the solution video
    :param start: the start point of the solution
    :param blocksize: the block size of the maze picture
    :return: no return
    """
    current_position = [start]
    next_move = [(0, 1), (0, -1), (-1, 0), (1, 0)]
    x, y = current_position[-1]
    width = len(maze[0])
    height = len(maze)
    # print(width, height)
    maze[start[0]][start[1]] = 4
    # create a video writer
    frame_size = (blocksize * height, blocksize * width)
    video_writer = cv2.VideoWriter(name + ".avi", cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), fps, frame_size)
    end = find_valid_end_point(maze, end, next_move)
    # print(end)
    maze[end[0]][end[1]] = 4
    img = save_maze(start, blocksize, img, maze, name)
    img = save_maze(end, blocksize, img, maze, name)
    frames = []
    count = 0
    jump = []
    while (x, y) != end:
        # this is the part to generate the video
        for item in frames:
            ii = cv2.cvtColor(np.asarray(item), cv2.COLOR_RGB2BGR)
            video_writer.write(ii)
        frames = []
        # if can make the move then change the value of the corresponding coordinate and
        # add one updated image object to the video frame list
        # if cannot make the move then back to the last step
        for move in next_move:
            x += move[0]
            y += move[1]
            if x in range(height) and y in range(width):
                if maze[x][y] == 1:
                    maze[x][y] = 2
                    current_position.append((x, y))
                    img = save_maze(current_position[-1], blocksize, img, maze, name)
                    frames.append(img)
                elif maze[x][y] == 4 and (x, y) != start:
                    current_position.append((x, y))
                    frames.append(img)
                else:
                    [x, y] = current_position[-1]
            else:
                x -= move[0]
                y -= move[1]
        # this part is to determine if move to a dead end
        length = len(current_position)
        if length in jump:
            count += 1
        else:
            count = 0
            jump.append(length)
        # if move to a dead end then pop on coordinate and convert to another branch
        if count == 6:
            jump = []
            count = 0
            [x, y] = current_position[-1]
            maze[x][y] = 3
            img = save_maze(current_position[-1], blocksize, img, maze, name)
            current_position.pop()
            if current_position:
                [x, y] = current_position[-1]
            else:
                continue
        else:
            continue
    # ii = cv2.cvtColor(np.asarray(frames[0]), cv2.COLOR_RGB2BGR)
    # video_writer.write(ii)
    save_maze(current_position, blocksize, frames[0], maze, name, save_video=False)


def find_valid_end_point(maze, end, next_move):
    """
    this is the function to generate the valid end point from the end point you desire
    :param maze: the maze list
    :param end: the end point you want to end
    :param next_move: the list contain all possible move
    :return: a valid end point
    """
    x = end[0]
    y = end[1]
    while True:
        direct = random.sample(next_move, 1)
        try:
            if maze[end[0]][end[1]] == 1:
                end = (end[0], end[1])
                return end
            else:
                x -= direct[0][0]
                y -= direct[0][1]
                end = (x, y)
        except IndexError:
                x += direct[0][0]
                y += direct[0][1]
                end = (x, y)


def gui():
    """
    this is the GUI interface
    :return: no return
    """
    root = tk.Tk()
    # Create labels and entrys
    tk.Label(root, text="Generate maze and sole maze").grid(row=0, columnspan=2)
    tk.Label(root, text="Maze width: ").grid(row=1, column=0)
    tk.Label(root, text="Maze length: ").grid(row=2, column=0)
    tk.Label(root, text="fps for the video(fps): ").grid(row=3, column=0)
    tk.Label(root, text="block size: ").grid(row=4, column=0)
    tk.Label(root, text="start point: ").grid(row=5, column=0)
    tk.Label(root, text="end point: ").grid(row=6, column=0)
    lb = tk.Label(root, text='''     the output is in the same folder with this python script''')
    lb.grid(row=7, columnspan=2)
    e1 = tk.Entry(root)
    e2 = tk.Entry(root)
    e3 = tk.Entry(root)
    e4 = tk.Entry(root)
    e5 = tk.Entry(root)
    e6 = tk.Entry(root)
    e1.grid(row=1, column=1, padx=10, pady=5)
    e2.grid(row=2, column=1, padx=10, pady=5)
    e3.grid(row=3, column=1, padx=10, pady=5)
    e4.grid(row=4, column=1, padx=10, pady=5)
    e5.grid(row=5, column=1, padx=10, pady=5)
    e6.grid(row=6, column=1, padx=10, pady=5)
    e3.insert(0, "30")
    e4.insert(0, "20")
    e5.insert(0, "[0, 0]")

    def generate_and_solve():
        """
        this is the function that will triggered when click the button
        :return: no return
        """
        try:
            width = int(e1.get())
            height = int(e2.get())
            fps = int(e3.get())
            blocksize = int(e4.get())
            start = json.loads(e5.get())
            end = json.loads(e6.get())

            def sub_process(width, height, fps, start, blocksize):
                """
                this is the sub process for the multi threading, deal with the GUI no response problem
                when take a longtime to compute
                :param width: the maze width
                :param height: the maze length
                :param fps: the video frame
                :param start: the start point for the maze
                :param blocksize: the block size for the image
                :return: no return
                """
                lb.config(text="Maze Generating....")
                generate_maze(width, height, 'maze', fps, start, blocksize)
                maze, img = load_maze("%d_%d_%d_maze.png" % (width, height, blocksize))
                # end = (len(maze) - 1, len(maze[0]) - 1)
                lb.config(text="Solving maze....")
                solve_maze(maze, img, end, "solution", fps, start, blocksize)
                lb.config(text="Solution is available!!!")
            t = threading.Thread(target=sub_process, args=(width, height, fps, start, blocksize))
            t.setDaemon(True)
            t.start()
            e3.delete(0, tk.END)
            e3.insert(0, "30")
            e4.delete(0, tk.END)
            e4.insert(0, "20")
            e5.delete(0, tk.END)
            e5.insert(0, "[0, 0]")
            e1.delete(0, tk.END)
            e2.delete(0, tk.END)
            e6.delete(0, tk.END)
        except:
            lb.config(text="please check your input!!!")

    def auto_endpoint_generation():
        """
        this is the function automatically generate the end point
        :return: no return
        """
        try:
            width = int(e1.get())
            height = int(e2.get())
            e6.insert(0, json.dumps([height - 1, width - 1]))
        except:
            lb.config(text="please check your input!!!")
    tk.Button(root, text="generate", width=10, command=generate_and_solve).grid(row=8, column=2,
                                                                               sticky=tk.E, padx=10, pady=5)
    tk.Button(root, text="auto generate endpoint", command=auto_endpoint_generation).grid(row=8, column=1,
                                                                                              padx=10, pady=5)
    tk.Button(root, text="exit", width=10, command=root.quit).grid(row=8, column=0, sticky=tk.W, padx=10, pady=5)
    root.mainloop()


if __name__ == "__main__":
    gui()
    # generate_maze(20, 30, 'test', 15, start=json.loads("[0, 0]"))
    # maze, img = load_maze("20_30_20_test.png")
    # print((len(maze) - 1, len(maze[0]) - 1))
    # solve_maze(maze, img, json.loads("[29, 19]"), "solve_test", 15)