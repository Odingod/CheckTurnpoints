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
            elif line[:5] == 'HFDTE':
                date = line[5:-1]
    except IOError as e:
        print('Trouble with the file')
        print(e)
    except ValueError as e:
        print('Broken file')
        print(e)
    finally:
        file.close()
    return points, accuracy, date
    
def parseDirectory(directory):
    if directory[-1] != '/':
        directory += '/'
    print('Reading directory '+directory+' ...')
    _,_, files = next(os.walk(directory))
    files = [f for f in files if f[-3:] == 'igc']
    points = []
    dates = [(0,0)]
    acc=0
    for filename in files:
        p,a,date = parseFlight(directory+filename)
        points += p
        dates.append((len(points),date))
        acc = max(a,acc)
    return points, acc, dates
    
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
    
def checkTurnPoints(flight, turnpoints, tpnames,acc, dates):
    tree = KDTree(flight)
    print('Turnpoints:\n')
    for p, name in zip(turnpoints, tpnames):
        ans = tree.query(p)
        d = calcDistance(*p,*flight[ans[1]])
        if d < 1: #XXX Change this to correct value
            date = [x+1 for (x,((i,_),(j,_))) in enumerate(zip(dates[:-1],dates[1:])) if i<ans[1]<j][0]
            print(dates[date][1], name)

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
    tpsfile = input('Turnpoint file [pisteet.cup]: ')
    tpsfile = tpsfile if tpsfile else 'pisteet.cup'
    if len(sys.argv)>1:
        flightfile = sys.argv[1]
    else:
        flightfile = input('Path to .igc file or to a folder: ')
    if flightfile[-3:] == 'igc':
        flight, acc, date = parseFlight(flightfile)
        dates = [(0,0),(len(flight),date)]
    else:
        flight, acc, dates = parseDirectory(flightfile)
    tps, tpnames = parseTurnpoints(tpsfile)
    checkTurnPoints(flight, tps, tpnames, acc, dates)


    
if __name__ == "__main__":
    main()
    