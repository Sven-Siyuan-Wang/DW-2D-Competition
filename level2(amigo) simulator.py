import math
import libdw.util as util
import libdw.sm as sm
import libdw.gfx as gfx
from soar.io import io
import libdw.sonarDist as sonarDist
import urllib2
import time

class MySMClass(sm.SM):
    align=0.75
    prevLoc='S'
    nextLoc='X'
    #right=1
    #left=0
    #startState=[state,delay,distance from wall, [prev, next], junction tracker]
    startState=[1,0,align,[prevLoc,nextLoc],0]
    jump=0
    order=[]
    for line in urllib2.urlopen("http://people.sutd.edu.sg/~oka_kurniawan/10_009/y2015/2d/tests/level2_1.inp"):
        order+=[line.split()[0]]*((int(line.split()[1])/6)+(1 if int(line.split()[1])%6 else 0))
    
    #level 2 junctions and turnings
    junction={\
    'AX':['left','left'],\
    'BX':['straight','left'],\
    'CX':['straight','left','straight'],\
    'DX':['right','left','straight'],\
    'XA':['right','right'],\
    'XB':['right','straight'],\
    'XC':['straight','right','straight'],\
    'XD':['straight','right','left'],\
    'SX':['straight','straight']}
    #level 1 junctions and turnings
    route={'AX':'left','BX':'straight','CX':'right','XA':'right','XB':'straight','XC':'left'}
    
    def log(self):
        end=False
        if self.state[3][0]=='S':
            self.outfile=open('log.txt','w')
        location=self.state[3][1]
        date=time.strftime("%d/%m/%Y")
        ctime=time.strftime("%H:%M:%S")
        if location!='X':
            action='Expose Plates at '+location
        
        elif not self.order:
            action='Finished, and arrived at X'
            end=True
            
            
        else:
            action='Collect Plates at '+location
        
        self.outfile.write('<'+ctime+'>||<'+date+'>||'+action+'\n')
        if end:
            self.outfile.close()
                        
        return
    def sensors(self,inp):
        return inp.sonars[0],inp.sonars[2],inp.sonars[3],inp.sonars[5]
    def getNextValues(self, state, inp):
        print 'Current state: ', state[0],' Delay: ',state[1],' Route:', state[3][0]+state[3][1], ' Junction:', state[4]
        left,front1,front2,right=self.sensors(inp)
        ##move forward
        if state[0]==1:
               
            print 'Wall follower'
            
            pright=sonarDist.getDistanceRight(inp.sonars)

            if round(front1,2)<0.5 or round(front2,2)<0.5:     #end of the alley    
                z=io.Action(fvel=0,rvel=0)
                #print 'stop'
                self.log()
                state[0]=3
                return state, z
            elif round(right,2)>1 and round(front1,2)>1 or round(left,2)>1 and round(front1,2)>1: # a new junction
                z=io.Action(fvel=0,rvel=0)
                print 'state 1 if'
                state[0]=5
                return state, z    
            else:       # keep moving
                fvel=0.2             
                a=self.align-round(pright,2)
                b=self.align-state[2]
                #rvel=k1*a+k2*b
                rvel=30*a+(-29.77)*b
                z=io.Action(fvel,rvel)
                print 'rvel', rvel
                print 'pright', pright
                state[2]=round(pright,2)
                return state, z
                #z=io.Action(fvel=0.2,rvel=0)
                ##print 'move'
                #return state, z
                
        ##rotate 180 degree at exposure
        if state[0]==2:
            print 'state 2 rotate 180'
            
            
            #if junction counter= len(junction[path])
            #swap destination and source
            
            if state[1]<=40:
                z=io.Action(fvel=0,rvel=(math.pi)/4)
                print 'rotate left'
                state[1]+=1
                return state, z
            #
            else:
                state[1]=0
                z=io.Action(fvel=0,rvel=0)
                print 'stop after turning'
                #set junction counter =0
                state[4]=0
                    #check if exposure area or collection area
                    #destination is either A,B,C,D
                if state[3][1]!='X':
                        state[0]=1
                        #swap prev and next
                        print 'Before swap',state[3][0],state[3][1]
                        state[3][0],state[3][1]=state[3][1],state[3][0]
                        print 'After swap',state[3][0],state[3][1]
                        print 'Exposure area'
                        pass
                elif not self.order:
                        state[0]=10 
                else:
                        state[0]=1
                        state[3][1]=self.order.pop(0)
                        state[3][0]='X'
                        print 'Collection area'
                                        
                return state,z
            
        #wait for 15 seconds
        if state[0]==3:
            print 'wait for 15 seconds'
            #if state[1]<=150:
            if state[1]<=10:
                z=io.Action(fvel=0,rvel=0)
                print 'waiting for ', state[1]/10 , 'seconds'
                state[1]+=1
                return state, z
            else:
                state[1]=0
                z=io.Action(fvel=0,rvel=0)
                print 'stop after turning'
                state[0]=2
                return state,z
                
        #proceed till junction
        #proportional controller after junction
    
                
        #at junction proceed till center of junction
        if state[0]==5:
            print 'state 5'
            print self.junction[state[3][0]+state[3][1]][state[4]-1]
            if state[1]<=15:
                z=io.Action(fvel=0.5,rvel=0)
                print 'waiting for ', state[1]/10 , 'seconds'
                state[1]+=1
                return state, z
            else:
                state[1]=0
                z=io.Action(fvel=0,rvel=0)
                
                #increase junction counter
                
                print 'stopped and ready to turn'
                print 'prev:',state[3][0]
                print 'next:',state[3][1]
                print 'junction:',self.junction[state[3][0]+state[3][1]]
                
                if self.junction[state[3][0]+state[3][1]][state[4]]=='right':
                    state[0]=6
                elif self.junction[state[3][0]+state[3][1]][state[4]]=='left':
                    state[0]=7
                elif self.junction[state[3][0]+state[3][1]][state[4]]=='straight':
                    state[0]=8
                else:
                     pass
                state[4]+=1
                return state, z
                
        #turn right
        if state[0]==6:
            print 'state 6'
            if state[1]<=20:
                z=io.Action(fvel=0,rvel=-(math.pi)/4)
                print 'rotate right'
                state[1]+=1
                return state, z
            #
            else:
                state[1]=0
                z=io.Action(fvel=0,rvel=0)
                print 'stop after turning'
                state[0]=8
                return state,z
                
        #turn left  
        if state[0]==7:
            print 'state 7'
            if state[1]<=20:
                z=io.Action(fvel=0,rvel=(math.pi)/4)
                print 'rotate left'
                state[1]+=1
                return state, z
            #
            else:
                state[1]=0
                z=io.Action(fvel=0,rvel=0)
                print 'stop after turning'
                state[0]=8
                return state,z 
                
        #exiting junction
        if state[0]==8: 
            print 'state 8'    
            if state[1]<=20:
                z=io.Action(fvel=0.5,rvel=0)
                print 'exiting junction for ', state[1]/10 , 'seconds'
                state[1]+=1
                return state, z
            else:
                state[1]=0
                z=io.Action(fvel=0.2,rvel=0)
                print 'entered alley'
                state[0]=1
                return state, z
                

                
        if state[0]==10:
            z=io.Action(fvel=0,rvel=0)
            print 'YAY!!!WOOHOOO!!! Task Completed Successfully!!!'
            return state, z
                
                
            

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
