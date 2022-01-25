import os
import sys
import time
import pytz
import datetime
from random import randrange
import pandas as pd

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci


def getDateTime():
    utc_now = pytz.utc.localize(datetime.datetime.utcnow())
    currentDT = utc_now.astimezone(pytz.timezone("Turkey"))
    DATIME = currentDT.strftime("%Y-%m-%d %H:%M:%S")
    return DATIME


def flattenList(_2d_list):
    flat_list = []
    for element in _2d_list:
        if type(element) is list:
            for item in element:
                flat_list.append(item)
        else:
            flat_list.append(element)
    return flat_list


sumoCmd = ["sumo", "-c", "map2.sumocfg"]
traci.start(sumoCmd)
packVehicleData = []
packTLSData = []
packBigData = []
vehicles = traci.vehicle.getIDList()
idd = []
tlsList = []
vehicleList = []
trafficLights = traci.trafficlight.getIDList()

def getVehicleData():
    for i in range(0, len(vehicles)):
        vehicleID = vehicles[i]
        x, y = traci.vehicle.getPosition(vehicleID)
        coord = [x, y]
        lon, lat = traci.simulation.convertGeo(x, y)
        gpscoord = [lon, lat]
        spd = round(traci.vehicle.getSpeed(vehicleID)*3.6, 2)
        edge = traci.vehicle.getRoadID(vehicleID)
        lane = traci.vehicle.getLaneID(vehicleID)
        displacement = round(traci.vehicle.getDistance(vehicleID), 2)
        turnAngle = round(traci.vehicle.getAngle(vehicleID), 2)
        nextTLS = traci.vehicle.getNextTLS(vehicleID)
        vehicleList = [getDateTime(), vehicleID, coord, gpscoord,
                    spd, edge, lane, displacement, turnAngle, nextTLS]
        print("Vehicle: ", vehicleID, " at datetime: ", getDateTime())
        print(vehicleID, " >>> Position: ", coord, " | GPS Position: ", gpscoord, " |",
            " Speed: ", round(traci.vehicle.getSpeed(vehicleID)*3.6, 2), "km/h |", \
            # Returns the id of the edge the named vehicle was at within the last step.
            " EdgeID of veh: ", traci.vehicle.getRoadID(vehicleID), " |", \
            # Returns the id of the lane the named vehicle was at within the last step.
            " LaneID of veh: ", traci.vehicle.getLaneID(vehicleID), " |", \
            # Returns the distance to the starting point like an odometer.
            " Distance: ", round(traci.vehicle.getDistance(vehicleID), 2), "m |", \
            # Returns the angle in degrees of the named vehicle within the last step.
            " Vehicle orientation: ", round(traci.vehicle.getAngle(vehicleID), 2), "deg |", \
            # Return list of upcoming traffic lights [(tlsID, tlsIndex, distance, state), ...]
            " Upcoming traffic lights: ", traci.vehicle.getNextTLS(vehicleID), \
            )
        idd = traci.vehicle.getLaneID(vehicleID)


def gettrafficLightsLData():
    for k in range(0, len(trafficLights)):
        if idd in traci.trafficlight.getControlledLanes(trafficLights[k]):
                tflight = trafficLights[k]
                tl_state = traci.trafficlight.getRedYellowGreenState(trafficLights[k])
                tl_phase_duration = traci.trafficlight.getPhaseDuration(trafficLights[k])
                tl_lanes_controlled = traci.trafficlight.getControlledLanes(trafficLights[k])
                tl_program = traci.trafficlight.getCompleteRedYellowGreenDefinition(trafficLights[k])
                tl_next_switch = traci.trafficlight.getNextSwitch(trafficLights[k])
                tlsList = [tflight, tl_state, tl_phase_duration, tl_lanes_controlled, tl_program, tl_next_switch]
                
                print(trafficLights[k], " --->", \
                      #Returns the named tl's state as a tuple of light definitions from rRgGyYoO, for red,
                      #green, yellow, off, where lower case letters mean that the stream has to decelerate
                        " TL state: ", traci.trafficlight.getRedYellowGreenState(trafficLights[k]), " |" \
                      #Returns the default total duration of the currently active phase in seconds; To obtain the
                      #remaining duration use (getNextSwitch() - simulation.getTime()); to obtain the spent duration
                      #subtract the remaining from the total duration
                        " TLS phase duration: ", traci.trafficlight.getPhaseDuration(trafficLights[k]), " |" \
                      #Returns the list of lanes which are controlled by the named traffic light. Returns at least
                      #one entry for every element of the phase state (signal index)                                
                        " Lanes controlled: ", traci.trafficlight.getControlledLanes(trafficLights[k]), " |", \
                      #Returns the complete traffic light program, structure described under data types                                      
                        " TLS Program: ", traci.trafficlight.getCompleteRedYellowGreenDefinition(trafficLights[k]), " |"
                      #Returns the assumed time (in seconds) at which the tls changes the phase. Please note that
                      #the time to switch is not relative to current simulation step (the result returned by the query
                      #will be absolute time, counting from simulation to);
                      #start obtain relative time, one needs to subtract current simulation time from the
                      #result returned by this query. Please also note that the time may vary in the case of
                      #actuated/adaptive traffic lights
                        " Next TLS switch: ", traci.trafficlight.getNextSwitch(trafficLights[k]))
def packData():
    packBigDataLine = flattenList([vehicleList, tlsList])
    packBigData.append(packBigDataLine)

def getData():
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        getVehicleData()
        gettrafficLightsLData()
        packData()
         
# Generate Excel file
def getDataExcel():
    columnnames = ['dateandtime', 'vehid', 'coord', 'gpscoord', 'spd', 'edge', 'lane', 'displacement', 'turnAngle', 'nextTLS',
                   'tflight', 'tl_state', 'tl_phase_duration', 'tl_lanes_controlled', 'tl_program', 'tl_next_switch']
    dataset = pd.DataFrame(packBigData, index=None, columns=columnnames)
    dataset.to_excel("output.xlsx", index=False)
    time.sleep(5)

getData()
getDataExcel()
