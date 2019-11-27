# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

from captureAgents import CaptureAgent
import util
from game import Directions, Actions
import math

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first='OffensiveReflexAgent', second='DefensiveReflexAgent'):
    """
    This function should return a list of two agents that will form the
    team, initialized using firstIndex and secondIndex as their agent
    index numbers.  isRed is True if the red team is being created, and
    will be False if the blue team is being created.

    As a potentially helpful development aid, this function can take
    additional string-valued keyword arguments ("first" and "second" are
    such arguments in the case of this function), which will come from
    the --redOpts and --blueOpts command-line arguments to capture.py.
    For the nightly contest, however, your team will be created without
    any extra arguments, so you should make sure that the default
    behavior is what you want for the nightly contest.
    """

    # The following line is an example only; feel free to change it.
    return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at baselineTeam.py for more details about how to
    create an agent as this is the bare minimum.
    """

    def __init__(self, index, timeForComputing=.1):
        CaptureAgent.__init__(self, index, timeForComputing)

    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the
        agent to populate useful fields (such as what team
        we're on).

        A distanceCalculator instance caches the maze distances
        between each pair of positions, so your agents can use:
        self.distancer.getDistance(p1, p2)

        IMPORTANT: This method may run for at most 15 seconds.
        """

        '''
        Make sure you do not delete the following line. If you would like to
        use Manhattan distances instead of maze distances in order to save
        on initialization time, please take a look at
        CaptureAgent.registerInitialState in captureAgents.py.
        '''
        CaptureAgent.registerInitialState(self, gameState)

        self.home = gameState.getAgentState(self.index).getPosition()
        self.walls = gameState.getWalls().asList()
        self.numFoodToDefend = len(self.getFoodYouAreDefending(gameState).asList())
        self.nearestEatenFood = None

    def getMiddleLines(self, gameState):
        middleLines = []
        actualMiddleLines = []
        if self.red:
            for y in range(0, gameState.data.layout.height):
                middleLines.append((gameState.data.layout.width / 2 - 1, y))
        else:
            for y in range(0, gameState.data.layout.height):
                middleLines.append((gameState.data.layout.width / 2, y))
        for ml in middleLines:
            if ml not in self.walls:
                actualMiddleLines.append(ml)
        return actualMiddleLines

    def getNearestMiddleLine(self, gameState):
        distance = []
        nearestMiddleLines = []
        middleLines = self.getMiddleLines(gameState)
        for ml in middleLines:
            distance.append(self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), ml))
        for m, d in zip(middleLines, distance):
            if d == min(distance): nearestMiddleLines.append(m)
        if len(nearestMiddleLines) != 0:
            return nearestMiddleLines[0]
        return None

    def getOpponentAttackers(self, gameState):
        attackers = []
        for o in self.getOpponents(gameState):
            if gameState.getAgentState(o).isPacman and gameState.getAgentState(o).getPosition() != None:
                attackers.append(gameState.getAgentState(o))
        return attackers

    def getNearestOpponentAttacker(self, gameState):
        distance = []
        nearestAttackers = []
        attackers = self.getOpponentAttackers(gameState)
        if len(attackers) != 0:
            for a in attackers:
                distance.append(self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), a.getPosition()))
            for a, d in zip(attackers, distance):
                if d == min(distance): nearestAttackers.append(a)
            if len(nearestAttackers) != 0:
                return nearestAttackers[0]
        return None

    def getOpponentDefenders(self, gameState):
        defenders = []
        for o in self.getOpponents(gameState):
            if not gameState.getAgentState(o).isPacman and gameState.getAgentState(o).getPosition() != None:
                defenders.append(gameState.getAgentState(o))
        return defenders

    def getNearestFoodToEat(self, gameState):
        distance = []
        nearestFood = []
        food = self.getFood(gameState).asList()
        for f in food:
            distance.append(self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), f))
        for f, d in zip(food, distance):
            if d == min(distance): nearestFood.append(f)
        if len(nearestFood) != 0:
            return nearestFood[0]
        return None

    def getNearestFoodToDefend(self, gameState):
        distance = []
        nearestFood = []
        food = self.getFoodYouAreDefending(gameState).asList()
        for f in food:
            distance.append(self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), f))
        for f, d in zip(food, distance):
            if d == min(distance): nearestFood.append(f)
        if len(nearestFood) != 0:
            return nearestFood[0]
        return None

    def getNearestCapsule(self, gameState):
        distance = []
        nearestCapsules = []
        capsules = self.getCapsules(gameState)
        for c in capsules:
            distance.append(self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), c))
        for c, d in zip(capsules, distance):
            if d == min(distance): nearestCapsules.append(c)
        if len(nearestCapsules) != 0:
            return nearestCapsules[0]
        return None

    def hasFood(self, gameState, x, y):
        for f in self.getFood(gameState).asList():
            if x == f[0] and y == f[1]:
                return True
        return False

    def getDirectlyAvailableFoodToEat(self, gameState):
        directlyAvailableFood = []
        for f in self.getFood(gameState).asList():
            foodFringes = []
            count = 0
            foodFringes.append((f[0] + 1, f[1]))
            foodFringes.append((f[0] - 1, f[1]))
            foodFringes.append((f[0], f[1] + 1))
            foodFringes.append((f[0], f[1] - 1))
            for foodFringe in foodFringes:
                if (foodFringe[0], foodFringe[1]) not in self.walls and \
                        not self.hasFood(gameState, foodFringe[0], foodFringe[1]):
                    count = count + 1
            if count > 1:
                directlyAvailableFood.append(f)
        return directlyAvailableFood

    def getNearestDirectlyAvailableFoodToEat(self, gameState):
        distance = []
        nearestAvailableFood = []
        directlyAvailableFood = self.getDirectlyAvailableFoodToEat(gameState)
        for f in directlyAvailableFood:
            distance.append(self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), f))
        for f, d in zip(directlyAvailableFood, distance):
            if d == min(distance): nearestAvailableFood.append(f)
        if len(nearestAvailableFood) != 0:
            return nearestAvailableFood[0]
        return None

    def getNearestEatenFood(self, gameState):
        eatenFood = []
        distance = []
        nearestEatenFood = []
        previousToDefend = self.getFoodYouAreDefending(self.getPreviousObservation()).asList()
        currentToDefend = self.getFoodYouAreDefending(self.getCurrentObservation()).asList()
        for f in previousToDefend:
            if f not in currentToDefend:
                eatenFood.append(f)
        for f in eatenFood:
            distance.append(self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), f))
        for f, d in zip(eatenFood, distance):
            if d == min(distance): nearestEatenFood.append(f)
        if len(nearestEatenFood) != 0:
            self.nearestEatenFood = nearestEatenFood[0]
            return nearestEatenFood[0]
        return None

    def getSuccessors(self, currentPosition):
        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x, y = currentPosition
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if (nextx, nexty) not in self.walls:
                nextPosition = (nextx, nexty)
                successors.append((nextPosition, action, 1))
        return successors

    def nullHeuristic(self, gameState, currentPosition):
        return 0

    def avoidOpponentDefenderHeuristic(self, gameState, currentPosition):
        heuristics = []
        defenders = self.getOpponentDefenders(gameState)
        if len(defenders) == 0:
            return 0
        else:
            for d in defenders:
                dist = self.getMazeDistance(currentPosition, d.getPosition())
                if dist < 3:
                    heuristics.append(math.pow((dist - 5), 4))
                else:
                    heuristics.append(0)
            return max(heuristics)

    def avoidOpponentAttackerHeuristic(self, gameState, currentPosition):
        heuristics = []
        attackers = self.getOpponentAttackers(gameState)
        if len(attackers) == 0:
            return 0
        else:
            for a in attackers:
                dist = self.getMazeDistance(currentPosition, a.getPosition())
                if dist < 3:
                    heuristics.append(math.pow((dist - 5), 4))
                else:
                    heuristics.append(0)
            return max(heuristics)

    def aStarSearch(self, gameState, goal, heuristic):
        start = self.getCurrentObservation().getAgentState(self.index).getPosition()
        open = util.PriorityQueue()
        actions = []
        open.push((start, actions, 0), 0 + heuristic(gameState, start))
        closed = []
        while not open.isEmpty():
            node, actions, accCost = open.pop()
            if node not in closed:
                closed.append(node)
                if node == goal:
                    if len(actions) == 0: return Directions.STOP
                    return actions[0]
                for succ, action, stepCost in self.getSuccessors(node):
                    g = accCost + stepCost
                    if succ not in closed:
                        open.push((succ, actions + [action], 1), g + heuristic(gameState, succ))
        return Directions.STOP

class OffensiveReflexAgent(ReflexCaptureAgent):

    def distanceToNearestMiddleLine(self, gameState):
        nearestMiddleLine = self.getNearestMiddleLine(gameState)
        return self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), nearestMiddleLine)

    def isOpponentDefenderStartScare(self, defender):
        if defender.scaredTimer > 10: return True
        return False

    def isOpponentDefenderFinishScare(self, defender):
        if 10 >= defender.scaredTimer > 0: return True
        return False

    def isMyAttackerScare(self, gameState):
        if gameState.getAgentState(self.index).scaredTimer > 0 and \
                not gameState.getAgentState(self.index).isPacman: return True
        return False

    def isOurAttackerReturnInTiem(self, gameState):
        if self.distanceToNearestMiddleLine(gameState) + 60 > gameState.data.timeleft: return True
        return False

    def chooseAction(self, gameState):

        nearestCapsule = self.getNearestCapsule(gameState)
        nearestFoodToEat = self.getNearestFoodToEat(gameState)
        nearestDirectlyAvailableFood = self.getNearestDirectlyAvailableFoodToEat(gameState)
        nearestMiddleLine = self.getNearestMiddleLine(gameState)
        defenders = self.getOpponentDefenders(gameState)
        attackers = self.getOpponentAttackers(gameState)

        # when my attacker is scared
        if self.isMyAttackerScare(gameState):
            if len(attackers) != 0:
                for attacker in attackers:
                    if self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), attacker.getPosition()) < 3:
                        return self.aStarSearch(gameState, self.home, self.avoidOpponentAttackerHeuristic)

        # when to return back to the nearest middle line
        if gameState.getAgentState(self.index).numCarrying > 10 or self.isOurAttackerReturnInTiem(gameState):
            return self.aStarSearch(gameState, nearestMiddleLine, self.avoidOpponentDefenderHeuristic)

        # when to escape
        if len(defenders) != 0:
            for defender in defenders:
                if self.getMazeDistance(defender.getPosition(), gameState.getAgentState(self.index).getPosition()) < 4 and \
                        self.isOpponentDefenderFinishScare(defender):
                    return self.aStarSearch(gameState, nearestMiddleLine, self.avoidOpponentDefenderHeuristic)

        # when to search for the nearest directly available food to eat
        if len(self.getDirectlyAvailableFoodToEat(gameState)) != 0:
            if len(defenders) != 0:
                for defender in defenders:
                    if self.getMazeDistance(defender.getPosition(), nearestDirectlyAvailableFood) < 2:
                        return self.aStarSearch(gameState, nearestMiddleLine, self.avoidOpponentDefenderHeuristic)
                return self.aStarSearch(gameState, nearestDirectlyAvailableFood, self.avoidOpponentDefenderHeuristic)

            # when to search for the nearest food to eat
        if len(defenders) != 0:
            for defender in defenders:
                if self.isOpponentDefenderStartScare(defender) or \
                        self.getMazeDistance(defender.getPosition(), gameState.getAgentState(self.index).getPosition()) > 10:
                    return self.aStarSearch(gameState, nearestFoodToEat, self.avoidOpponentDefenderHeuristic)

        # when to search for the nearest capsule
        if nearestCapsule != None and len(self.getDirectlyAvailableFoodToEat(gameState)) == 0:
            if len(defenders) != 0:
                for defender in defenders:
                    if self.isOpponentDefenderFinishScare(defender) or \
                            self.getMazeDistance(defender.getPosition(), nearestCapsule) < 2:
                        return self.aStarSearch(gameState, nearestMiddleLine, self.avoidOpponentDefenderHeuristic)
                return self.aStarSearch(gameState, nearestCapsule, self.avoidOpponentDefenderHeuristic)

        # guarantee the food carried to be returned
        if len(self.getFood(gameState).asList()) == 0 or \
                (nearestCapsule == None and gameState.getAgentState(self.index).numCarrying != 0 and len(defenders) != 0):
            return self.aStarSearch(gameState, nearestMiddleLine, self.avoidOpponentDefenderHeuristic)

        # normally search for the nearest food
        return self.aStarSearch(gameState, nearestFoodToEat, self.avoidOpponentDefenderHeuristic)

class DefensiveReflexAgent(ReflexCaptureAgent):

    def setNumFoodToDefend(self, gameState, opponent):
        if self.getPreviousObservation() != None and \
                gameState.getAgentState(opponent).numReturned > self.getPreviousObservation().getAgentState(opponent).numReturned:
            self.numFoodToDefend -= (gameState.getAgentState(opponent).numReturned - self.getPreviousObservation().getAgentState(opponent).numReturned)

    def chooseAction(self, gameState):

        attackers = self.getOpponentAttackers(gameState)
        nearestAttacker = self.getNearestOpponentAttacker(gameState)
        nearestMiddleLine = self.getNearestMiddleLine(gameState)
        nearestFoodToDefend = self.getNearestFoodToDefend(gameState)

        # set number of food to defend
        for o in self.getOpponents(gameState):
            self.setNumFoodToDefend(gameState, o)

        # guarantee my defender not to become an attacker
        if gameState.getAgentState(self.index).getPosition() == nearestMiddleLine:
            return self.aStarSearch(gameState, self.home, self.nullHeuristic)

        # when to search for the nearest food to defend
        if gameState.getAgentState(self.index).getPosition() == self.nearestEatenFood:
            if nearestFoodToDefend != None:
                return self.aStarSearch(gameState, nearestFoodToDefend, self.nullHeuristic)

        # when to escape
        if gameState.getAgentState(self.index).scaredTimer > 0:
            if len(attackers) != 0:
                for attacker in attackers:
                    if self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), attacker.getPosition()) < 3:
                        return self.aStarSearch(gameState, self.home, self.avoidOpponentAttackerHeuristic)

        # when to search for the nearest attacker
        if len(attackers) != 0:
            if nearestAttacker != None:
                return self.aStarSearch(gameState, nearestAttacker.getPosition(), self.nullHeuristic)

        # when to search for the nearest eaten food
        if len(self.getFoodYouAreDefending(self.getCurrentObservation()).asList()) < self.numFoodToDefend:
            if self.getPreviousObservation() != None and len(self.getFoodYouAreDefending(self.getCurrentObservation()).asList()) < \
                    len(self.getFoodYouAreDefending(self.getPreviousObservation()).asList()):
                self.nearestEatenFood = self.getNearestEatenFood(gameState)
                return self.aStarSearch(gameState, self.nearestEatenFood, self.nullHeuristic)
            return self.aStarSearch(gameState, self.nearestEatenFood, self.nullHeuristic)

        # normally return to the nearest middle line
        return self.aStarSearch(gameState, nearestMiddleLine, self.nullHeuristic)