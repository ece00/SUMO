from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import optparse
import random

from pandas import Period, period_range

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary
import traci

totalVehicleNumber = 200   
maxStep = 900

routesDirect = [["E0","-E1"],["E0","-E3"],
                ["E1","-E0"],["E1","-E3"],
                ["E3","-E0"],["E3","-E1"],
                ["-E4","E5"],["-E4","E6"],
                ["-E5","E4"],["-E5","E6"],
                ["-E6","E4"],["-E6","E5"]]
routesWithVia = [["E0","E4","-E2"], ["E0","E5","-E2"],["E0","E6","-E2"],
                 ["E1","E4","-E2"], ["E0","E5","-E2"],["E0","E6","-E2"],
                 ["E3","E4","-E2"], ["E3","E5","-E2"],["E3","E6","-E2"],
                 ["-E4","-E0","E2"],["-E4","-E1","E2"],["-E4","-E3","E2"], 
                 ["-E5","-E0","E2"],["-E5","-E1","E2"],["-E5","-E3","E2"],
                 ["-E6","-E0","E2"],["-E6","-E1","E2"],["-E6","-E3","E2"]]

def generate_routefile():
    with open("map2.rou.xml", "w") as routes:
        with open("rou.txt","r") as rou:
            for i in rou:
                print(i,file=routes)
            rou.close()
        vehicleID = 0
        vehicleEnteranceRange = 10
        random.seed(0)
        while(vehicleID<totalVehicleNumber): 
            departTime = random.randint(vehicleEnteranceRange-10,vehicleEnteranceRange)
            directVia = random.randint(0,1) # if via then 0 if direct then 1
            if (directVia==0):
                routeArr = random.randint(0,len(routesWithVia)-1)
                fromEdge = routesWithVia[routeArr][0]
                toEdge = routesWithVia[routeArr][1]
                viaEdge = routesWithVia[routeArr][2]
                print('    <trip id="vehicle_%i" depart="%i" from="%s" to="%s" via="%s"/>' 
                                %(vehicleID, departTime, fromEdge,toEdge,viaEdge), file=routes)
            else:
                routeArr = random.randint(0,len(routesDirect)-1)
                fromEdge = routesDirect[routeArr][0]
                toEdge = routesDirect[routeArr][1]
                print('    <trip id="vehicle_%i" depart="%i" from="%s" to="%s" />' 
                                %(vehicleID, departTime, fromEdge, toEdge), file=routes)
            vehicleID += 1
            vehicleEnteranceRange += 10
        print("</routes>", file=routes)
        routes.close()    


TLConfigs= ["GGGrrrrrrrrr","rrrGGGrrrrrr","rrrrrrGGGrrr","rrrrrrrrrGGG"]

def traffic_lights():
    step = 0
    period = 25
    configID = 0
    while(step<maxStep):
        for step in range(period-25, period):
            traci.simulationStep()
            traci.trafficlight.setRedYellowGreenState("J1", TLConfigs[(configID%4)])
            traci.trafficlight.setRedYellowGreenState("J3", TLConfigs[(configID+1)%4])
            step += 1
        period += 25
        configID += 1

if __name__ == "__main__":
    generate_routefile()
    sumoBinary = checkBinary('sumo-gui')
    sumoCmd = [sumoBinary, "-c", "map2.sumocfg"]
    traci.start(sumoCmd)
    traffic_lights()
    traci.close()
