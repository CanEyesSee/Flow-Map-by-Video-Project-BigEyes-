from platform import system
doRun = True
## check os
if system() != "Linux":
    print("This code is designed for Linux + GNU base Debian package")
    doRun = False
    # quit()
    
import cv2
import os
import numpy as np
import pandas as pd
from ultralytics import YOLO
from PIL import Image
from dash import Dash, dcc, html, Input, Output, ctx
import dash
import matplotlib.pyplot as plt
import math
import webbrowser
import subprocess
import signal
from time import sleep

df, raw = pd.array(list()), np.empty((1,1))
try : 
    df = pd.read_csv('./Temp/map.csv')
    raw = df.to_numpy()
except Exception as e:
    print(f"Err : {e}")
    print("If map file not has been created, This might cause bad behavior. The program will stop from this step...")
    quit()
    
model = YOLO("./model/yolov8n.pt")

Map = np.zeros((int(raw[0][0]),int(raw[0][1])))
for i in range(int(raw[0][0])):
    for j in range(int(raw[0][1])):
        Map[i][j] = raw[i][j+2+int(raw[0][1])]
Output = np.zeros((int(raw[0][0]),int(raw[0][1])))
for i in range(int(raw[0][0])):
    for j in range(int(raw[0][1])):
        Output[i][j] = raw[i][j+2+int(raw[0][1])*2]
        
Camera = list(map(int,list(np.unique(Map))))
Camera.pop(0)

def detect_people(frame, conf: float=0.2, Class: int=0, debug: bool=False):
    results = model(frame, verbose=debug)
    Cls = results[0].boxes.cls.cpu().numpy()
    Score = results[0].boxes.conf.cpu().numpy()
    Detections = results[0].boxes.xyxy.cpu().numpy()
    detecPer = list()
    for i in range(len(Detections)):
        if int(Cls[i]) == Class and float(Score[i]) >= conf:
            detecPer.append(Detections[i])
    people_count = len(detecPer)
    return people_count, detecPer

def videoAnalysis(video: str,debug: bool=False, addMP4: bool=True, addLoc: str='./insert/', fps: int = 5, returnINT: bool=True, printFeed: bool=False, color: list[int,int,int]= [0, 255, 0], size: list[int,int]=[800,600], multiply: float=1.345):
    video_name = addLoc + video + '.mp4' if addMP4 else ''
    cap = cv2.VideoCapture(video_name)
    Temp = 0
    frame_count, maxFrame, First = 0, int(math.floor(cap.get(cv2.CAP_PROP_FRAME_COUNT)/fps)), True
    while True:
        ret, frame = cap.read()
        if not ret:
            if debug:
                print("End process")
            break
        if debug:
            print(f"Frame : {frame_count}")
        if int(frame_count) % fps == 0:
            frame = cv2.resize(frame, size)
            many, detections = detect_people(frame, debug=debug)
            
            if printFeed:
                img = frame
                for (x1, y1, x2, y2) in detections:
                        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                        label = "Person"
                        cv2.putText(img, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
#                 ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                if First:
                    plt.show()
                    First = False
                else :
#                     plt.draw()
                    plt.show()
#                 image = Image.fromarray(img)
#                 image.show()
#                 print('\033[H\033[J')
            Temp += many/maxFrame
            if debug:
                print(f"{many} -> {Temp}")
        frame_count += 1
    cap.release()
    if returnINT:
        return int(Temp*multiply)
    else :
        return Temp*multiply
    
app = Dash(__name__)

# size of array
num_rows = int(raw[0][0])
num_cols = int(raw[0][1])

# shape of array
ratioArr = num_cols/num_rows
sizeRow = 100*5/num_rows
# sizeRow = 100
sizeCol = ratioArr*500 

if sizeCol > 500:
    sizeRow = sizeRow * 500/sizeCol
    sizeCol = 500
    
# setting
Temp_app ={
        'debug':False,
        'camera-place':['1','3','4'],
        'color-able':(211,211,211),
        'color-unable':(105,105,105),
        'color-camera':(255,165,0),
        'color-enable':(173,255,47),
        'color-rendered':(85,107,47),
        'font-color-able':(192,192,192),
        'font-color-unable':(120,120,120),
        'font-color-camera':(8,9,7),
        'font-color-rendered':(154,205,50),
        'log-fileName':"🟢",
        'log-ok':"🟢",
        'log-loading':"⏳",
        'log-done':"✅",
        'log-fail':"⛔",
        'process-state':False,
        "dd":1, "mm":1, "yy":1985
    }

queue = [list(),list()]
def updateCell(buttons ,confix: bool=False, cordinate: list[int,int]=(0,0), button_ID = "button_1_1", color=(0,0,0)):
    global raw, Map, Temp_app, Camera, Output, queue
    if Temp_app['debug']:
        print("In function: updateCell")
    ratio = 100/int(raw[0][1])
    setStyle = {'width':f'{ratio}%', 'height':'100%'}
    # update value on mode camera change
    if confix:
        new_buttons = []
        for row_buttons in buttons:
            Row_buttons = row_buttons.children
            new_row_buttons = []
            for button in Row_buttons:
                if button.id == button_ID:
                    new_color = '#%02x%02x%02x' % color
                    new_button = html.Button(button.children, id=button_ID, style={'backgroundColor': new_color}|setStyle)
                    new_row_buttons.append(new_button)
                else:
                    new_row_buttons.append(button)
            new_buttons.append(html.Div(new_row_buttons))
        buttons = new_buttons
        
    #  change color and children
    row = -1
    new_buttons = []
    for row_buttons in buttons:
            row += 1
            column = -1
            Row_buttons = row_buttons.children
            new_row_buttons = []
            for button in Row_buttons:
                column += 1
                button_id = button.id
                if not str(raw[row][column+2])[0] in Temp_app['camera-place']:
                    new_color = '#%02x%02x%02x' % Temp_app['color-unable']
                    new_button = html.Button("%02d"%int(raw[row][column+2]), id=button_id, style={'backgroundColor':new_color, 'color':'#%02x%02x%02x' % Temp_app['font-color-unable']}|setStyle)
                    new_row_buttons.append(new_button)
                else :
                    if not Map[row][column] in Camera:
                        new_color = '#%02x%02x%02x' % Temp_app['color-able']
                        new_button = html.Button("%02d"%int(raw[row][column+2]), id=button_id, style={'backgroundColor':new_color, 'color':'#%02x%02x%02x' % Temp_app['font-color-able']}|setStyle)
                        new_row_buttons.append(new_button)
                    else :
                        text_color = Temp_app['font-color-camera']
                        if int(Output[row][column]) != 0:
                            text_color = Temp_app['font-color-rendered']
#                             print("Test")
                        if not Map[row][column] in queue[0] and int(Output[row][column]) == 0:
                            new_color = '#%02x%02x%02x' % Temp_app['color-camera']
                            new_button = html.Button("%02d"%int(Map[row][column]), id=button_id, style={'backgroundColor':new_color, 'color':'#%02x%02x%02x' % text_color}|setStyle)
                            new_row_buttons.append(new_button)
                        elif Map[row][column] in queue[0]:
                            new_color = '#%02x%02x%02x' % Temp_app['color-enable']
                            new_button = html.Button("%02d"%int(Map[row][column]), id=button_id, style={'backgroundColor':new_color, 'color':'#%02x%02x%02x' % text_color}|setStyle)
                            new_row_buttons.append(new_button)
                        else :
                            new_color = '#%02x%02x%02x' % Temp_app['color-rendered']
                            new_button = html.Button("%02d"%int(Map[row][column]), id=button_id, style={'backgroundColor':new_color, 'color':'#%02x%02x%02x' % text_color}|setStyle)
                            new_row_buttons.append(new_button)
                        
            new_buttons.append(html.Div(new_row_buttons, style={'width':'100%', 'height':'100%', 'justify-content':'center'}))
    buttons = new_buttons
#     if Temp_app['debug']:
#         print(buttons)
    return buttons
def updateData(buttons, button_id):
    global raw, Map, Temp_app, Camera, Output, queue
    row, column, found = 0, 0, False
    for row_buttons in buttons:
        column = 0
        Row_buttons = row_buttons.children
        for button in Row_buttons:
            if button.id == button_id:
                found = True
                break
            column += 1
        if found:
            break
        row += 1
    if not found:
        if Temp_app['debug']:
            print("Could not find button")
        return buttons
    
    # check if it is select able
    if not Map[row][column] in Camera:
        if Temp_app['debug']:
            print("This block is not a camera block")
        return buttons
    else :
        # check if is it selected or not
        if not (row,column) in queue[1]:
            # add in queue
            queue[0].append(Map[row][column])
            queue[1].append((row,column))
        else :
            # remove from queue
            index = queue[1].index((row,column))
            queue[1].pop(index)
            queue[0].pop(index)
    return updateCell(buttons)

def anaVideo(que, debug: bool=False):
    global Temp_app
    if not Temp_app['process-state']:
        global Output
        Temp_app['process-state'] = True
        List = list(que)
        Temp_app['log-fileName'] = Temp_app['log-loading']
        for i in range(len(List[0])):
            cam, pos = int(List[0][i]), List[1][i]
            if debug:
                print(f"{cam} : {pos}")
#             Output[pos[0]][pos[1]] = videoAnalysis(f'{cam}', printFeed=debug)
            Temp_app['log-fileName'] = Temp_app['log-loading'] + str(cam)
            Output[pos[0]][pos[1]] = videoAnalysis(f'{cam}')
            if debug:
                print(f"Output -> {Output[pos[0]][pos[1]]}")
            Temp_app['log-fileName'] = Temp_app['log-done']+str(cam)
        Temp_app['log-fileName'] = Temp_app['log-ok']
        Temp_app['process-state'] = False
#         que = [list(),list()]

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

def saveData(data: str):
    global Temp_app, Map, Output, Camera, raw
    Temp_app['log-fileName'] = Temp_app['log-loading']
    
    # check if is it full fill?
    for row in range(int(raw[0][0])):
        for column in range(int(raw[0][1])):
            if Map[row][column] in Camera:
                if Output[row][column] == 0:
                    Temp_app['log-fileName'] = Temp_app['log-fail']
                    if Temp_app['debug']:
                        print("Fail to save due to missing info")
                    return False
                
    # save file to raw and sent back to save file
    for row in range(int(raw[0][0])):
        for column in range(int(raw[0][1])):
            raw[row][column+2+int(raw[0][1])*2] = Output[row][column]
    
    saveMap(raw, df, asNew=True, location="./save/"+data+".csv")
    Temp_app['log-fileName'] = Temp_app['log-done']
    if Temp_app['debug']:
        print("Done saving")
    return True

# create button array
button_ids = [[f"button_{i}_{j}" for j in range(num_cols)] for i in range(num_rows)]
buttons = []
for row_idx in range(num_rows):
    row_buttons = []
    for col_idx in range(num_cols):
        button_id = button_ids[row_idx][col_idx]
        row_buttons.append(html.Button("0", id=button_id, style={'backgroundColor': 'black'}))
    buttons.append(html.Div(row_buttons))
    
buttons = updateCell(buttons)

app.layout = html.Div([
    html.Div([
        # left
        html.Div([
            # logo
            html.Div([
                html.H1(children="👁️"),
                html.H1(children="|", style={'margin-left' : '0.25%', 'margin-right' : '0.5%'}),
                html.Table([
                    html.H5(children="Big"),
                    html.H3(children="Eyes", style={'margin-top' : '-50%'})
                ], style={'justify-content' : 'left', 'fontFamily': 'Verdana, Sans-serif'})
            ], style={'display' : 'flex', 'justify-content' : 'center', 'margin-top':'5%'}),
            
            # render button & progress
            html.Div([
                html.Button("Analyse",id='analyse', style={'background-color' : 'tranparent', 'border-radius' : 8, 'width':'40%', 'height':'30px', 'margin-top':'20%', 'text-align' : 'center', 'fontFamily': 'Georgia, monospace'}),
                html.H6(children=Temp_app["log-fileName"], id="log-fileName", style={'margin-left' : '1%', 'margin-right' : '1%', 'margin-top':'24%'}),
                dcc.Interval(id='interval-component', interval=500, n_intervals=0),
                html.H1(children=":", style={'margin-left' : '3%', 'margin-right' : '3%', 'margin-top':'18.4%'}),
                html.Button("🧹", id="clear", style={'background-color' : 'tranparent', 'border-radius' : 8, 'width':'10.2%', 'height':'30px', 'margin-top':'20%', 'margin-left':'1%', 'text-align' : 'center', 'fontFamily': 'Georgia, monospace'}),
                html.Button("🗑️", id="remove", style={'background-color' : 'tranparent', 'border-radius' : 8, 'width':'11%', 'height':'30px', 'margin-top':'20%', 'margin-left':'2%', 'text-align' : 'center', 'fontFamily': 'Georgia, monospace'}),
                html.Button("⟳", id="reload", style={'background-color' : 'tranparent', 'border-radius' : 8, 'width':'11.5%', 'height':'30px', 'margin-top':'20%', 'margin-left':'2%', 'text-align' : 'center', 'fontFamily': 'Georgia, monospace'})
            ], style={'justify-content':'left', 'display':'flex'}),
            
            # save
            html.Div([
                html.H3(children="Enter Date 📆", style={'margin-bottom' : '-6.5px', 'text-align' : 'left', 'margin-left' : '13%'}),
                html.Div([
                    dcc.Input(id='ddIn', placeholder="dd", type='number', style={'background-color' : 'tranparent', 'height' : '28px', 'border-radius' : 8, 'margin-top' : '15px', 'width' : '40px', 'text-align' : 'center', 'fontFamily': 'Georgia, monospace'}, min = 1, max = 31),
                    html.H3(children="/", style={'margin-right' : '10px', 'margin-left' : '10px'}),
                    dcc.Input(id='mmIn', placeholder="mm", type='number', style={'background-color' : 'tranparent', 'height' : '28px', 'border-radius' : 8, 'margin-top' : '15px', 'width' : '40px', 'text-align' : 'center', 'fontFamily': 'Georgia, monospace'}, min = 1, max = 12),
                    html.H3(children="/", style={'margin-right' : '10px', 'margin-left' : '10px'}),
                    dcc.Input(id='yyIn', placeholder="yyyy", type='number', style={'background-color' : 'tranparent', 'height' : '28px', 'border-radius' : 8, 'margin-top' : '15px', 'width' : '62px', 'text-align' : 'center', 'fontFamily': 'Georgia, monospace'}, min = 1985),
                    html.Button('Save', id='save_button', style={'margin-left' : '8%', 'background-color' : 'transparent', 'height' : '30px', 'margin-top' : '15px', 'border-radius': 10}),
                    html.Button('X', id='exit_button', style={'margin-left' : '4%', 'background-color' : 'transparent', 'height' : '30px', 'margin-top' : '15px', 'border-radius': 10, 'width':'38px'})
                ], style={'display' : 'flex', 'width' : '80%', 'justify-content': 'left', 'margin-left' : '1%', 'margin-bottom' : '-29px'})
            ], style={'margin-top':'30%'})
            
        ], style={'width':'37%', 'margin-left':'4%'}),
        
        # right
        html.Div([html.Div([html.Div(buttons, id='button-container', style={'width':'100%', 'height':'100%', 'justify-content':'center'})],style={'width':f'{sizeCol}px', 'height':f'{sizeRow}px', 'margin-left':'10%', 'margin-right':'1%', 'margin-top':'5%'})], style={'width':'60%'})
    ], style={'display':'flex'})
], style={'width':'100%', 'justify-content':'center'})

# button selection
@app.callback(
    dash.dependencies.Output('button-container', 'children'),
    Input('clear', 'n_clicks'),
    Input('remove', 'n_clicks'),
    Input('analyse', 'n_clicks'),
    Input('reload', 'n_clicks'),
    [dash.dependencies.Input(button_id, 'n_clicks') for row in button_ids for button_id in row]
)
def update_button(*args):
#     global buttons, queue, Output, Camera
    global df, raw, model, Map, Output, Camera, num_rows, num_cols, ratioArr, sizeRow, num_cols, queue, buttons
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return buttons
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
#     print(button_id)
    
    if   button_id == 'clear':
        if Temp_app['debug']:
            print("button clear has been selected")
        
        if len(queue[0]) > 0: 
            queue = [list(),list()]
        else :
            for cam in Camera:
                queue[0].append(cam)
                row, column, temp = None, None, False
                for row in range(int(raw[0][0])):
                    for column in range(int(raw[0][1])):
                        if Map[row][column] == cam:
                            temp = True
                            break
                    if temp:
                        break
                queue[1].append((row,column))
                if Temp_app['debug']:
                    print("button clear[add option] has been selected")
        
        buttons = updateCell(buttons)
        
    elif button_id == 'remove':
        if Temp_app['debug']:
            print("button reset has been selected")
        
        Output = np.zeros_like(Output)
        
        buttons = updateCell(buttons)
        
    elif button_id == 'analyse':
        if Temp_app['debug']:
            print("button analyse has been selected")
        
        anaVideo(queue, debug=Temp_app['debug'])
        while Temp_app['process-state']:
            pass        
        queue = [list(),list()]
        buttons = updateCell(buttons)
        
    elif button_id == 'reload':
        if Temp_app['debug']:
            print("button reload has been selected")
            
        tempDF = df.copy()
        tempRaw = np.copy(raw)
        df, raw = pd.array(list()), np.empty((1,1))
        try : 
            df = pd.read_csv('./Temp/map.csv')
            raw = df.to_numpy()
        except Exception as e:
            print(f"Err : {e}")
            print("If map file not has been created, This might cause bad behavior. The program will stop from this step...")
#             quit()
            df = tempDF.copy()
            raw = np.copy(tempRaw)
        
        try :
            if raw[0][0] != tempRaw[0][0] or raw[0][1] != tempRaw[0][1]:
                if Temp_app['debug']:
                    print("File size does not the same !!")
                df = tempDF.copy()
                raw = np.copy(tempRaw)
        except Exception as e:
            print(f"Err : {e}")
            print("If map file not has been created, This might cause bad behavior. The program will stop from this step...")
            df = tempDF.copy()
            raw = np.copy(tempRaw)
        
        model = YOLO("./model/yolov8n.pt")
        
        Map = np.zeros((int(raw[0][0]),int(raw[0][1])))
        for i in range(int(raw[0][0])):
            for j in range(int(raw[0][1])):
                Map[i][j] = raw[i][j+2+int(raw[0][1])]
        Output = np.zeros((int(raw[0][0]),int(raw[0][1])))
        for i in range(int(raw[0][0])):
            for j in range(int(raw[0][1])):
                Output[i][j] = raw[i][j+2+int(raw[0][1])*2]
                
        Camera = list(map(int,list(np.unique(Map))))
        Camera.pop(0)
        
        num_rows = int(raw[0][0])
        num_cols = int(raw[0][1])
        
        ratioArr = num_cols/num_rows
        sizeRow = 100*5/num_rows
        sizeCol = ratioArr*500 
        if sizeCol > 500:
            sizeRow = sizeRow * 500/sizeCol
            sizeCol = 500

        queue = [list(),list()]
        
        button_ids = [[f"button_{i}_{j}" for j in range(num_cols)] for i in range(num_rows)]
        buttons = []
        for row_idx in range(num_rows):
            row_buttons = []
            for col_idx in range(num_cols):
                button_id = button_ids[row_idx][col_idx]
                row_buttons.append(html.Button("0", id=button_id, style={'backgroundColor': 'black'}))
            buttons.append(html.Div(row_buttons))

        buttons = updateCell(buttons)
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        buttons = updateData(buttons, button_id)
        
    return buttons#, Temp_app["log-fileName"]

# state
@app.callback(
    dash.dependencies.Output('log-fileName', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_log(n_int):
    return Temp_app['log-fileName']

# save
@app.callback(
    Input("ddIn", "value"),
    Input("mmIn", "value"),
    Input("yyIn", "value"),
    Input("save_button", 'n_clicks'),
    Input('exit_button','n_clicks')
)
def update_save(in1, in2, in3, btn1, btn2):
    if 'ddIn' == ctx.triggered_id:
        if not in1 is None:
            Temp_app["dd"] = in1
        if Temp_app["debug"]:
            print (f'dd {in1}')
    if 'mmIn' == ctx.triggered_id:
        if not in2 is None:
            Temp_app["mm"] = in2
        if Temp_app["debug"]:
            print (f'mm {in2}')
    if 'yyIn' == ctx.triggered_id:
        if not in3 is None:
            Temp_app["yy"] = in3
        if Temp_app["debug"]:
            print (f'yy {in3}')
    if 'save_button' == ctx.triggered_id:
        if Temp_app["debug"]:
            print (f'save {Temp_app["dd"]}-{Temp_app["mm"]}-{Temp_app["yy"]}')
        saveData(f'{Temp_app["dd"]}-{Temp_app["mm"]}-{Temp_app["yy"]}')
    if 'exit_button' == ctx.triggered_id:
        if Temp_app['debug']:
            print("Exit bye~")
        if doRun:
            subprocess.run('xdotool windowactivate $(wmctrl -lG | grep "Chrome" | cut -d ' ' -f1); xdotool key alt+F4;', shell=True)
        os.kill(os.getpid(), signal.SIGTERM)
        quit()
        
# start GUI
if __name__ == '__main__':
    webbrowser.open_new("http://127.0.0.1:8050/")
    sleep(50/1000)
    if doRun:
        subprocess.run('xdotool windowactivate $(wmctrl -lG | grep "Chrome" | cut -d ' ' -f1); xdotool key F11;', shell=True)
        pass
    app.run_server(debug=Temp_app['debug'])