import requests
import json
import collections
import sys
import time
from pandas import DataFrame
from enum import Enum

UKN = ' '
WALL = 'W'
EXPLORED = 'E'
maze = None
x_dim = None
y_dim = None

url = "http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com"
ID = {'uid' : 304937334 }

Action = Enum('Action', 'UP DOWN LEFT RIGHT')
def undo(action):
    if action == Action.UP.name:
        return Action.DOWN.name
    elif action == Action.DOWN.name:
        return Action.UP.name
    elif action == Action.LEFT.name:
        return Action.RIGHT.name
    elif action == Action.RIGHT.name:
        return Action.LEFT.name

class Coord:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Coord(x, y)

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return Coord(x, y)
    
    def __repr__(self):
        return 'Coord(%r, %r)' % (self.x, self.y)
    
    def move(self, dir):
        return self + DIR[dir]

    def undo(self, dir):
        return self - DIR[dir]

    def valid(self):
        return ((self.x >= 0) and (self.y >= 0) and (self.x < x_dim) and (self.y < y_dim))

DIR = {
        'UP' : Coord(0, -1),
        'DOWN' : Coord(0, 1),
        'LEFT' : Coord(-1, 0),
        'RIGHT' : Coord(1, 0)
    }

""" Return value indicates whether we should still continue """
def probe(curr_loc):
    for action in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
        new_loc = curr_loc.move(action)
        if ((not new_loc.valid()) or maze[new_loc.y][new_loc.x] != UKN):
            continue
        move = {'action' : action}
        response = requests.post(url + '/game?token=' + TOKEN, data=move)
        time.sleep(0.050)
        data = response.json()
        result = data['result']
        if result == 'SUCCESS':
            maze[new_loc.y][new_loc.x] = EXPLORED
            print(DataFrame(maze))
            if probe(new_loc):
                return True
            else:
                move = {'action' : undo(action)}
                response = requests.post(url + '/game?token=' + TOKEN, data=move)
                time.sleep(0.050)
        elif result == 'WALL':
            maze[new_loc.y][new_loc.x] = WALL
            print(DataFrame(maze))
        elif result == 'OUT_OF_BOUNDS':
            print("moved to invalid location, should not happen!")
        elif result == 'END':
            return True
    return False
    

""" Initialize Session """
session = requests.post(url + '/session', data=ID)
session_data = session.json()
TOKEN = session_data['token']


""" GAME """

while True:
    game = requests.get(url + '/game?token=' + TOKEN)
    game_data = game.json()
    
    if game_data['status'] == 'FINISHED':
        break

    loc = game_data['current_location']
    dim = game_data['maze_size']
    (x_dim, y_dim) = dim
    (x_start, y_start) = game_data['current_location']

    maze = [[UKN for _ in range(x_dim) ] for _ in range(y_dim)]
    maze[y_start][x_start] = EXPLORED
    print(DataFrame(maze))

    if probe(Coord(x_start, y_start)):
        print('Solved Level: %d!' % (game_data['levels_completed']))



    
