from __future__ import division
from __future__ import print_function
import sys
import math
import time
import Queue as Q
import heapq
import resource
#### SKELETON CODE ####
## The Class that Represents the Puzzle
class PuzzleState(object):
    """
        The PuzzleState stores a board configuration and implements
        movement instructions to generate valid children.
    """
    def __init__(self, config, n, parent=None, action="Initial", cost=0):
        """
        :param config->List : Represents the n*n board, for e.g. [0,1,2,3,4,5,6,7,8] represents the goal state.
        :param n->int : Size of the board
        :param parent->PuzzleState
        :param action->string
        :param cost->int
        """
        if n*n != len(config) or n < 2:
            raise Exception("The length of config is not correct!")
        if set(config) != set(range(n*n)):
           raise Exception("Config contains invalid/duplicate entries : ", config)

        self.n        = n
        self.cost     = cost
        self.parent   = parent
        self.action   = action
        self.config   = config
        self.children = []
        # Get the index and (row, col) of empty block
        self.blank_index = self.config.index(0)

    def display(self):
        """ Display this Puzzle state as a n*n board """
        for i in range(self.n):
            print(self.config[3*i : 3*(i+1)])

    def move_up(self):
        if self.blank_index - self.n >=0:
            newState = self.config[:]
            i,j = self.blank_index,self.blank_index-self.n
            newState[i],newState[j] = newState[j],newState[i]
            tempSt = PuzzleState(newState,self.n,self,"Up",self.cost + 1)
            return tempSt
        return None
         
    def move_down(self):
        if self.blank_index + self.n < self.n*self.n:
            newState = self.config[:]
            i,j = self.blank_index,self.blank_index + self.n
            newState[i],newState[j] = newState[j],newState[i]
            tempSt = PuzzleState(newState,self.n,self,"Down",self.cost + 1)
            return tempSt
        return None
      
    def move_left(self):
        if self.blank_index % self.n != 0:
            newState = self.config[:]
            i,j = self.blank_index,self.blank_index-1
            newState[i],newState[j] = newState[j],newState[i]
            tempSt = PuzzleState(newState,self.n,self,"Left",self.cost + 1)
            return tempSt
        return None
    def move_right(self):
        if (self.blank_index + 1) % self.n  != 0:
            newState = self.config[:]
            i,j = self.blank_index,self.blank_index+1
            newState[i],newState[j] = newState[j],newState[i]
            tempSt = PuzzleState(newState,self.n,self,"Right",self.cost + 1) 
            return tempSt
        return None 
    def expand(self):
        # Node has already been expanded
        if len(self.children) != 0:
            return self.children
        # Add child nodes in order of UDLR
        children = [
            self.move_up(),
            self.move_down(),
            self.move_left(),
            self.move_right()]

        # Compose self.children of all non-None children states
        self.children = [state for state in children if state is not None]
        return self.children
class Node(object):
    def __init__(self,dataIn=None,prevIn=None,nextIn=None):
        self.data = dataIn
        self.prev = prevIn
        self.nex = nextIn
class Frontier(object):
    def __init__(self):
        self.head = None
        self.tail = self.head
        self.container = set()
        self.hq = [] 
    def add(self,dataIn):
        if self.head == None:
            self.head = Node(dataIn)
            self.tail = self.head
        else:
            temp = Node(dataIn)
            temp.prev = self.tail
            self.tail.nex = temp
            self.tail = temp
        self.container.add(tuple(dataIn.config))
    def heapPush(self,state):
        val = calculate_total_cost(state) 
        heapq.heappush(self.hq,(val,state))
        self.container.add(tuple(state.config))
    def contains(self,target):
        return tuple(target.config) in self.container
    def isEmpty(self):
        return self.head == None and not self.hq
    def dequeue(self):
        if not self.isEmpty():
            temp = self.head
            self.head = self.head.nex
            if self.head == None:
                self.tail = self.head
            else:
                self.head.prev = None
            return temp.data
        return None
    
    def pop(self):
        if not self.isEmpty():
            temp = self.tail
            self.tail = self.tail.prev
            if self.tail == None:
                self.head = self.tail
            else:
                self.tail.next = None
            return temp.data
        return None

    def deleteMin(self):
        return heapq.heappop(self.hq)

# Function that Writes to output.txt
def writeOutput(child,numOfExpands,maxDepth,timeTaken):
    cost = child.cost 
    parent = child.parent
    path = []
    while parent != None:
        path.append(child.action)
        child = parent
        parent = parent.parent
    f = open("output.txt","w")
    f.write("path_to_goal: " + str(path[::-1]) + "\n")
    f.write("cost_of_path: " + str(cost) + "\n")
    f.write("nodes_expanded: " + str(numOfExpands) + "\n")
    f.write("search_depth: " + str(cost) + "\n")
    f.write("max_search_depth: " + str(maxDepth)+ "\n")
    f.write("running_time: {:.8f}\n".format(timeTaken))
    f.write("max_ram_usage: {:.8f}\n".format(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000))
    f.close()
    return       

def bfs_search(initial_state):
    tt = time.time()
    frontier = Frontier()
    frontier.add(initial_state)
    explored = set()
    maxDepth = 0
    while not frontier.isEmpty():
        state = frontier.dequeue()
        if test_goal(state): 
            et = time.time()
            writeOutput(state,len(explored),maxDepth,et - tt)
            return
        explored.add(tuple(state.config))
        for neighbor in state.expand():
            if not frontier.contains(neighbor) and tuple(neighbor.config) not in explored:
                if maxDepth < neighbor.cost:
                    maxDepth = neighbor.cost
                frontier.add(neighbor)
    return

def dfs_search(initial_state):
    tt = time.time()
    frontier = Frontier()
    frontier.add(initial_state)
    explored = set()
    maxDepth = 0
    while not frontier.isEmpty():
        state = frontier.pop()
        if test_goal(state): 
            et = time.time()
            writeOutput(state,len(explored),maxDepth,et - tt)
            return
        explored.add(tuple(state.config))
        for neighbor in reversed(state.expand()):
            if not frontier.contains(neighbor) and tuple(neighbor.config) not in explored: 
                if maxDepth < neighbor.cost:
                    maxDepth = neighbor.cost
                frontier.add(neighbor)
    return

def A_star_search(initial_state):
    tt = time.time()
    frontier = Frontier()
    frontier.heapPush(initial_state)
    explored = set()
    maxDepth = 0
    while not frontier.isEmpty():
        state = frontier.deleteMin()
        if test_goal(state[1]):
            et = time.time()
            writeOutput(state[1],len(explored),maxDepth,et- tt)
            return
        explored.add(tuple(state[1].config))
        for neighbor in state[1].expand():
            if not frontier.contains(neighbor) and tuple(neighbor.config) not in explored:
                if maxDepth < neighbor.cost:
                    maxDepth = neighbor.cost
                frontier.heapPush(neighbor)
            elif frontier.contains(neighbor):
                frontier.heapPush(neighbor)
    return

def calculate_total_cost(state):
    return calculate_manhattan_dist(state.config,0,state.n*state.n) + state.cost

def calculate_manhattan_dist(idx, value, n):
    result = 0
    goal = 1 
    while goal < n:
        current = idx.index(goal)
        if current != goal:
            x1 = current % int(math.sqrt(n))
            y1 = int(current / int(math.sqrt(n)))
            x2 = goal % int(math.sqrt(n))
            y2 = int(goal / int(math.sqrt(n)))
            result += abs(x2-x1) + abs(y2-y1) 
        goal += 1
    return result
    
def test_goal(puzzle_state):
    return puzzle_state.config == range(puzzle_state.n*puzzle_state.n)
# Main Function that reads in Input and Runs corresponding Algorithm
def main():
    search_mode = sys.argv[1].lower()
    begin_state = sys.argv[2].split(",")
    begin_state = list(map(int, begin_state))
    board_size  = int(math.sqrt(len(begin_state)))
    hard_state  = PuzzleState(begin_state, board_size)
    start_time  = time.time()
    
    if   search_mode == "bfs": bfs_search(hard_state)
    elif search_mode == "dfs": dfs_search(hard_state)
    elif search_mode == "ast": A_star_search(hard_state)
    else: 
        print("Enter valid command arguments !")
        
    end_time = time.time()
    print("Program completed in %.3f second(s)"%(end_time-start_time))

if __name__ == '__main__':
    main()
