import enum

class Maze(object):

    def __init__(self, maze, cellcodes):
        self.maze = maze
        self.cellcodes = cellcodes
        for row_idx in range(len(self.maze)):
            for col_idx in range(len(self.maze[row_idx])):
                if self.maze[row_idx][col_idx] == self.cellcodes.START:
                    self.startPos = [col_idx, row_idx]

    def __repr__(self):
        out = ''
        for row in self.maze:
            for char in row:
                if char == self.cellcodes.WALL:
                    symb = '#'
                elif char == self.cellcodes.EMPTY:
                    symb = ' '
                elif char == self.cellcodes.ROUTE:
                    symb = '.'
                elif char == self.cellcodes.START:
                    symb = 'S'
                elif char == self.cellcodes.GOAL:
                    symb = 'G'
                out += (symb + '  ')
            out += '\n'
        return out

    # Gets value for position of maze
    def getPositionValue(self, x, y):
        if (x < 0 or y < 0 or x >= len(self.maze) or y >= len(self.maze[0])):
            return self.cellcodes.WALL
        return self.maze[y][x]

    # Check if position is wall
    def isWall(self, x, y):
        return self.getPositionValue(x, y) == self.cellcodes.WALL
    
    def isGoal(self, x, y):
        return self.getPositionValue(x, y) == self.cellcodes.GOAL

    # Gets maximum index of x position
    def getMaxX(self):
        return len(self.maze[0])-1

    # Gets maximum index of y position
    def getMaxY(self):
        return len(self.maze)-1

    # Scores a maze route
    def scoreRoute(self, route):
        score = 0
        visited = [[False] * (self.getMaxY()+1) for _ in range(self.getMaxX()+1)]
        # Loop over route and score each move
        for routeStep in route:
            step = routeStep
            if (self.maze[step[1]][step[0]] == self.cellcodes.ROUTE and visited[step[1]][step[0]] == False):
                # Increase score for correct move
                score += 1
                # Remove reward
                visited[step[1]][step[0]] = True
        return score
    

coordinates = enum.Enum('coordinates', 'NORTH EAST SOUTH WEST')

class Robot:

    ''' Initalize a robot with controller '''
    def __init__(self, controller, maze, maxMoves, movecodes, opcodes):
        self.movecodes = movecodes
        self.opcodes = opcodes
        self.controller = controller
        self.maze = maze
        startPos = self.maze.startPos
        self.xPosition = startPos[0]
        self.yPosition = startPos[1]
        self.sensorVal = None
        self.heading = coordinates.SOUTH
        self.maxMoves = maxMoves
        self.n_moves = 0
        self.moves= []
        self.route = []
        self.route.append(startPos)

    ''' Runs the robot's actions based on sensor inputs '''
    def run(self):
        while self.n_moves < self.maxMoves:
            if self.maze.isGoal(self.xPosition, self.yPosition):
                break
            # Run action
            self.makeNextAction()
            self.n_moves += 1

    def eval(self):
        program = self.controller.copy()
        stack = self.getSensorValue().copy()
        while program != []:
            op = program[0]
            program = program[1:]
            if op == self.opcodes.IF:
                op1 = stack.pop()
                if op1:
                    program = [program[0]] + program[2:]
                else:
                    program = program[1:]
            elif op == self.opcodes.NOT:
                op1 = stack.pop()
                stack.append(not op1)
            elif op == self.opcodes.AND:
                op1 = stack.pop()
                op2 = stack.pop()
                stack.append(op1 and op2)
            elif op == self.opcodes.OR:
                op1 = stack.pop()
                op2 = stack.pop()
                stack.append(op1 or op2)
            elif op == self.opcodes.NOP:
                pass
            else:
                return op # Op is a move
        return None # If we end up here the program is 'invalid'
    
    ''' Runs the next action '''
    def makeNextAction(self):
        # If move forward
        move = self.getNextAction()
        if move == self.movecodes.FORWARD:
            currentX = self.xPosition
            currentY = self.yPosition

            # Move depending on current direction
            if self.heading == coordinates.NORTH:
                self.yPosition += -1
                if self.yPosition < 0:
                    self.yPosition = 0
            
            if self.heading == coordinates.EAST:
                self.xPosition += 1
                if self.xPosition > self.maze.getMaxX():
                    self.xPosition = self.maze.getMaxX()

            if self.heading == coordinates.SOUTH:
                self.yPosition += 1
                if self.yPosition > self.maze.getMaxY():
                    self.yPosition = self.maze.getMaxY()
            
            if self.heading== coordinates.WEST:
                self.xPosition += -1
                if self.xPosition < 0:
                    self.xPosition = 0

            # We can't move here
            if (self.maze.isWall(self.xPosition, self.yPosition) == True):
                self.xPosition = currentX
                self.yPosition = currentY

            else:
                if (currentX != self.xPosition or currentY != self.yPosition):
                    self.route.append(self.getPosition())

        elif move == self.movecodes.RIGHT:

            if self.heading == coordinates.NORTH:
                self.heading = coordinates.EAST

            elif self.heading == coordinates.EAST:
                self.heading = coordinates.SOUTH

            elif self.heading == coordinates.SOUTH:
                self.heading = coordinates.WEST

            elif self.heading == coordinates.WEST:
                self.heading = coordinates.NORTH
        
        elif move == self.movecodes.LEFT:

            if self.heading == coordinates.NORTH:
                self.heading = coordinates.WEST

            elif self.heading == coordinates.EAST:
                self.heading = coordinates.NORTH

            elif self.heading == coordinates.SOUTH:
                self.heading = coordinates.EAST

            elif self.heading == coordinates.WEST:
                self.heading = coordinates.SOUTH

        # Reset sensor value
        self.sensorVal = None
        self.moves.append(move)
                
    ''' Get next action depending on sensor mapping '''
    def getNextAction(self):
        res = self.eval()
        if res is None:
            raise Exception('Invalid output for the controller')
        return res 

    def getSensorValue(self):
        # If sensor value has already been calculated
        if self.sensorVal is not None:
            return self.sensorVal

        frontSensor = frontLeftSensor = frontRightSensor = leftSensor = rightSensor = backSensor = False

        # Find which sensors have been activated
        if self.getHeading() == coordinates.NORTH:
            frontSensor = self.maze.isWall(self.xPosition, self.yPosition-1)
            frontLeftSensor = self.maze.isWall(self.xPosition-1, self.yPosition-1)
            frontRightSensor = self.maze.isWall(self.xPosition+1, self.yPosition-1)
            leftSensor = self.maze.isWall(self.xPosition-1, self.yPosition)
            rightSensor = self.maze.isWall(self.xPosition+1, self.yPosition)
            backSensor = self.maze.isWall(self.xPosition, self.yPosition+1)

        elif self.getHeading() == coordinates.EAST:
            frontSensor = self.maze.isWall(self.xPosition+1, self.yPosition)
            frontLeftSensor = self.maze.isWall(self.xPosition+1, self.yPosition-1)
            frontRightSensor = self.maze.isWall(self.xPosition+1, self.yPosition+1)
            leftSensor = self.maze.isWall(self.xPosition, self.yPosition-1)
            rightSensor = self.maze.isWall(self.xPosition, self.yPosition+1)
            backSensor = self.maze.isWall(self.xPosition-1, self.yPosition)

        elif self.getHeading() == coordinates.SOUTH:
            frontSensor = self.maze.isWall(self.xPosition, self.yPosition+1)
            frontLeftSensor = self.maze.isWall(self.xPosition+1, self.yPosition+1)
            frontRightSensor = self.maze.isWall(self.xPosition-1, self.yPosition+1)
            leftSensor = self.maze.isWall(self.xPosition+1, self.yPosition)
            rightSensor = self.maze.isWall(self.xPosition-1, self.yPosition)
            backSensor = self.maze.isWall(self.xPosition, self.yPosition-1)

        else:
            frontSensor = self.maze.isWall(self.xPosition-1, self.yPosition)
            frontLeftSensor = self.maze.isWall(self.xPosition-1, self.yPosition+1)
            frontRightSensor = self.maze.isWall(self.xPosition-1, self.yPosition-1)
            leftSensor = self.maze.isWall(self.xPosition, self.yPosition+1)
            rightSensor = self.maze.isWall(self.xPosition, self.yPosition-1)
            backSensor = self.maze.isWall(self.xPosition+1, self.yPosition)

        # Calculate sensor value
        sensorVal = [frontSensor, frontLeftSensor, frontRightSensor, leftSensor, rightSensor, backSensor]
        self.sensorVal = sensorVal
        return sensorVal

    ''' Get robot's position '''
    def getPosition(self):
        return [self.xPosition, self.yPosition]

    ''' Get robot's heading '''
    def getHeading(self):
        return self.heading

    ''' Returns robot's complete route around the maze '''
    def getRoute(self):
        return self.route