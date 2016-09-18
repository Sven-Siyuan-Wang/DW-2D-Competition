# -*- coding: utf-8 -*-
#wsy
import math
import libdw.util as util
import libdw.sm as sm
import libdw.gfx as gfx
from soar.io import io
import libdw.sonarDist as sonarDist
import urllib2
import time
class MySMClass(sm.SM):
    align=0.7
    leftAlign=0.4
    rightAlign=0.5
    prevLoc='S'
    nextLoc='X'
    forwardVel=0.3
    #right=1
    #left=0
    #startState=[state,delay,distance from wall, [prev, next], junction tracker,obstacle tracker,delay for junction detection]
    startState=[1,0,align,[prevLoc,nextLoc],0,0,0]
    
    
#########################
# PATH OPTIMISATION     # 
#########################   
    tasks={'A':3,'B':0,'C':3,'D':0} 
    #for line in urllib2.urlopen("http://people.sutd.edu.sg/~oka_kurniawan/10_009/y2015/2d/tests/level3_1.inp"):
    #       tasks[line.split()[0]]=int(line.split()[1])
    bot=[]
    leftover=''
    l=['A','B','C','D']
    for site in l:
        if tasks[site]>=6:
            count=tasks[site]/6
            bot.extend([site]*count)        
            tasks[site]%=6
        
    sum4=0
    done4=False
    
    #print tasks
    #FOUR
    for a in tasks.values():
        if a==0:
            sum4=10
            break
        else:
            sum4+=a
    if sum4<=6:
        leftover='ABCD'
        bot.append(leftover)
        for i in l:
            tasks[i]=0
        done4=True
    
    #print 'after 4 check',tasks
    #Check for 'AB','CD' case
    if all(i>0 for i in tasks.itervalues()) and not done4:   #tasks['A']>0 and tasks['B']>0 and tasks['C']>0 and tasks['D']>0:
        print tasks['B']
        if tasks['A']+tasks['B']<=6 and tasks['C']+tasks['D']<=6:
            bot.append('AB')
            bot.append('CD')
            done4=True
            for i in l:
                tasks[i]=0 
        
    
    #THREE destinations 
    done3=False
    if not done4:
        cases=['ABC','ABD','ACD','BCD']
        for i in cases:
            sum3=0
            for j in i:
                if tasks[j]==0:
                    sum3=10
                    
                else:
                    sum3+=tasks[j]
            if sum3<=6:
                print 'sum3<=6'
                leftover+=i
                bot.append(leftover)
                leftover=''
                done3=True
                for j in i:
                    tasks[j]=0
                break
    #print 'after 3 check',tasks
    
    #Check for double destinations
    if not done3 and not done4:
        for i in range(3):
            if tasks[l[i]]>0:
                print 'passed'
                for j in range (i+1,4):
                    if tasks[l[i]]+tasks[l[j]]<=6 and tasks[l[j]]>0 and tasks[l[i]]>0:
                        leftover=l[i]+l[j]
                        print leftover
                        bot.append(leftover)
                        tasks[l[i]]=0
                        tasks[l[j]]=0
    # Check for single desitinations left
    if not done4:
        for i in l:
            if tasks[i]>0:
                bot.append(i)
                tasks[i]=0
    print bot
    order='X'.join(bot)
    order=list(order+'X')
    print order
############################
# End of PATH OPTIMISATION # 
############################  
    
    #level 3 junctions and turnings
    junction={\
    'AX':['left','left'],\
    'BX':['straight','left'],\
    'CX':['straight','left','straight'],\
    'DX':['right','left','straight'],\
    'XA':['right','right'],\
    'XB':['right','straight'],\
    'XC':['straight','right','straight'],\
    'XD':['straight','right','left'],\
    'SX':['straight','straight'],\
    'AB':['right'],\
    'AC':['straight','right'],\
    'AD':['straight','straight'],\
    'BC':['right','right'],\
    'BD':['right','straight'],\
    'CD':['right']\
    }
    
   
    def sensors(self,inp):
        return inp.sonars[0],inp.sonars[1],inp.sonars[2],inp.sonars[3],inp.sonars[4],inp.sonars[5]
    def getNextValues(self, state, inp):
        left,fleft,front1,front2,fright,right=self.sensors(inp)
        pright=sonarDist.getDistanceRight(inp.sonars)
        print
        print 'Current state: ', state[0],' Delay: ',state[1],' Route:', state[3][0]+state[3][1], ' Junction:', state[4]
        print 'Front1,Front2:',front1,front2,'fleft,fright:',fleft,fright,'left,right:',left,right   
        print 'Wall follow delay: ',state[6]
         
        ##wall follow
        if state[0]==1:
            
            

            if round(front1,2)<0.6 and round(front2,2)<0.6: #end of the alley    
                z=io.Action(fvel=0,rvel=0)            
                state[0]=3
                state[6]=0   # clear wall follower timer
                print 'end of alley'
                
                return state, z
            elif round(right,2)>1.2 and round(front1,2)>1 or round(left,2)>1.2 and round(front1,2)>1: # a new junction
                z=io.Action(fvel=0,rvel=0)
                print 'a new junction'
                print left,right
                state[0]=5
                return state, z
            elif front2<0.8 and fright<0.9 and front1>1.5 and fleft>0.7:# obstacle on the right
                print 'front2,fright',(front2,fright)
                
                z=io.Action(fvel=0,rvel=math.pi/4)
                state[0]=9      # go to 45 degrees left state
                
                return state,z
             
            elif front1<0.8 and fleft<0.9 and front2>1.5 and fright>0.7: # obstacle detected on the left
                print 'fleft,front1',(fleft,front1)
                z=io.Action(fvel=0,rvel=-math.pi/4)
                state[0]=10
                state[5]=1      # obstacle tracker
                
                return state,z
                

            elif front1<1 and front2<1:    # Slow down when entering station
                print 'Slowing down...' 
                front=(front1+front2)/2
                print 'front:',front, 'fvel:',2*(front-0.5)
                 # max=0.5m/s
		z=io.Action(fvel=1*(front-0.5),rvel=0)
		return state,z
  #          elif front1<=1:            # Slow down when approaching obstacle on the left
  #              print 'Slowing down'
  #              fvel=1*(front1-0.5)
  #              a=self.align-round(pright,2)
  #              b=self.align-state[2]
  #              #rvel=k1*a+k2*b
  #              rvel=30*a+(-29.77)*b
  #              z=io.Action(fvel,rvel)
  #              print 'rvel', rvel
  #              print 'pright', pright
  #              state[2]=round(pright,2)
  #              return state,z
            elif front2>1 and fright<1.9 and fleft<1.9 and right>0.3:       #wall following
                fvel=self.forwardVel             
                a=self.align-round(pright,2)
                b=self.align-state[2]
                #rvel=k1*a+k2*b
                rvel=30*a+(-29.77)*b
                if rvel>0.5:
                    rvel=0.5
                if rvel<-0.5:
                    rvel=-0.5
                    
                z=io.Action(fvel,rvel)
                print 'rvel', rvel
                print 'pright', pright
                state[2]=round(pright,2)
                return state, z
            #elif front2<=1:       # slow down obstacle on the right
            #    print 'PRight disabled'
            #    print 'Slowing down'                
            #    z=io.Action(fvel=1*(front2-0.5),rvel=0)
            #    return state, z
            
                
            else:                  #approaching a new junction
                print 'frontleft,frontright:',fleft,fright
                z=io.Action(fvel=0.35,rvel=0)
                print 'ELSE'
                return state, z 
                
        ##rotate 180 degree at exposure
        if state[0]==2:
            print 'state 2 rotate 180'
           
            
            #if junction counter= len(junction[path])
            #swap destination and source
            
            if state[1]<=32:
                z=io.Action(fvel=0,rvel=1)
                print 'rot ate left'
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
                if not self.order:
                    state[0]=4
                else:
                    state[0]=1
                    state[3][0]=state[3][1]  #prev=next
                    state[3][1]=self.order.pop(0) #next=new destination
                                    
                return state,z
            
        #wait for 15 seconds
        if state[0]==3:
            print 'wait for 15 seconds'
            #if state[1]<=150:
            if state[1]<=10:
                z=io.Action(fvel=0,rvel=0)
                state[1]+=1
                return state, z
            else:
                state[1]=0
                z=io.Action(fvel=0,rvel=0)
                print 'stop after turning'
                state[0]=2
                return state,z
        if state[0]==5:
            print 'state 5'
            print self.junction[state[3][0]+state[3][1]][state[4]-1]
            if state[1]<=25:
                if round(right,2)<1 and round(left,2)<1:
                    state[0]=1
                    state[1]=0
                    z=io.Action(fvel=0.5,rvel=0)
                    print 'wall detected in state 5'
                else:
                    z=io.Action(fvel=0.3,rvel=0)
                    print 'waiting for ', float(state[1])/10 , 'seconds'
                    state[1]+=1
                return state, z
            
            else:
                state[1]=0
                z=io.Action(fvel=0.3,rvel=0)
                
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
            if state[1]<=20:  # 29
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
            if state[1]<=60:
                if round(right,2)<1.1 and round(left,2)<1.1 and state[1]>3: # left and right sensors sometimes not accurate
                    state[0]=1
                    state[1]=0
                    z=io.Action(fvel=0.4,rvel=0)
                    print 'wall detected in state 8'
                else:
                    z=io.Action(fvel=0.4,rvel=0)
                    print 'exiting junction for ', state[1]/10 , 'seconds'
                    state[1]+=1
                return state, z
            else:
                state[1]=0
                z=io.Action(fvel=0.4,rvel=0)
                print 'entered alley'
                state[0]=1
                return state, z 
            
        if state[0]==9: #45 left
            if state[1]<=8:
                z=io.Action(fvel=0,rvel=0.5)
                print 'rotate left'
                state[1]+=1
                return state, z
            else:
                state[1]=0
                z=io.Action(fvel=0.4,rvel=0)
                print 'stop turning'
                state[0]=11
                return state,z 
       
        if state[0]==10: #45 right
            if state[1]<=8:
                z=io.Action(fvel=0,rvel=-0.5)
                print 'rotate right'
                state[1]+=1
                return state, z
            
            else:
                state[1]=0
                z=io.Action(fvel=0.4,rvel=0)
                print 'stop turning'
                state[0]=17
                return state,z 
                
        if state[0]==11: # left1
            
            if state[1]<=12:
                z=io.Action(fvel=0.4,rvel=0)
                state[1]+=1
                return state, z
            else:
                z=io.Action(fvel=0,rvel=-0.5)
                state[1]=0
                state[0]=12
                return state,z
        if state[0]==12: #left2
            if state[1]<=8:  #7
                z=io.Action(fvel=0,rvel=-0.5)
                print 'rotate right'
                state[1]+=1
                return state, z
            
            else:
                state[1]=0
                z=io.Action(fvel=0.4,rvel=0)             
                state[0]=13
                return state,z 
        if state[0]==13: # left3
            print 'right:',right
            if round(right,2)>1.2 and round(front1,2)>1 or round(left,2)>1.2 and round(front1,2)>1: # a new junction
                z=io.Action(fvel=0,rvel=0)
                print 'a new junction'
                print left,right
                state[0]=5
                state[1]=0
                return state, z
            elif state[1]>20 and right>0.6:
                print 'Bypassed obstacle!'
                z=io.Action(fvel=0,rvel=-0.5)
                state[1]=0
                state[0]=14
                return state,z
                
            else:
                #if state[1]==0:
                #    state[2]=self.leftAlign             
                #a=round(left,2)-self.leftAlign  
                #b=state[2]-self.leftAlign  
                ##rvel=k1*a+k2*b
                #
                #z=io.Action(fvel=0.3,rvel=50*a+(-49)*b)
                #
                #print 'rvel', 50*a+(-49)*b  
                #print 'Aligning to the left'            
                #state[2]=round(left,2)
                z=io.Action(fvel=0.3,rvel=0)
                state[1]+=1
                return state,z
        if state[0]==14: #left4
            if round(right,2)>1.2 and round(front1,2)>1 or round(left,2)>1.2 and round(front1,2)>1: # a new junction
                z=io.Action(fvel=0,rvel=0)
                print 'a new junction'
                print left,right
                state[0]=5
                state[1]=0
                return state, z
            elif state[1]<=8:  # last value 10
                z=io.Action(fvel=0,rvel=-0.5)
                print 'rotate right'
                state[1]+=1
                return state, z
            
            else:
                state[1]=0
                z=io.Action(fvel=0.4,rvel=0)             
                state[0]=15
                return state,z
        if state[0]==15: # left5
            
            
            if state[1]<=12: #last value 10，8
                z=io.Action(fvel=0.4,rvel=0)
                state[1]+=1
                return state, z
            else:
                z=io.Action(fvel=0,rvel=0.5)
                state[1]=0
                state[0]=16
                return state,z
        if state[0]==16: #left6
            if state[1]<=8:    #10,9
                z=io.Action(fvel=0,rvel=0.5)
                print 'rotate left'
                state[1]+=1
                return state, z
            else:
                state[1]=0
                z=io.Action(fvel=1,rvel=0)
                state[0]=1
                return state,z 
                
        if state[0]==17: # right1
            
            if state[1]<=12:
                z=io.Action(fvel=0.4,rvel=0)
                state[1]+=1
                return state, z
            else:
                z=io.Action(fvel=0,rvel=0.5)
                state[1]=0
                state[0]=18
                return state,z
        if state[0]==18: #right2
            if state[1]<=8: #7
                z=io.Action(fvel=0,rvel=0.5)
                
                state[1]+=1
                return state, z
            
            else:
                state[1]=0
                z=io.Action(fvel=0.4,rvel=0)             
                state[0]=19
                return state,z 
        if state[0]==19: #right3
            print 'left:',left
            if round(right,2)>1.2 and round(front1,2)>1 or round(left,2)>1.2 and round(front1,2)>1: # a new junction
                z=io.Action(fvel=0,rvel=0)
                print 'a new junction'
                print left,right
                state[0]=5
                state[1]=0
                return state, z
            elif left>0.6 and state[1]>20:
                z=io.Action(fvel=0,rvel=0.5)
                state[1]=0
                state[0]=20
                return state,z
                
            else:
                #if state[1]==0:
                #    state[2]=self.rightAlign
                #a=self.rightAlign-round(pright,2)
                #b=self.rightAlign-state[2]
                #print 'Aligning to the right'
                ##rvel=k1*a+k2*b
                #
                #z=io.Action(fvel=0.3,rvel=50*a+(-49)*b)
                #
                #print 'rvel', 50*a+(-49)*b           
                #state[2]=round(pright,2)
                z=io.Action(fvel=0.3,rvel=0)
                state[1]+=1
                return state,z 
        if state[0]==20: #right4
            if round(right,2)>1.2 and round(front1,2)>1 or round(left,2)>1.2 and round(front1,2)>1: # a new junction
                z=io.Action(fvel=0,rvel=0)
                print 'a new junction'
                print left,right
                state[0]=5
                state[1]=0
                return state, z
            elif state[1]<=8:
                z=io.Action(fvel=0,rvel=0.5)
                state[1]+=1
                return state, z
            
            else:
                state[1]=0
                z=io.Action(fvel=0.4,rvel=0)             
                state[0]=21
                return state,z
        if state[0]==21: # right5
            
            
            if state[1]<=12:
                z=io.Action(fvel=0.4,rvel=0)
                state[1]+=1
                return state, z
            else:
                z=io.Action(fvel=0,rvel=-0.5)
                state[1]=0
                state[0]=22
                return state,z
        if state[0]==22: #right6
             if state[1]<=8:
                z=io.Action(fvel=0,rvel=-0.5)
                state[1]+=1
                return state, z
             else:
                state[1]=0
                z=io.Action(fvel=1,rvel=0)
                state[0]=1
                return state,z 
        #if state[0]==23:
        #    if state[1]<=10:
        #        z=io.Action(fvel=1,rvel=0)
        #        state[1]+=1
        #        print 'Accelarating...'
        #    else:
        #        print 'A new junction'                        
        #        z=io.Action(fvel=1,rvel=0)
        #        print 'prev:',state[3][0]
        #        print 'next:',state[3][1]
        #        print 'junction:',self.junction[state[3][0]+state[3][1]]
        #        
        #        if self.junction[state[3][0]+state[3][1]][state[4]]=='right':
        #            state[0]=6
        #        elif self.junction[state[3][0]+state[3][1]][state[4]]=='left':
        #            state[0]=7
        #        elif self.junction[state[3][0]+state[3][1]][state[4]]=='straight':
        #            state[0]=5
        #        else:
        #             pass
        #        state[4]+=1
        #        state[1]=0
        #        state[6]+=20
        #    return state, z
                
        
        
                
                
                
        if state[0]==4:
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
        
    
        
    
        