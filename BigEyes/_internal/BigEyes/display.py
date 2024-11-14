from platform import system
doRun = True
## check os
if system() != "Linux":
    print("This code is designed for Linux + GNU base Debian package")
    doRun = False
    # quit()
try :
    import math
    import numpy as np
    import pandas as pd
    from dash import Dash, dcc, html, Input, Output, ctx
    import plotly.graph_objects as go
    import plotly.express as px
    import matplotlib.pyplot as plt
    import plotly
    from flask import Flask
    from PIL import Image
    import os
    import signal
    import webbrowser
    import subprocess
    from time import sleep
except Exception as e:
    print("Error while import libraries: " + str(e) + "\nTry to install the libraries")
    #!pip install numpy
    #!pip install pandas
    #!pip install dash
    #!pip install plotly
    #!pip install matplotlib
    #!pip install flask
    #!pip install pillow  
    #!pip install signals
    #!pip install python-signal
    #!pip install subprocess.run
    subprocess.run(["pip", "install", "numpy"])
    subprocess.run(["pip", "install", "pandas"])
    subprocess.run(["pip", "install", "dash"])
    subprocess.run(["pip", "install", "plotly"])
    subprocess.run(["pip", "install", "matplotlib"])
    subprocess.run(["pip", "install", "flask"])
    subprocess.run(["pip", "install", "pillow"])
    subprocess.run(["pip", "install", "signals"])
    subprocess.run(["pip", "install", "python-signal"])
    subprocess.run(["pip", "install", "subprocess.run"])
    try :
        ## install xdotool on linux + GNU base debian package
        if doRun:
            subprocess.run(["sudo", "apt-get", "install", "xdotool"])
    except Exception as e:
        print("Sorry but this code create for wayland system: " + str(e))

df = pd.DataFrame()
raw = np.empty((1,1))

def readRaw(row: int, column: int, typeOfInfo: int) -> int:
#     row, column start from 1 to n
#     typeOfInfo from 1 to 3
    typeOfInfo -= 1
    row -= 1
    # row out of bounce
    if row < 0 or row >= raw[0][0]:
        return None
    column -= 1
    # column out of bounce
    if column < 0 or column >= raw[0][1]:
        return None
    column = column + int(raw[0][1])*typeOfInfo + 2
    value: int = 0
    value = raw[row][column]
    return value

def readRaw_float(row: int, column: int, typeOfInfo: int) -> float:
#     row, column start from 1 to n
#     typeOfInfo from 1 to 3
    typeOfInfo -= 1
    row -= 1
    # row out of bounce
    if row < 0 or row >= raw[0][0]:
        return None
    column -= 1
    # column out of bounce
    if column < 0 or column >= raw[0][1]:
        return None
    column = column + int(raw[0][1])*typeOfInfo + 2
    value: int = 0
    value = float(raw[row][column])
    return value

def extractNP(parm: np.ndarray) -> np.ndarray:
    a = np.zeros((int(raw[0][0]), int(raw[0][1])))
    for row in range(int(raw[0][0])):
        for column in range(int(raw[0][1])):
            a[row][column] = parm[row][column+2+int(raw[0][1]*2)]
    return a

def saveMap(cfgNP: np.ndarray, orgPD: pd.DataFrame, asMdf=False, asNew=False, location: str= "./save/map.csv") -> int:
#     This would save data as map.csv file
    df_new = pd.DataFrame(cfgNP, columns=orgPD.columns)
    if asNew:
        df_new.to_csv(location, index=False)
    elif asMdf:
        df_new.to_csv('map_modified.csv', index=False)
    else :
        df_new.to_csv('map.csv', index=False)
    return 0

def saveCSV(np_array: np.ndarray, name: str) -> int:
    Row: int = np_array.shape[0]
    Column: int = np_array.shape[1]
    array = np.zeros((Row,Column+2))
    Columns = ["sizeRow","sizeColumn"]
    for i in range(Column):
        Columns.append(i)
    for i in range(1,Row):
        for j in range(2):
            array[i][j] = None
    array[0][0] = Row 
    array[0][1] = Column
    for i in range(Row):
        for j in range(Column):
            array[i][j+2] = np_array[i][j]
    df_new = pd.DataFrame(array, columns=Columns)
    df_new.to_csv(name+".csv", index=False)
    return 0

def extract_shortCSV(name: str) -> np.ndarray:
    df_load = pd.read_csv(name+".csv")
    array_load = df_load.to_numpy()
    a = np.zeros((int(array_load[0][0]),int(array_load[0][1])))
    for i in range(int(array_load[0][0])):
        for j in range(int(array_load[0][1])):
                 a[i][j] = array_load[i][j+2]
    return a

def blurSpot(inRow: int,inClmn: int, size: int = 9, rateChange: float = 0.65, debug: bool = False) -> float:
    value: float = 0
    Sum = 0
    Count = 0
    if debug :
        print(f"row {inRow-int(math.floor((size-1)/2))} - {inRow+int(math.ceil((size-1)/2))}\ncolumn {inClmn-int(math.floor((size-1)/2))} - {inClmn+int(math.ceil((size-1)/2))}")
    for row in range(inRow-int(math.floor((size-1)/2)),inRow+int(math.ceil((size-1)/2))+1):
        for column in range(inClmn-int(math.floor((size-1)/2)),inClmn+int(math.ceil((size-1)/2))+1):
            Temp = readRaw(row+1, column+1, 3)
#             if debug :
#                 print(Temp)
            if Temp is None:
                if debug :
                    print(f"not found ({row},{column})")
                    if row == inRow and column == inClmn:
                        if debug:
                            print("This is a wall!!, cannot be in here.")
                        return 0;
            else :
                if readRaw(row+1, column+1, 1) != 0 and  int(str(readRaw(row+1, column+1, 1))[0]) != 2:
                    temp = math.sqrt((inRow-row)*(inRow-row)+(inClmn-column)*(inClmn-column))*rateChange+1
                    Sum += Temp/temp
                    Count += 1
                    if debug :
                        print(Temp)
                else :
                    if debug :
                        print(f"found wall ({row},{column})")
    if (Count ==  0):
        return 0
    value = Sum/Count
    if not (readRaw(inRow+1, inClmn+1, 1) != 0 and int(str(readRaw(inRow+1, inClmn+1, 1))[0]) != 2):
        if debug:
            print("This is a wall!!, cannot be in here.")
        return 0;
    return value;

def blur(size: int = 9, rateChange: float = 0.65) -> np.ndarray:
    a = np.empty_like(raw)
    a[:] = raw
    for row in range(int(raw[0][0])):
        for column in range(int(raw[0][1])):
            a[row][column+int(raw[0][1]*2)+2] = blurSpot(row, column, size=size, rateChange=rateChange)
    return a

def map_value(value, from_low, from_high, to_low, to_high) -> float:
    return (value - from_low) * (to_high - to_low) / (from_high - from_low) + to_low

def speed(lowestValue: float = 1.2, size: int = 9, rateChange: float = 0.65) -> np.ndarray:
    a = np.zeros((int(raw[0][0]), int(raw[0][1])))
    b = blur(size=size, rateChange=rateChange)
    
    for row in range(int(raw[0][0])):
        for column in range(int(raw[0][1])):
            a[row][column] = b[row][column+int(raw[0][1]*2)+2]
    
    Max = np.max(a)
    
    mask = a > lowestValue
    Min = np.min(a[mask])
        
    for row in range(int(raw[0][0])):
        for column in range(int(raw[0][1])):
            if b[row][column+int(raw[0][1]*2)+2] <= lowestValue :
                b[row][column+int(raw[0][1]*2)+2] = 0
            else :
                b[row][column+int(raw[0][1]*2)+2] = map_value(b[row][column+int(raw[0][1]*2)+2],Min,Max,Max,Min)
    
    return b

def density(expand: int = 3, dropValue: float = 0.85, debug: bool = False) -> np.ndarray:
    a = np.empty_like(raw)
    a[:] = raw
    count = 0
    Row = list()
    Column = list()
    Value = list()
    for row in range(int(raw[0][0])):
        for column in range(int(raw[0][1])):
            if readRaw(row+1, column+1, 2):
                count += 1
                Row.append(row)
                Column.append(column)
                Value.append(readRaw(row+1, column+1, 3))
                
    for i in range(count):
        temp = Value[i]
        x = -expand
        if (debug):
            print(f"{temp} : ({Row[i]},{Column[i]})")
        for row in range(Row[i]-expand,Row[i]+expand+1):
            y = -expand
            for column in range(Column[i]-expand, Column[i]+expand+1):
                Temp = readRaw(row+1, column+1, 1)
                if not (row == Row[i] and column == Column[i]):
                    if debug:
                        print(f"({x},{y})")
                    if not Temp is None:
                        if Temp != 0 and int(str(readRaw(row+1, column+1, 1))[0]) != 2:
                            a[row][column+2+int(raw[0][1]*2)] += map_value(math.sqrt(y*y+x*x),0,math.sqrt(2*(expand+1)*(expand+1)),temp*dropValue,0)
                y+=1
            x+=1
    return a

def scaleCheckBorder(scale: int, disy: int, disx: int, mapNumpy: np.ndarray, posRow: int, posColumn: int, maxRow: int, maxColumn: int) -> bool:
    # if it is not on the border should return False
#     print(mapNumpy[7][35])
    if scale <= 1:
        return False
    list_border = list()
    for row in range(scale):
        for column in range(2):
            Temp = (0,scale-1)
            list_border.append((row,Temp[column]))
    for column in range(1,scale-1):
        for row in range(2):
            Temp = (0,scale-1)
            list_border.append((Temp[row],column))
    if not (disy,disx) in list_border:
        return False
    
    # find that near parent is the same type or not??
    # type check up down left right edge-4
    temp = mapNumpy[posRow][posColumn]
        # up
    if posRow - 1 >= 0:
        if disy == 0 and (disx >= 0 and disx <= scale-1):
            if temp != mapNumpy[posRow-1][posColumn]:
                return True
        # down
    if posRow + 1  < maxRow:
        if disy == scale-1 and (disx >= 0 and disx <= scale-1):
            if temp != mapNumpy[posRow+1][posColumn]:
                return True
        # left
    if posColumn - 1 >= 0:
        if disx == 0 and (disy >= 0 and disy <= scale-1):
            if temp != mapNumpy[posRow][posColumn-1]:
                return True
        # right
    if posColumn + 1 < maxColumn:
        if disx == scale-1 and (disy >= 0 and disy <= scale-1):
            if temp != mapNumpy[posRow][posColumn+1]:
                return True
        # edge
        # left up
    if posColumn - 1 >= 0 and posRow - 1 >= 0:
        if disx == 0 and disy == 0:
            if temp != mapNumpy[posRow-1][posColumn-1]:
                return True
        # right up
    if posColumn + 1 < maxColumn and posRow - 1 >= 0:
        if disx == scale-1 and disy == 0:
            if temp != mapNumpy[posRow-1][posColumn+1]:
                return True
        # left down
    if posColumn - 1 >= 0 and posRow + 1 < maxRow:
        if disx == 0 and disy == scale-1:
            if temp != mapNumpy[posRow+1][posColumn-1]:
                return True
        # right down
    if posColumn + 1 < maxColumn and posRow + 1 < maxRow:
        if disx == scale-1 and disy == scale-1:
            if temp != mapNumpy[posRow+1][posColumn+1]:
                return True
    return False

def scalemap(border :int = 3, debug: bool=False, save: bool=True, saveName: str="./temp/map_scale", createborder: list[str]=["0","2","3"], enBorder: bool=True, saveData: bool=True) -> np.ndarray:
    global raw
    org_h, org_w = int(raw[0][0]), int(raw[0][1])
    exp = [(border*2+1,border*2+1)]
    exp.append((int(exp[0][0]*org_h),int(exp[0][1]*org_w)))
    nmap = np.zeros((exp[1][0],exp[1][1]+2))
    temp = np.zeros(exp[1])
    Temp = np.zeros(exp[1])
    nmap[0][0], nmap[0][1] = exp[1]
    if debug:
        print(f"set up value : {exp}")
        
    # copy value and expand by border
    for Rows in range(org_h):
        for Columns in range(org_w):
            Row = Rows*exp[0][0]
            Column = Columns*exp[0][1]
            for rScale in range(exp[0][0]):
                for cScale in range(exp[0][1]):
                    row = Row + rScale
                    column = Column + cScale
                    nmap[row][column+2] = raw[Rows][Columns+2]
                    temp[row][column] = raw[Rows][Columns+2]
                    Temp[row][column] = raw[Rows][Columns+2]
                    
    # create border
    if enBorder:
        for Rows in range(org_h):
            for Columns in range(org_w):
                Row = Rows*exp[0][0]
                Column = Columns*exp[0][1]
                for rScale in range(exp[0][0]):
                    for cScale in range(exp[0][1]):
                        row = Row + rScale
                        column = Column + cScale
                        if str(raw[Rows][Columns+2])[0] in createborder:
                            if scaleCheckBorder(exp[0][0], rScale, cScale, temp, row, column, exp[1][0], exp[1][1]):
                                buffer = "9" + str(raw[Rows][Columns+2])[0]
                                nmap[row][column+2] = int(buffer)
                                Temp[row][column] = int(buffer)
    
    # save data as map_scale.csv
    if saveData:
        saveCSV(Temp,saveName)
        saveCSV(temp,saveName+"noborder")
    return nmap

def scaleInfo_box(arr: np.ndarray, scale: int) -> np.ndarray:
    temp = np.zeros((scale,scale))
    center = (scale-1)/2 + 1
    center_int = int(center)
    
    # set middle line 
    Map = {
            "u" : arr[0][center_int], "d" : arr[scale+2-1][center_int], "l": arr[center_int][0],"r": arr[center_int][scale+2-1],
            "m" : arr[center_int][center_int],
            "ul": arr[0][0], "ur": arr[0][scale+2-1], "dl": arr[scale+2-1][0], "dr":arr[scale+2-1][scale+2-1]
          }
    # m
    temp[center_int-1][center_int-1] = Map["m"] 
    # u
    for i in range(center_int-1):
        row = center_int - i - 2
        temp[row][center_int-1] = map_value(i,-1,center_int-2,Map["m"],Map["u"])
    # d
    for i in range(center_int-1):
        row = center_int + i
        temp[row][center_int-1] = map_value(i,-1,center_int-2,Map["m"],Map["d"])
    # l
    for i in range(center_int-1):
        column = center_int - i - 2
        temp[center_int-1][column] = map_value(i,-1,center_int-2,Map["m"],Map["l"])        
    # r
    for i in range(center_int-1):
        column = center_int + i
        temp[center_int-1][column] = map_value(i,-1,center_int-2,Map["m"],Map["r"])
        
    # create crossline
    center_int -= 1
    # ul
    for i in range(center_int):
            row = center_int -i -1
            column = center_int -i -1
            temp[row][column] = (map_value(i,0,center_int-1,Map["m"],Map["u"]) + map_value(i,0,center_int-1,Map["m"],Map["l"]) + map_value(i,0,center_int-1,Map["m"],Map["ul"]))/3
    # ur
    for i in range(center_int):
            row = center_int -i -1
            column = center_int +i +1
            temp[row][column] = (map_value(i,0,center_int-1,Map["m"],Map["u"]) + map_value(i,0,center_int-1,Map["m"],Map["r"]) + map_value(i,0,center_int-1,Map["m"],Map["ur"]))/3
    # dl
    for i in range(center_int):
            row = center_int +i +1
            column = center_int -i -1
            temp[row][column] = (map_value(i,0,center_int-1,Map["m"],Map["d"]) + map_value(i,0,center_int-1,Map["m"],Map["l"]) + map_value(i,0,center_int-1,Map["m"],Map["dl"]))/3
    # dr
    for i in range(center_int):
            row = center_int +i +1
            column = center_int +i +1
            temp[row][column] = (map_value(i,0,center_int-1,Map["m"],Map["d"]) + map_value(i,0,center_int-1,Map["m"],Map["r"]) + map_value(i,0,center_int-1,Map["m"],Map["dr"]))/3
            
    # create missing out data
    # ul
    for i in range(1,center_int):
        row = center_int -i -1
        size = i + 2
        for j in range(0,i,1):
            pos = (j+1+1,size-j-2)
            column = center_int -j -1
            temp[row][column] = (pos[1]/size)*temp[row][center_int]+ (pos[0]/size)*temp[row][row]
    for i in range(1,center_int):
        column = center_int -i -1
        size = i + 2
        for j in range(0,i,1):
            pos = (j+1+1,size-j-2)
            row = center_int -j -1
            temp[row][column] = (pos[1]/size)*temp[center_int][column]+ (pos[0]/size)*temp[column][column]
    # ur
    for i in range(1,center_int):
        row = center_int -i -1
        Row = center_int +i +1
        size = i + 2
        for j in range(0,i,1):
            pos = (j+1+1,size-j-2)
            column = center_int +j +1
            temp[row][column] = (pos[1]/size)*temp[row][center_int]+ (pos[0]/size)*temp[row][Row]
    for i in range(1,center_int):
        column = center_int +i +1
        Row = center_int -i -1
        size = i + 2
        for j in range(0,i,1):
            pos = (j+1+1,size-j-2)
            row = center_int -j -1
            temp[row][column] = (pos[1]/size)*temp[center_int][column]+ (pos[0]/size)*temp[Row][column]
    # dl
    for i in range(1,center_int):
        row = center_int +i +1
        Row = center_int -i -1
        size = i + 2
        for j in range(0,i,1):
            pos = (j+1+1,size-j-2)
            column = center_int -j -1
            temp[row][column] = (pos[1]/size)*temp[row][center_int]+ (pos[0]/size)*temp[row][Row]
    for i in range(1,center_int):
        column = center_int -i -1
        Row = center_int +i +1
        size = i + 2
        for j in range(0,i,1):
            pos = (j+1+1,size-j-2)
            row = center_int +j +1
            temp[row][column] = (pos[1]/size)*temp[center_int][column]+ (pos[0]/size)*temp[Row][column]
    # dr
    for i in range(1,center_int):
        row = center_int +i +1
        size = i + 2
        for j in range(0,i,1):
            pos = (j+1+1,size-j-2)
            column = center_int +j +1
            temp[row][column] = (pos[1]/size)*temp[row][center_int]+ (pos[0]/size)*temp[row][row]
    for i in range(1,center_int):
        column = center_int +i +1
        Row = center_int +i +1
        size = i + 2
        for j in range(0,i,1):
            pos = (j+1+1,size-j-2)
            row = center_int +j +1
            temp[row][column] = (pos[1]/size)*temp[center_int][column]+ (pos[0]/size)*temp[Row][column]
    
    return temp

def scaleInfo(Map: np.ndarray, org: np.ndarray, saveName: str, border: int=3, read: list[str]=["1","3","4"], debug: bool=False, nameRescale: bool= True) -> np.ndarray:
    scale = border*2 + 1
    size = [(int(Map[0][0] * scale),int(Map[0][1] * scale))]
    size.append((int(size[0][0]/scale),int(size[0][1]/scale)))
    center = (scale-1)/2+1
    center_int = int(center)
    temp = np.ndarray(size[0])
    center_int -= 1
    Count = 0
    for row in range(size[1][0]):
        for column in range(size[1][1]):
            Row = row*scale
            Column = column*scale
            if not str(Map[row][column+2])[0] in read:
                for i in range(scale):
                    for j in range(scale):
                        temp[Row+i][Column+j] = 0
            else :
                buffer = np.zeros((scale+2,scale+2))
                # save data for processing
                # u d l r 
                # check is box is available
                Temp: bool = {"u":False,"d":False,"l":False,"r":False, "ul":True, "ur":True, "dl":True, "dr":True}
                # m
                buffer[center_int+1][center_int+1] = org[row][column]
                # u
                if row-1 < 0:
                    buffer[0][center_int+1] = org[row][column]
                    Temp["u"]=True
                    Count += 1
                else :
                    if not str(Map[row-1][column+2])[0] in read:
                        buffer[0][center_int+1] = org[row][column]
                        Temp["u"]=True
                        Count += 1
                    else :
                        buffer[0][center_int+1] = (org[row-1][column]+org[row][column])/2
                # d
                if row+1 >= size[1][0]:
                    buffer[scale+1][center_int+1] = org[row][column]
                    Temp["d"]=True
                    Count += 1
                else :
                    if not str(Map[row+1][column+2])[0] in read:
                        buffer[scale+1][center_int+1] = org[row][column]
                        Temp["d"]=True
                        Count += 1
                    else :
                        buffer[scale+1][center_int+1] = (org[row+1][column]+org[row][column])/2
                # l
                if column-1 < 0:
                    buffer[center_int+1][0] = org[row][column]
                    Temp["l"]=True
                    Count += 1
                else :
                    if not str(Map[row][column+1])[0] in read:
                        buffer[center_int+1][0] = org[row][column]
                        Temp["l"]=True
                        Count += 1
                    else :
                        buffer[center_int+1][0] = (org[row][column-1]+org[row][column])/2
                # r
                if column+1 >= size[1][1]:
                    buffer[center_int+1][scale+1] = org[row][column]
                    Temp["r"]=True
                    Count += 1
                else :
                    if not str(Map[row][column+3])[0] in read:
                        buffer[center_int+1][scale+1] = org[row][column]
                        Temp["r"]=True
                        Count += 1
                    else :
                        buffer[center_int+1][scale+1] = (org[row][column+1]+org[row][column])/2
                        
                # ul
                if row-1 < 0 or column-1 < 0:
                    buffer[0][0] = org[row][column]
                else :
                    if not str(Map[row-1][column+1])[0] in read:
                        buffer[0][0] = org[row][column]
                    else :
                        buffer[0][0] = (org[row-1][column-1]+org[row-1][column]+org[row][column-1])/3
                        if not Temp["u"] and Temp["l"]:
                            buffer[0][0] = (org[row-1][column-1]+4*org[row-1][column])/5
                        elif Temp["u"] and not Temp["l"]:
                            buffer[0][0] = (org[row-1][column-1]+4*org[row][column-1])/5
                        Temp["ul"]=False
                # ur
                if row-1 < 0 or column+1 >= size[1][1]:
                    buffer[0][scale+1] = org[row][column]
                else :
                    if not str(Map[row-1][column+3])[0] in read:
                        buffer[0][scale+1] = org[row][column]
                    else :
                        buffer[0][scale+1] = (org[row-1][column+1]+org[row-1][column]+org[row][column+1])/3
                        if not Temp["u"] and Temp["r"]:
                            buffer[0][scale+1] = (org[row-1][column+1]+4*org[row-1][column])/5
                        elif Temp["u"] and not Temp["l"]:
                            buffer[0][scale+1] = (org[row-1][column+1]+4*org[row][column+1])/5
                        Temp["ur"]=False
                # dl
                if row+1 >= size[1][0] or column-1 < 0:
                    buffer[scale+1][0] = org[row][column]
                else :
                    if not str(Map[row+1][column+1])[0] in read:
                        buffer[scale+1][0] = org[row][column]
                    else :
                        buffer[scale+1][0] = (org[row+1][column-1]+org[row+1][column]+org[row][column-1])/3
                        if not Temp["d"] and Temp["l"]:
                            buffer[scale+1][0] = (org[row+1][column-1]+4*org[row+1][column])/5
                        elif Temp["d"] and not Temp["l"]:
                            buffer[scale+1][0] = (org[row+1][column-1]+4*org[row][column-1])/5
                        Temp["dl"]=False
                # dr
                if row+1 >= size[1][0] or column+1 >= size[1][1]:
                    buffer[scale+1][scale+1] = org[row][column]
                else :
                    if not str(Map[row+1][column+3])[0] in read:
                        buffer[scale+1][scale+1] = org[row][column]
                    else :
                        buffer[scale+1][scale+1] = (org[row+1][column+1]+org[row+1][column]+org[row][column+1])/3
                        if not Temp["d"] and Temp["r"]:
                            buffer[scale+1][scale+1] = (org[row+1][column+1]+4*org[row+1][column])/5
                        elif Temp["d"] and not Temp["r"]:
                            buffer[scale+1][scale+1] = (org[row+1][column+1]+4*org[row][column+1])/5
                        Temp["dr"]=False
                 
                if  Count > 0 and Count < 3:
                    # clean up
                    # l u r
                    if Temp["u"]:
                        if not Temp["l"] and not Temp["r"]:
                            buffer[0][center_int+1] = (buffer[center_int+1][0] + buffer[center_int+1][scale+1] + buffer[center_int+1][center_int+1])/3
                            buffer[center_int+1][center_int+1] = buffer[0][center_int+1]
                            buffer[0][0] = (buffer[center_int+1][0] + buffer[center_int+1][center_int+1])/2
                            buffer[0][scale+1] = (buffer[center_int+1][scale+1] + buffer[center_int+1][center_int+1])/2
                            Temp["ul"]=False
                            Temp["ur"]=False
                        elif not Temp["l"]:
                            buffer[0][center_int+1] = (buffer[center_int+1][0] + buffer[center_int+1][center_int+1])/2
                            buffer[0][0] = (2*buffer[center_int+1][0] + buffer[center_int+1][center_int+1])/3
                            Temp["ul"]=False
                        elif not Temp["r"]:
                            buffer[0][center_int+1] = (buffer[center_int+1][scale+1] + buffer[center_int+1][center_int+1])/2
                            buffer[0][scale+1] = (2*buffer[center_int+1][scale+1] + buffer[center_int+1][center_int+1])/3
                            Temp["ur"]=False
                        else :
                            pass
                    # l d u
                    if Temp["d"]:
                        if not Temp["l"] and not Temp["r"]:
                            buffer[scale+1][center_int+1] = (buffer[center_int+1][0] + buffer[center_int+1][scale+1] + buffer[center_int+1][center_int+1])/3
                            buffer[center_int+1][center_int+1] = buffer[scale+1][center_int+1]
                            buffer[scale+1][0] = (buffer[center_int+1][0] + buffer[center_int+1][center_int+1])/2
                            buffer[scale+1][scale+1] = (buffer[center_int+1][scale+1] + buffer[center_int+1][center_int+1])/2
                            Temp["dl"]=False
                            Temp["dr"]=False
                        elif not Temp["l"]:
                            buffer[scale+1][center_int+1] = (buffer[center_int+1][0] + buffer[center_int+1][center_int+1])/2
                            buffer[scale+1][0] = (5*buffer[center_int+1][0] + buffer[center_int+1][center_int+1])/6
                            Temp["dl"]=False
                        elif not Temp["r"]:
                            buffer[scale+1][center_int+1] = (buffer[center_int+1][scale+1] + buffer[center_int+1][center_int+1])/2
                            buffer[scale+1][scale+1] = (5*buffer[center_int+1][scale+1] + buffer[center_int+1][center_int+1])/6
                            Temp["dr"]=False
                        else :
                            pass
                    # u l d
                    if Temp["l"]:
                        if not Temp["u"] and not Temp["d"]:
                            buffer[center_int+1][0] = (buffer[0][center_int+1] + buffer[scale+1][center_int+1] + buffer[center_int+1][center_int+1])/3
                            buffer[center_int+1][center_int+1] = buffer[center_int+1][0]
                            buffer[0][0] = (buffer[0][center_int+1] + buffer[center_int+1][center_int+1])/2
                            buffer[scale+1][0] = (buffer[scale+1][center_int+1] + buffer[center_int+1][center_int+1])/2
                            Temp["ul"]=False
                            Temp["dl"]=False
                        elif not Temp["u"]:
                            buffer[center_int+1][0] = (buffer[0][center_int+1] + buffer[center_int+1][center_int+1])/2
                            buffer[0][0] = (5*buffer[0][center_int+1] + buffer[center_int+1][center_int+1])/6
                            Temp["ul"]=False
                        elif not Temp["d"]:
                            buffer[center_int+1][0] = (buffer[scale+1][center_int+1] + buffer[center_int+1][center_int+1])/2
                            buffer[scale+1][0] = (5*buffer[scale+1][center_int+1] + buffer[center_int+1][center_int+1])/6
                            Temp["dl"]=False
                        else :
                            pass
                    # u r d
                    if Temp["r"]:
                        if not Temp["u"] and not Temp["d"]:
                            buffer[center_int+1][scale+1] = (buffer[0][center_int+1] + buffer[scale+1][center_int+1] + buffer[center_int+1][center_int+1])/3
                            buffer[center_int+1][center_int+1] = buffer[center_int+1][scale+1]
                            buffer[0][scale+1] = (buffer[0][center_int+1] + buffer[center_int+1][center_int+1])/2
                            buffer[scale+1][scale+1] = (buffer[scale+1][center_int+1] + buffer[center_int+1][center_int+1])/2
                            Temp["ur"]=False
                            Temp["dr"]=False
                        elif not Temp["u"]:
                            buffer[center_int+1][scale+1] = (buffer[0][center_int+1] + buffer[center_int+1][center_int+1])/2
                            buffer[0][scale+1] = (5*buffer[0][center_int+1] + buffer[center_int+1][center_int+1])/6
                            Temp["ur"]=False
                        elif not Temp["d"]:
                            buffer[center_int+1][scale+1] = (buffer[scale+1][center_int+1] + buffer[center_int+1][center_int+1])/2
                            buffer[scale+1][scale+1] = (5*buffer[scale+1][center_int+1] + buffer[center_int+1][center_int+1])/6
                            Temp["dr"]=False
                        else :
                            pass
                        
                # update missing edge
                # ul
                if Temp["ul"]:
                    if not Temp["u"] and not Temp["l"]:
                        buffer[0][0] = (buffer[0][center_int+1] + buffer[center_int+1][0])/2
                    elif not Temp["u"]:
                        buffer[0][0] = (buffer[0][center_int+1] + buffer[center_int+1][center_int+1])/2
                    elif not Temp["l"]:
                        buffer[0][0] = (buffer[center_int+1][center_int+1] + buffer[center_int+1][0])/2
                    else :
                        pass
                # ur
                if Temp["ur"]:
                    if not Temp["u"] and not Temp["r"]:
                        buffer[0][scale+1] = (buffer[0][center_int+1] + buffer[center_int+1][scale+1])/2
                    elif not Temp["u"]:
                        buffer[0][scale+1] = (buffer[0][center_int+1] + buffer[center_int+1][center_int+1])/2
                    elif not Temp["r"]:
                        buffer[0][scale+1] = (buffer[center_int+1][center_int+1] + buffer[center_int+1][scale+1])/2
                    else :
                        pass
                # dl
                if Temp["dl"]:
                    if not Temp["d"] and not Temp["l"]:
                        buffer[scale+1][0] = (buffer[scale+1][center_int+1] + buffer[center_int+1][0])/2
                    elif not Temp["d"]:
                        buffer[scale+1][0] = (buffer[scale+1][center_int+1] + buffer[center_int+1][center_int+1])/2
                    elif not Temp["l"]:
                        buffer[scale+1][0] = (buffer[center_int+1][center_int+1] + buffer[center_int+1][0])/2
                    else :
                        pass
                # dr
                if Temp["dr"]:
                    if not Temp["d"] and not Temp["r"]:
                        buffer[scale+1][scale+1] = (buffer[scale+1][center_int+1] + buffer[center_int+1][scale+1])/2
                    elif not Temp["d"]:
                        buffer[scale+1][scale+1] = (buffer[scale+1][center_int+1] + buffer[center_int+1][center_int+1])/2
                    elif not Temp["r"]:
                        buffer[scale+1][scale+1] = (buffer[center_int+1][center_int+1] + buffer[center_int+1][scale+1])/2
                    else :
                        pass    
                    
                # process data
                Buffer = scaleInfo_box(buffer, scale)
                
                # save data
                for i in range(scale):
                    for j in range(scale):
                        temp[Row+i][Column+j] = Buffer[i][j]
                    
    if debug:
        print(temp)
    if nameRescale:
        saveName = saveName + "_scale"
    saveCSV(temp,saveName)
    
    return temp


# df = pd.read_csv('map.csv')
# raw = df.to_numpy()
# # saveMap(density(), df, asMdf=True)
# saveCSV(extractNP(density()),"./temp/density")
# saveCSV(extractNP(speed()),"./temp/flow")
# saveCSV(extractNP(blur()),"./temp/interaction")

server = Flask(__name__)
app = Dash(__name__, server=server)

Temp_app =   {
                "debug":False, 
                "log-fileName":"Waiting for input...",
                "select_image":[["interaction","speed","density"],0,["./temp/interaction_scale","./temp/flow_scale","./temp/density_scale"]],
                "dd":1, "mm":1, "yy":1985,
                "upsize":5,
                "url":"#",
                "size":9, "rateChange":0.65, "speed-s":2, "speed-rC":0.12, "expand":3
             }

Temp_color = {
                "0":(96,96,96), 
                "1": None, 
                "2":(247, 234, 173), 
                "2+":(1,-12,-58), 
                "3":None, 
#                 "3+":(51,0,-25), 
                "4":None, 
                "colorORG":(102,0,254), 
                "colorHGH":(255,51,51), 
                "minClrRange": 12,
                "9":(0,0,0),
                "90":(54,52,52),
                "92":(245,128,0),
                "93":(180,180,180),
             }

def create_fig(array: np.ndarray, init: bool=False) -> plotly.graph_objs._figure.Figure:
    global fig, image_data
    # create random for display start
    if init:
        img = Image.open('./AppData/img.png')
        img = img.resize((80,80))
        image_data = np.array(img)
    else :
        image_data = array
        
    height, width, channels = image_data.shape 
    ratio, size_w, size_h = height/width, 0, 0
    if ratio > 1:
        size_w = 400
        size_h = 400 * ratio
    else :
        size_h = 400
        size_w = 400 / ratio
    fig = go.Figure(data=go.Image(z=image_data))
    fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False, xaxis_showticklabels=False, yaxis_showticklabels=False)
    fig.update_layout(
        margin=dict(l=2, r=2, t=2, b=2),
        width =size_w,
        height=size_h,
    )
    return fig
        
        
fig = create_fig(np.zeros((1,1)), init=True)

def genImg(valueArr: np.ndarray, debug: bool=False) -> np.ndarray:
    global raw
    if debug:
        print(f"In func() -> genImg \n{raw}")
    Rows = int(raw[0][0])
    Columns = int(raw[0][1])
    if debug:
        print(f"Pass : load func(): get IMG\n{valueArr}")
    Min, Max = None, None
    Temp = np.empty((Rows, Columns, 3), dtype=np.uint8)
    for row in range(Rows):
        for column in range(Columns):
            if str(raw[row][column+2])[0] in ["3","4","1"]:
                if Min is None or Max is None:
                    Min, Max = valueArr[row][column], valueArr[row][column]
                if Min > valueArr[row][column]:
                    Min = valueArr[row][column]
                if Max < valueArr[row][column]:
                    Max = valueArr[row][column]
    if debug:
        print(F"min : {Min}, max : {Max}")
        
    if Min/(Min + Max) * 100 < Temp_color["minClrRange"]:
        Min = Min / Temp_color["minClrRange"] * (Min/(Min + Max) * 100)
        Min -= Temp_color["minClrRange"] / (Min/(Min + Max) * 100) * 0.5
        if debug:
            print(F"min : {Min}, max : {Max}")
    
    for row in range(1,Rows+1):
        for column in range(1,Columns+1):
            temp = readRaw(row, column, 1)
            if not Temp_color[str(temp)[0]] is None:
                Row = row-1
                Column = column-1
                if debug:
                    print(f"in ({Row},{Column})")
                Temp[Row][Column] = Temp_color[str(temp)[0]]
                if debug:
                    print(f"save : {Temp[Row][Column]}")
                if int(temp) >= 10:
                    if not str(temp)[0] in ["9"]:
                        buffer = str(temp)[0]+"+"
                        value_buffer = 1
                        value_buffer = int(temp)%10 - 1
                        convert = (Temp_color[buffer][0]*value_buffer,Temp_color[buffer][1]*value_buffer,Temp_color[buffer][2]*value_buffer)
                        if debug:
                            print(f"({value_buffer}) -> {convert}")
                        Temp[Row][Column] = Temp[Row][Column] + convert
                    else :
                        buffer = str(temp)[0] + str(temp)[1] 
                        if debug:
                            print(f"load cover <9> : {buffer}")
                        convert = Temp_color[buffer]
                        Temp[Row][Column] = convert
                        
                        # for type "3"
                        if str(temp)[1] in ["3"]:
                            if debug:
                                print(f"load cover <9 -> 3> : {buffer}")
                            Row = row-1
                            Column = column-1
                            if debug:
                                print(f"in ({Row},{Column})")
                            Buffer = map_value(float(valueArr[Row][Column]),Min,Max,0 + Temp_color["minClrRange"]/(Min/(Min + Max) * 100),100)
                            create = (map_value(Buffer,0,100,Temp_color["colorORG"][0],Temp_color["colorHGH"][0]),
                                      map_value(Buffer,0,100,Temp_color["colorORG"][1],Temp_color["colorHGH"][1]),
                                      map_value(Buffer,0,100,Temp_color["colorORG"][2],Temp_color["colorHGH"][2]))
                            # overlay
                            overlay: float=65.2
                            create = (map_value(overlay,0,100,create[0],Temp[Row][Column][0]),
                                      map_value(overlay,0,100,create[1],Temp[Row][Column][1]),
                                      map_value(overlay,0,100,create[2],Temp[Row][Column][2]))
                            Temp[Row][Column] = create
                            if debug:
                                print(f"save : {Temp[Row][Column]}")
                            
            else :
                Row = row-1
                Column = column-1
                if debug:
                    print(f"in ({Row},{Column})")
                Buffer = map_value(float(valueArr[Row][Column]),Min,Max,0 + Temp_color["minClrRange"]/(Min/(Min + Max) * 100),100)
                create = (map_value(Buffer,0,100,Temp_color["colorORG"][0],Temp_color["colorHGH"][0]),
                          map_value(Buffer,0,100,Temp_color["colorORG"][1],Temp_color["colorHGH"][1]),
                          map_value(Buffer,0,100,Temp_color["colorORG"][2],Temp_color["colorHGH"][2]))
                Temp[Row][Column] = create
                if debug:
                    print(f"save : {Temp[Row][Column]}")
    return Temp

def creatProcessData(location: str, debug: bool = False) -> int:
    global df, raw
    try :
        df = pd.read_csv(location)
        raw = df.to_numpy()
        if debug :
            print(df)
            print(raw)
    except Exception as e:
        if debug:
            print(e)
        return 1
    else :
        df = pd.read_csv(location)
        raw = df.to_numpy()
        saveCSV(extractNP(density(expand=Temp_app["expand"])),"./temp/density")
        saveCSV(extractNP(speed(size=Temp_app["size"]+Temp_app["speed-s"], rateChange=Temp_app["rateChange"]-Temp_app["speed-rC"])),"./temp/flow")
        saveCSV(extractNP(blur(size=Temp_app["size"], rateChange=Temp_app["rateChange"])),"./temp/interaction")
        saveMap(raw, df, asNew=True, location="./temp/map.csv")
        scalemap(saveName="./temp/map_scale", border=Temp_app["upsize"])
        scaleInfo(raw, extract_shortCSV("./temp/density"), "./temp/density", border=Temp_app["upsize"])
        scaleInfo(raw, extract_shortCSV("./temp/flow"), "./temp/flow", border=Temp_app["upsize"])
        scaleInfo(raw, extract_shortCSV("./temp/interaction"), "./temp/interaction", border=Temp_app["upsize"])
        if debug:
            print("Create analysis file successfully")
        # update display
        importTemp(Temp_app["select_image"][2][Temp_app["select_image"][1]], debug=Temp_app["debug"])
        return 0

def importTemp(location_short: str, location_map: str="./temp/map_scale.csv", debug: bool = False) -> int:
    global df, raw, fig
    Temp = 0
    if debug:
        print("import shortCSV")
    try :
        global df, raw, fig
        if debug:
            print(f"read : {location_short}.csv, {location_map}")
        Temp = extract_shortCSV(location_short)
        if debug:
            print("pass : read shortCSV")
        df = pd.read_csv(location_map)
        if debug:
            print("pass : read map (in temp)")
        raw = df.to_numpy()
    except Exception as e:
        fig = create_fig(np.zeros((1,1)), init=True)
        return 1
    else :
        if debug:
            print(f"In create fig : size >> {raw[0,0]} x {raw[0,1]}")
        fig = create_fig(
            genImg(Temp, debug=Temp_app["debug"])
                )
        
        return 0
    
# initialize -> try to load data from temp file
if importTemp(Temp_app["select_image"][2][Temp_app["select_image"][1]], debug=Temp_app["debug"]):
      if Temp_app["debug"]:
            print("Can't load data <On start up>")
    
def ud_select_image(Up: bool, notMv: bool = False) -> str:
    if Up and not notMv:
        Temp_app["select_image"][1] += 1
        if (Temp_app["select_image"][1] >= len(Temp_app["select_image"][0])):
            Temp_app["select_image"][1] = 0
    elif not notMv:
        Temp_app["select_image"][1] -= 1
        if (Temp_app["select_image"][1] < 0):
            Temp_app["select_image"][1] = len(Temp_app["select_image"][0])-1
            
    # --- call open file and ready to display
    call_back = "Open data successfully"
    try :
        if importTemp(Temp_app["select_image"][2][Temp_app["select_image"][1]], debug=Temp_app["debug"]):
            call_back = "Unable to open file"
        else :
            call_back = "Updated ✔️"
    except Exception as e:
        call_back = f"Unexpected error : ({str(e)})"
    
    return call_back


app.layout = html.Div([
    # page
    html.Div([
        #left
        html.Div([
            #logo
            html.Div([
                html.H1(children="👁️"),
                html.H1(children="|", style={'margin-left' : '0.25%', 'margin-right' : '0.5%'}),
                html.Table([
                    html.H5(children="Big"),
                    html.H3(children="Eyes", style={'margin-top' : '-50%'})
                ], style={'justify-content' : 'left', 'fontFamily': 'Verdana, Sans-serif'})
            ], style={'display' : 'flex', 'justify-content' : 'center'}),
            
            #button zone            
            html.Div([
                #select file name <date-month-year>
                html.Div([    
                        html.H3(children="Enter Date 📆", style={'margin-bottom' : '-6.5px', 'text-align' : 'left', 'margin-left' : '13%'}),
                        html.Div([
                            dcc.Input(id='ddIn', placeholder="dd", type='number', style={'background-color' : 'tranparent', 'height' : '28px', 'border-radius' : 8, 'margin-top' : '15px', 'width' : '40px', 'text-align' : 'center', 'fontFamily': 'Georgia, monospace'}, min = 1, max = 31),
                            html.H3(children="/", style={'margin-right' : '10px', 'margin-left' : '10px'}),
                            dcc.Input(id='mmIn', placeholder="mm", type='number', style={'background-color' : 'tranparent', 'height' : '28px', 'border-radius' : 8, 'margin-top' : '15px', 'width' : '40px', 'text-align' : 'center', 'fontFamily': 'Georgia, monospace'}, min = 1, max = 12),
                            html.H3(children="/", style={'margin-right' : '10px', 'margin-left' : '10px'}),
                            dcc.Input(id='yyIn', placeholder="yyyy", type='number', style={'background-color' : 'tranparent', 'height' : '28px', 'border-radius' : 8, 'margin-top' : '15px', 'width' : '62px', 'text-align' : 'center', 'fontFamily': 'Georgia, monospace'}, min = 1985),
                            html.Button('Search', id='search_button', style={'margin-left' : '8%', 'background-color' : 'transparent', 'height' : '30px', 'margin-top' : '15px', 'border-radius': 10})
                        ], style={'display' : 'flex', 'width' : '80%', 'justify-content': 'left', 'margin-left' : '1%', 'margin-bottom' : '-29px'}),
                        html.Div([
                            html.H6(children="log :", style={'margin-left' : '10px', 'margin-right' : '6px'}), html.H6(children=Temp_app["log-fileName"], id="log-fileName")
                        ], style={'display' : 'flex', 'fontFamily' : 'Georgia, monospace', 'color' : 'grey'})
                ], style={'fontFamily': 'Verdana, Sans-serif', 'margin-top' : '20%'}),

                #select information <cycle : interaction, flow, density>
                html.Div([
                    html.Div([
                        html.Button('<', id='leftSelect', style={'border-radius' : 3, 'background-color' : '#4d4d4d', 'color' : '#f2f2f2', 'font-weight' : 'bold', 'height' : '23px', 'margin-top' : '20px', 'margin-left' : '2%', 'margin-right' : '4%'}),
                        html.H3(children=Temp_app["select_image"][0][Temp_app["select_image"][1]], id="select_image", style={'width' : '100%', 'text-align' : 'center', 'border' : '3px', 'border' : '3px solid', 'border-radius' : 4, 'border-color' : '#f2f2f2', 'background-color' : '#f2f2f2'}),
                        html.Button('>', id='rightSelect', style={'border-radius' : 3, 'background-color' : '#4d4d4d', 'color' : '#f2f2f2', 'font-weight' : 'bold', 'height' : '23px', 'margin-top' : '20px', 'margin-left' : '4%'}),
                    ], style={'display' : 'flex', 'justify-content' : 'space-between', 'width' : '87%'})
                ], style={'fontFamily': 'Verdana, Sans-serif'})
                ], style={'margin-left' : '12%'}),
            
                #exit program
                html.Button('x quit', id='exit_button', style={'margin-top':'8%', 'margin-left':'13%', 'width':'50px', 'border-radius': 10, 'background-color' : 'transparent', 'height' : '30px'}),
            
                html.A('', href='#', id='url'),
        ], style={'justify-content' : 'center', 'width' : '40%', 'vertical-align' : 'center', 'height' : '100%'}),
        
        #right
        html.Div([
#             html.H2(children="Temp for Graph", style={'text-align' : 'center'}),
            html.Div([
                dcc.Graph(id='map-grid', 
                figure=fig
                )
            ], style={'width':'50%', 'margin-left':'8%'})
        ], style={'justify-content':'center', 'width' : '50%','verticalAlign': 'top', 'margin-top' : '4%'})
        
    ], style={'display' : 'flex', 'justify-content': 'center', 'width' : '100%'})
], style={'justify-content':'center', 'height':'100%', 'verticalAlign':'center', 'margin-top':'4%', 'margin-left':'8%'})

@app.callback(
    Output("log-fileName", 'children'),
    Output("select_image", 'children'),
    Output("map-grid",'figure'),
    Output('url', 'href'),
    Input("ddIn", "value"),
    Input("mmIn", "value"),
    Input("yyIn", "value"),
    Input("search_button", 'n_clicks'),
    Input("leftSelect", 'n_clicks'),
    Input("rightSelect", 'n_clicks'),
    Input("exit_button", 'n_clicks')
)

def update_output(input1, input2, input3, btn1, btn2, btn3, btn4):
    global fig
    if 'exit_button' == ctx.triggered_id:
        Temp_app["url"] = "about:blank"
        if doRun:
            subprocess.run('xdotool windowactivate $(wmctrl -lG | grep "Chrome" | cut -d ' ' -f1); xdotool key alt+F4;', shell=True)
        os.kill(os.getpid(), signal.SIGTERM)
    if 'ddIn' == ctx.triggered_id:
        if not input1 is None:
            Temp_app["log-fileName"] = f"Update date to {input1}"
            Temp_app["dd"] = input1
        if Temp_app["debug"]:
            print (f'dd {input1}')
    if 'mmIn' == ctx.triggered_id:
        if not input2 is None:
            Temp_app["log-fileName"] = f"Update month to {input2}"
            Temp_app["mm"] = input2
        if Temp_app["debug"]:
            print (f'mm {input2}')
    if 'yyIn' == ctx.triggered_id:
        if not input3 is None:
            Temp_app["log-fileName"] = f"Update year to {input3}"
            Temp_app["yy"] = input3
        if Temp_app["debug"]:
            print (f'yy {input3}')
    if 'search_button' == ctx.triggered_id:
        Temp_app["log-fileName"] = f"Finding file {Temp_app["dd"]}-{Temp_app["mm"]}-{Temp_app["yy"]}.csv"
        if Temp_app["debug"]:
            print (f'search {Temp_app["dd"]}-{Temp_app["mm"]}-{Temp_app["yy"]}')
        # ---  call open ---
        if creatProcessData(f"./save/{Temp_app["dd"]}-{Temp_app["mm"]}-{Temp_app["yy"]}.csv", debug = Temp_app["debug"]):
            Temp_app["log-fileName"] = f"Could not find : ./save/{Temp_app["dd"]}-{Temp_app["mm"]}-{Temp_app["yy"]}.csv"
        else :
            Temp_app["log-fileName"] = f"Open file successfully"
    if 'leftSelect' == ctx.triggered_id:
        if Temp_app["debug"]:
            print (f'left') 
        Temp_app["log-fileName"] = ud_select_image(False)
    if 'rightSelect' == ctx.triggered_id:
        if Temp_app["debug"]:
            print (f'right') 
        Temp_app["log-fileName"] = ud_select_image(True)       
    return Temp_app["log-fileName"], Temp_app["select_image"][0][Temp_app["select_image"][1]], fig, Temp_app["url"]

if __name__ == "__main__":
    webbrowser.open_new("http://127.0.0.1:8050/")
    sleep(50/1000)
    if doRun:
        subprocess.run('xdotool windowactivate $(wmctrl -lG | grep "Chrome" | cut -d ' ' -f1); xdotool key F11;', shell=True)
    app.run_server(debug=Temp_app["debug"])