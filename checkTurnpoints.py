# -*- coding: utf-8 -*-
"""
Created on Tue Jun 14 23:12:05 2016

@author: Antti Rantala
"""

import sys, os, math
from scipy.spatial import KDTree

def parseFlight(file):
    accuracy = 0
    points = []
    try:
        if isinstance(file, str):
            file = open(file)
        for line in file:
            if line[0] == 'B':
                n = int(line[7:9])+float(line[9:14])/60000.0
                e = int(line[15:18]) + float(line[18:23])/60000.0
                points.append((n,e))
                continue
            elif line[:5] == 'HFFXA':
                accuracy = int(line[5:8])
    except IOError as e:
        print('Trouble with the file')
        print(e)
    except ValueError as e:
        print('Broken file')
        print(e)
    finally:
        file.close()
    return points, accuracy
    
def parseDirectory(directory):
    _,_, files = next(os.walk(directory))
    files = [f for f in files if f[-3:] == 'igc']
    points = []
    acc=0
    for filename in files:
        p,a = parseFlight(directory+filename)
        points += p
        acc = max(a,acc)
    return points, acc
    
def parseTurnpoints(file):
    points = []
    names = []
    try:
        if isinstance(file, str):
            file = open(file)
        file.readline()
        for line in file:
            parts = line.split(',')
            if len(parts) < 5:
                continue
            n = float(parts[3][:2])+float(parts[3][2:5])/60.0
            e = float(parts[4][:3])+float(parts[4][3:6])/60.0
            points.append((n,e))
            names.append(parts[0][4:-1])
    except IOError:
        print('Trouble with the file')
    except ValueError:
        print('Broken file')
    finally:
        file.close()
    return points, names
    
def checkTurnPoints(flight, turnpoints, tpnames,acc):
    tree = KDTree(flight)
    print('Turnpoints:\n')
    for p, name in zip(turnpoints, tpnames):
        ans = tree.query(p)
        d = calcDistance(*p,*flight[ans[1]])
        if d < 1: #XXX Change this to correct value
            print(name)

def calcDistance(lat1,lon1,lat2,lon2):
    r = 6371
    lat1=math.radians(lat1)
    lon1=math.radians(lon1)
    lat2=math.radians(lat2)
    lon2=math.radians(lon2)
    return 2*r*math.asin(math.sqrt(haversine(lat2-lat1)+math.cos(lat1)*math.cos(lat2)*haversine(lon2-lon1)))
    
def haversine(theta):
    return (1.0 - math.cos(theta))/2.0
    


def main():
    tpsfile = input('Turnpointfile [pisteet.cup]: ')
    tpsfile = tpsfile if tpsfile else 'pisteet.cup'
    if len(sys.argv)>1:
        flightfile = sys.argv[1]
    else:
        flightfile = input('Flight\n')
    flightfile = flightfile if flightfile else 'F:/Antti/lento/logs/2016-06-13-XCS-AAA-01.igc'
    if flightfile[-3:] == 'igc':
        flight, acc = parseFlight(flightfile)
    else:
        print('Reading directory...:')
        flight, acc = parseDirectory(flightfile)
    tps, tpnames = parseTurnpoints(tpsfile)
    checkTurnPoints(flight, tps, tpnames, acc)


    
if __name__ == "__main__":
    main()
    