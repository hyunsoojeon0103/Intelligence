import random
from BaseAI_3 import BaseAI
import time
import math
timeLimit = 0.18
class PlayerAI(BaseAI):
    
    def getMove(self, grid):
        startTime = time.process_time()
        alpha,beta = -math.inf,math.inf
        idsDepth = 0
        idsLimit = 1
        decision = self.maximize(grid,alpha,beta,startTime,idsDepth,idsLimit)
        return decision[0]

    def maximize(self,grid,alpha,beta,startTime,idsDepth,idsLimit):
        if idsDepth >= idsLimit:
            return [None,self.evaluate(grid)]
        if time.process_time() - startTime > timeLimit:
            return [None,self.evaluate(grid)]

        maxNode = [None,-math.inf]
        
        while time.process_time() - startTime <= timeLimit:
            for child in grid.getAvailableMoves():
                temp = self.minimize(child[1],alpha,beta,startTime,idsDepth,idsLimit)
                if temp[1] > maxNode[1]:
                    maxNode[1] = temp[1]
                    maxNode[0] = child[0]
                if maxNode[1] >= beta:
                    break
                if maxNode[1] > alpha:
                    alpha = maxNode[1]
            if idsDepth == 0:
                idsLimit += 1
                alpha,beta = -math.inf,math.inf
            else:
                break
       
        return maxNode 

    def minimize(self,grid,alpha,beta,startTime,idsDepth,idsLimit):
        if idsDepth >= idsLimit:
            return [None,self.evaluate(grid)]
        if time.process_time() - startTime > timeLimit:
            return [None,self.evaluate(grid)]

        minNode = [None,math.inf]

        for pos in grid.getAvailableCells():
                chance = self.expectMiniMax(grid,alpha,beta,startTime,idsDepth,idsLimit,pos)
                if chance < minNode[1]:
                    minNode[1] = chance
                if minNode[1] <= alpha:
                    break
                if minNode[1] < beta:
                    beta = minNode[1]

        return minNode 

    def expectMiniMax(self,grid,alpha,beta,startTime,idsDepth,idsLimit,pos):
        newGrid = grid.clone()
        newGrid2 = grid.clone()
        newGrid.insertTile(pos,2)
        newGrid2.insertTile(pos,4)
        temp = self.maximize(newGrid,alpha,beta,startTime,idsDepth+1,idsLimit)
        temp2 = self.maximize(newGrid2,alpha,beta,startTime,idsDepth+1,idsLimit)
        return 0.9 * temp[1] + 0.1 * temp2[1]    

    def evaluate(self,grid):
        return self.givePattern(grid)

    def givePattern(self,grid):
        pts = 0
        pattern = self.getSnakePattern(grid)

        significance = len(pattern) / 10.0 
        offset = significance / len(pattern)

        for i in range(len(pattern)):
            pts += pattern[i] * pow(significance,significance)
            significance -= offset 

        return pts
   
    def getSnakePattern(self,grid):
        snake = list()
        size = grid.size
        for i in range(size):
            if i % 2 == 0:
                for j in range(size):
                    snake.append(grid.map[i][j])
            else:
                for j in range(size-1,-1,-1):
                    snake.append(grid.map[i][j])
        return snake
