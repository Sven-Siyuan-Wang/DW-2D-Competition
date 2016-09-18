import math
import libdw.util as util
import libdw.sm as sm
import libdw.gfx as gfx
from soar.io import io
import libdw.sonarDist as sonarDist
import urllib2
import time

class MySMClass(sm.SM):
    
    startState=1
   
    
    def sensors(self,inp):
        return inp.sonars[0],inp.sonars[2],inp.sonars[3],inp.sonars[5]
    def getNextValues(self, state, inp):
        left,fleft,front1,front2,fright,right=inp.sonars[0],inp.sonars[1],inp.sonars[2],inp.sonars[3],inp.sonars[4],inp.sonars[5]
        pright=sonarDist.getDistanceRight(inp.sonars)
        print 'left,right:',left,right
        print 'fleft,fright:',fleft,fright
        print 'front1,front2:',front1,front2
        print 'PRight:',pright
        print
        z=io.Action(fvel=0,rvel=0)
        return state,z

                
        
                
            

mySM = MySMClass()
mySM.name = 'brainSM'


######################################################################
###
###          Brain methods
###
######################################################################

def plotSonar(sonarNum):
    robot.gfx.addDynamicPlotFunction(y=('sonar'+str(sonarNum),
                                        lambda: 
                                        io.SensorInput().sonars[sonarNum]))

# this function is called when the brain is (re)loaded
def setup():
    robot.gfx = gfx.RobotGraphics(drawSlimeTrail=True, # slime trails
                                  sonarMonitor=False) # sonar monitor widget
    
    # set robot's behavior
    robot.behavior = mySM

# this function is called when the start button is pushed
def brainStart():
    robot.behavior.start(traceTasks = robot.gfx.tasks())

# this function is called 10 times per second
def step():
    inp = io.SensorInput()
    robot.behavior.step(inp).execute()
    io.done(robot.behavior.isDone())

# called when the stop button is pushed
def brainStop():
    pass

# called when brain or world is reloaded (before setup)
def shutdown():
    pass
