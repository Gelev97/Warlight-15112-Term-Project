from tkinter import *
import random, string, copy, math, time
from PIL import Image, ImageFilter
import sys
import threading
import decimal
import json

####################################
# Helper Function
####################################

# cited from 15-112 Website
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

def rgbString(red, green, blue):
    return "#%02x%02x%02x" % (red, green, blue)

def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def AS_HeightAndColor():
    # used to contorl the atttack sequence box color and place
    (count,margin,length,witdh,start) = (0,20,39,8,60)
    height = []
    for index in range(length):
        height.append(((start + count * margin - witdh), 
            (start + count * margin + witdh), start + count * margin))
        count += 1
    return height

def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)

def writeFile_Type(path, contents):
    # use json to save dictionary and list
    with open(path, "wt") as f:
        json.dump(contents, f)

def readFile_Type(path):
    # use json to read dictionary and list
    with open(path, "rt") as f:
        return json.load(f)

# cited from 15-112 Website
def callWithLargeStack(f,*args):
    threading.stack_size(2**27)  # 64MB stack
    sys.setrecursionlimit(2**27) # will hit 64MB stack limit first
    # need new thread to get the redefined stack size
    def wrappedFn(resultWrapper): resultWrapper[0] = f(*args)
    resultWrapper = [None]
    thread = threading.Thread(target=f, args=args)
    thread = threading.Thread(target=wrappedFn, args=[resultWrapper])
    thread.start()
    thread.join()
    return resultWrapper[0]

def paintBucket_Inside(original,pix,rgb,inside,WALL):
    (cx,cy) = original
    callWithLargeStack(paintBucket_FloodFill_Inside,cx,cy,original,pix,rgb,
        inside,WALL)

# Floodfill Structure cited from 15-112, Chandged a lot
def paintBucket_FloodFill_Inside(cx,cy,original,pix,rgb,inside,WALL):
    (width, height,pixel) = (800,680,3)
    if ((cx < 0) or (cx >= width) or
        (cy < 0) or (cy >= height)):
        return # off-board!
    if((cx,cy) in WALL[original]):
        return # hit a different color
    if ((cx,cy) in inside[original] and (cx,cy) != original):
        return # already change color
    # "fill" this cell
    if(original not in inside):
        inside[original] = {(cx,cy)}
    inside[original].add((cx,cy))
    # then recursively fill its neighbors
    paintBucket_FloodFill_Inside(cx+pixel,cy,original,pix,rgb,inside,WALL)
    paintBucket_FloodFill_Inside(cx-pixel,cy,original,pix,rgb,inside,WALL)
    paintBucket_FloodFill_Inside(cx,cy-pixel,original,pix,rgb,inside,WALL)
    paintBucket_FloodFill_Inside(cx,cy+pixel,original,pix,rgb,inside,WALL)

def paintBucket_Border(original,pix,rgb,border,WALL,inside):
    # prevent recursion maximum
    (cx,cy) = original
    callWithLargeStack(paintBucket_FloodFill_Border,cx,cy,original,pix,rgb,
        border,WALL,inside)

# Floodfill Structure cited from 15-112, Chandged a lot
def paintBucket_FloodFill_Border(cx,cy,original,pix,rgb,border,WALL,inside):
    (width, height,pixel) = (800, 680, 3)
    # off-board!
    if ((cx < 0) or (cx >= width) or(cy < 0) or (cy >= height)):return 
    current_Color = pix[cx,cy]
    if (current_Color != pix[original[0],original[1]]):
        (r,g,b) = rgb.getpixel((cx, cy))
        if(original not in border):border[original] = {(cx,cy,r,g,b)}
        border[original].add((cx,cy,r,g,b))
        count = 0
        while(count < pixel):
            points = [(cx,cy-count),(cx-count,cy),(cx,cy),(cx+count,cy),
                        (cx,cy+count)]
            for item in points:
                if(original not in WALL):WALL[original] = {item}
                WALL[original].add(item)
            count += 1
        return # hit a different color
    # already change color
    if ((cx,cy) in inside[original] and (cx,cy) != original):return 
    # "fill" this cell
    if(original not in inside):inside[original] = {(cx,cy)}
    inside[original].add((cx,cy))
    # then recursively fill its neighbors
    paintBucket_FloodFill_Border(cx+1,cy,original,pix,rgb,border,WALL,inside)
    paintBucket_FloodFill_Border(cx-1,cy,original,pix,rgb,border,WALL,inside)
    paintBucket_FloodFill_Border(cx,cy-1,original,pix,rgb,border,WALL,inside)
    paintBucket_FloodFill_Border(cx,cy+1,original,pix,rgb,border,WALL,inside)

def playGameBackGround(canvas, data):
    if(data.playerFlag_MF == -1):
        canvas.create_text(1000, 70, text = "It's player 2's turn",
            fill = "white", font = "Times 20 bold")
    if(data.playerFlag_MF == 1):
        canvas.create_text(1000, 70, text = "It's player 1 's turn",
            fill = "white", font = "Times 20 bold")
    canvas.create_text(960, 110, text = "1. Deploy", fill = "white", 
        font = "Times 20 bold")
    canvas.create_text(998, 150, text = "2. Attack/Transfer", fill = "white", 
         font = "Times 20 bold")
    canvas.create_text(965, 190, text = "3. Confirm", fill = "white", 
         font = "Times 20 bold") 
    canvas.create_image(955, 330,image = data.image_Button)
    canvas.create_text(955, 330, text = "Start Over", fill = "white", 
         font = "Times 16") 
    canvas.create_image(1042, 330, image = data.image_Button)
    canvas.create_text(1042, 330, text = "Surrender", fill = "white", 
         font = "Times 16") 
    canvas.create_image(955, 390, image = data.image_Button)
    canvas.create_text(955, 390, text = "Save Game", fill = "white", 
         font = "Times 16") 
    canvas.create_image(1042, 390, image = data.image_Button)
    canvas.create_text(1042, 390, text = "Map Info", fill = "white", 
         font = "Times 16") 
    canvas.create_image(1000, 510, image = data.image_Button)
    canvas.create_text(1000, 510, text = "Exit", fill = "white", 
         font = "Times 20")

def stringToTuple(contentsRead):
    # get data from my text
    result, part, answer = ([], "", [])
    for item in contentsRead:
        for index in range(len(item)):
            if(item[index].isdigit()):
                part += item[index]
            elif(item[index] == "," or item[index] == ")"):
                result.append(int(part))
                part = ""
            else:part = ""
        answer.append(tuple(result))
        result = []
    return answer

def startOver(data):
    # use to reset data ith the call of start over button
    data.selectedFlag_AMF = 0
    data.AS_Height = AS_HeightAndColor()
    (data.AS_selected,data.luck) = ([],{})
    (data.tempC1,data.tempC2,data.cache)  = ([],[],[])
    (data.C_MF_Color,data.mode) = ("white", "playGame_Deploy_MF")
    data.player.selected = None
    data.player.attackNumber = {}
    data.player.attack_areas.clear()
    data.player.Already_Deploy = 0
    Map = data.WorldMap
    for index in data.player1_MF.center:
        territory = Map.centers[index]
        Map.attack_value[territory] = Map.deploy_value[territory]
        Map.value[territory] = Map.deploy_value[territory]
    for index in data.player2_MF.center:
        territory = Map.centers[index]
        Map.attack_value[territory] = Map.deploy_value[territory]
        Map.value[territory] = Map.deploy_value[territory]

def dictValueKey(test):
    # save dict into text
    result = {}
    for key in test:
        if(test[key] not in result):
            result[test[key]] = {key}
        result[test[key]].add(key)
    for key in result:
        result[key] = list(result[key])
    return result

def decodeDict(test):
    # get dict from text
    result = {}
    for key in test:
        for item in test[key]:
            if(isinstance(item[0],list)):
                result[(tuple(item[0]),tuple(item[1]))] = int(key)
            else:
                result[tuple(item)] = int(key)
    return result

def SaveGame(data):
    # save my data to text
    contents = [None] * 16
    #player
    contents[0] = data.player1_MF.center
    contents[1] = data.player1_MF.Already_Deploy
    contents[2] = data.player1_MF.total_Deploy 
    contents[3] = data.player1_MF.attack_areas 
    contents[4] = dictValueKey(data.player1_MF.attackNumber)
    contents[5] = data.player2_MF.center
    contents[6] = data.player2_MF.Already_Deploy 
    contents[7] = data.player2_MF.total_Deploy 
    contents[8] = data.player2_MF.attack_areas 
    contents[9] = dictValueKey(data.player2_MF.attackNumber)
    #mode
    contents[10] = data.playerFlag_MF
    contents[11] = data.selectedFlag_AMF
    #map
    contents[12] = dictValueKey(data.WorldMap.value)
    contents[13] = dictValueKey(data.WorldMap.deploy_value)
    contents[14] = dictValueKey(data.WorldMap.attack_value)
    contents[15] = data.mode
    ChooseFile(data, contents)

def ChooseFile(data, contents):
    # correspond to the correct file with click
    if(data.LoadGame_flag == 0):writeFile_Type("File0.txt", contents)
    if(data.LoadGame_flag == 1):writeFile_Type("File1.txt", contents)
    if(data.LoadGame_flag == 2):writeFile_Type("File2.txt", contents)
    if(data.LoadGame_flag == 3):writeFile_Type("File3.txt", contents)
    if(data.LoadGame_flag == 4):writeFile_Type("File4.txt", contents)
    if(data.LoadGame_flag == 5):writeFile_Type("File5.txt", contents)

def LoadFileSet_Helper(data):
    # try to find what files are stored and displayed in load Game
    files = ["file0","file1","file2","file3","file4","file5"]
    data.LoadFileSet = set()
    for index in range(len(files)):
        try:
            readFile_Type(files[index] + ".txt")
            data.LoadFileSet.add(index)
        except:
            print("HA-HA")

####################################
# splashScreen mode
####################################

# To draw opening animation
def drawAnimationSS_initial(canvas, data):
    plot = []
    for index in data.index_SS:
        (cx,cy) = data.startScreenXY[index]
        plot.append((cx,cy,index))
    for item in plot:
        (x,y) = (item[0], item[1])
        if(item[2] % 2 == 0):
            canvas.create_oval(x, y, x + data.r, y + data.r, fill = "red")
        else:
            canvas.create_oval(x, y, x + data.r, y + data.r, fill = "blue")

####################################
# help mode
####################################
# Five help screen instrucitons

def drawHelp0(canvas,data):
    cx = data.width//2
    (margin, cy) = (40,220)
    canvas.create_text(cx, cy, text = "Welcome to Warlight",font = "Times 24")
    canvas.create_text(cx, cy+margin, text = "This is a Turn-based strategic" 
        + " game", font = "Times 24")
    canvas.create_text(cx, cy+margin*2, text = "Each player has three stages" 
        + " and a replay in one turn", font = "Times 24")
    canvas.create_text(cx,cy+margin*3,text="The goal of this game is to conquer" 
        + " all opponent's territories", font = "Times 24")
    canvas.create_text(cx,cy+margin*4,text="player can save game when he or she" 
        + " need to rest", font = "Times 24")
    canvas.create_text(cx, cy+margin*5, text ="player can also surrender when" 
        + " he or she is going to loose", font = "Times 24")
    canvas.create_text(cx, cy+margin*6, text ="Furthermore, the mysterious fog" 
        + " and the real world map makes this game fabulous", font = "Times 24")

def drawHelp1(canvas,data):
    cx = data.width//2
    (margin, cy) = (40,180)
    canvas.create_text(cx, cy, text = "Deploy stage",font = "Times 30")
    canvas.create_text(cx, cy+margin, text = "Total deploy armies —"
        + " The whole army which a player can deploy in one turn", 
        font = "Times 24")
    canvas.create_text(cx, cy+margin*2, text ="Bonus — If player have captured" 
        + " all territories with same colored borders" , font = "Times 24")
    canvas.create_text(cx,cy+margin*3,text="\this total deploy armies increase" 
        + " by these territories bonus next turn", font = "Times 24")
    canvas.create_text(cx-margin*2, cy+margin*4, text ="Fog — Impede player" 
        + " from seeing non-adjacent territory", font = "Times 24")
    canvas.create_text(cx, cy+margin*5, text ="In this turn, a player needs to" 
        + " intelligently deploy all his or her total deploy armies.", 
        font = "Times 24")
    canvas.create_text(cx, cy+margin*6, text ="Player can only deploy armies, " 
        + "which means he or she cannot decrease" , font = "Times 24")
    canvas.create_text(cx, cy+margin*7, text = "his or her armies’ value in" 
        + "owned territory during this stage", font = "Times 24")

def drawHelp2(canvas,data):
    cx = data.width//2
    (margin, cy) = (40,170)
    canvas.create_text(cx, cy, text = "Attack stage",font = "Times 30")
    canvas.create_text(cx-margin*4, cy+margin, text = "Attack — Attack will" 
        + "calculate in sequence", font = "Times 24")
    canvas.create_text(cx, cy+margin*2, text ="Attack Sequence — player1’ first" 
        + " attack followed by player2’s first two attacks", font = "Times 24")
    canvas.create_text(cx, cy+margin*3, text = "then player1’s next two attacks" 
        +  " , until one player run out of moves" , font = "Times 24") 
    canvas.create_text(cx,cy+margin*4,text="The player can decide whether to" +
        " attack or transfer an adjacent territory", font = "Times 24")
    canvas.create_text(cx, cy+margin*5, text ="In this turn, a player needs to" 
        + " intelligently deploy all his or her total deploy armies.", 
        font = "Times 24")
    canvas.create_text(cx, cy+margin*6, text ="The player must always leave one"
    + " army on its territory" , font = "Times 24")
    canvas.create_text(cx, cy+margin*7, text = "Attack sequence is very"  +
     " important for each player", font = "Times 24")
    canvas.create_text(cx, cy+margin*8, text = "so take more time o think"
    + " about it", font = "Times 24")

def drawHelp3(canvas,data):
    cx = data.width//2
    (margin, cy) = (50,200)
    canvas.create_text(cx, cy, text = "Confirm Stage",font = "Times 30")
    canvas.create_text(cx, cy+margin, text = "Player must deploy all you armies"
        + " before entering next turn", font = "Times 24")
    canvas.create_text(cx, cy+margin*2, text ="Replay",font = "Times 30")
    canvas.create_text(cx, cy+margin*3, text="Before each player’s next turn," 
    + " there will be a display of step by step animation ",font="Times 24")
    canvas.create_text(cx, cy+margin*4, text ="Player can use forward" 
        + "and back to control the steps" , font = "Times 24")
    canvas.create_text(cx, cy+margin*5, text ="Also, he or she can use skip" 
        + " button to directly go to net turn", font = "Times 24")
    canvas.create_text(cx, cy+margin*6, text ="However, he or she might lose" 
    + "the best chance to gather information of opponent", font = "Times 24")

def drawHelp4(canvas,data):
    cx = data.width//2
    (margin, cy) = (50,200)
    canvas.create_text(cx, cy, text = "Load Game",font = "Times 30")
    canvas.create_text(cx, cy+margin, text = "You can save game in any of these" 
        + " three stages", font = "Times 24")
    canvas.create_text(cx, cy+margin*2, text = "Click save game button and" + 
        "choose one file to save" , font = "Times 24")
    canvas.create_text(cx,cy+margin*3, text= "Then player can reload the battle" 
        + "in the load game slots and start load game", font = "Times 24")
    canvas.create_text(cx, cy+margin*4, text = "Map info", font = "Times 30")
    canvas.create_text(cx, cy+margin*5, text = "Map info button provides player" 
        + "a chance to", font = "Times 24")
    canvas.create_text(cx, cy+margin*6, text = "see the index of map and plan" 
        + "their attack", font = "Times 24")

####################################
# LOAD GAME
####################################
# Used to display available load file name on board.
def drawloadFile(canvas, data):
    for item in data.LoadFileSet:
        if(item == 0): 
            canvas.create_text(300, 240, text = "FILE 0", font ="Times 20 bold")
        if(item == 1): 
            canvas.create_text(300, 390, text = "FILE 1", font ="Times 20 bold")
        if(item == 2): 
            canvas.create_text(300, 520, text = "FILE 2", font ="Times 20 bold")
        if(item == 3): 
            canvas.create_text(800, 240, text = "FILE 3", font ="Times 20 bold")
        if(item == 4): 
            canvas.create_text(800, 390, text = "FILE 4", font = "Times 20 bold")
        if(item == 5): 
            canvas.create_text(800, 520, text = "FILE 5", font = "Times 20 bold")

# change json list data type to tuple
def Totuple(contents):
    result = []
    for item in contents:
        temp = (tuple(item[0]),tuple(item[1]))
        result.append(temp)
    return result

# Restore my data in text back to game
def openLoad(data,file):
    contents = readFile_Type(file)
    data.player1_MF.center = contents[0] 
    data.player1_MF.Already_Deploy =  contents[1]
    data.player1_MF.total_Deploy = contents[2]
    data.player1_MF.attack_areas = Totuple(contents[3])
    data.player1_MF.attackNumber = decodeDict(contents[4]) 
    data.player2_MF.center = contents[5]
    data.player2_MF.Already_Deploy = contents[6]
    data.player2_MF.total_Deploy = contents[7]
    data.player2_MF.attack_areas = Totuple(contents[8])
    data.player2_MF.attackNumber = decodeDict(contents[9])
    #mode
    data.playerFlag_MF = contents[10]
    data.selectedFlag_AMF = contents[11]
    #map
    data.WorldMap.value= decodeDict(contents[12])
    data.WorldMap.deploy_value = decodeDict(contents[13])
    data.WorldMap.attack_value = decodeDict(contents[14])
    data.mode = contents[15]
#############################################
# playGame mode_D
#############################################
# Used to avoid player 2 see the change of player 1 while playing 
def drawPlayer_1N(data, canvas, Map, player):
    for index in range(len(Map.centers)):
        if(index in player.center):
            (cx,cy) = Map.centers[index]
            number = str(Map.deploy_value[(cx,cy)])
            canvas.create_text(cx, cy ,text = number
                    ,font = "Times 16 bold")
        else:
            (cx,cy) = Map.centers[index] 
            canvas.create_text(cx, cy ,text = Map.value[(cx,cy)]
                ,font = "Times 16 bold")

# draw Mpa index when click "Map info button"
def MapInfo(Map,canvas):
    for index in range(len(Map.centers)):
        item = Map.centers[index] 
        canvas.create_text(item[0],item[1],text = str(index),
                    font = "Times 16 bold")

# create fog for the map
def drawFog(canvas,Map,player):
    fog = Map.centers.copy()
    for item in player.center:
        points = Map.centers[item]
        Index = Map.getIndex(points[0],points[1])
        for index in Map.adjacent[Index]:
            territory = Map.centers[index]
            if(territory in fog):
                fog.remove(territory)
    for item in player.center:
        points = Map.centers[item]
        if(points in fog):
            fog.remove(points)
    for cx_cy in fog:
        for item in Map.inside_3Pix[cx_cy]:
            (cx,cy) = item
            points = [(cx-4,cy-4),(cx+4,cy-4),(cx+4,cy+4),(cx-4,cy+4)]
            canvas.create_polygon(points, fill = "black", width = 0,smooth = 1)
        for item in Map.border[cx_cy]:
            (cx,cy) = (item[0],item[1])
            color = rgbString(item[2], item[3], item[4])
            canvas.create_rectangle(cx-1,cy-1,cx+1,cy+1,fill = color, width = 0)

# chang the color of the map according to conquer
def fillSelected(canvas,index,player,color,Map):
    point = Map.centers[index]
    for item in Map.inside_3Pix[point]:
        (cx,cy) = item
        points = [(cx-4,cy-4),(cx+4,cy-4),(cx+4,cy+4),(cx-4,cy+4)]
        canvas.create_polygon(points, fill = color, width = 0,smooth = 1)
    canvas.create_text(point[0],point[1],text = Map.value[point]
        ,font = "Times 16 bold")
    for item in Map.border[point]:
        (cx,cy) = (item[0],item[1])
        color = rgbString(item[2], item[3], item[4])
        canvas.create_rectangle(cx-1,cy-1,cx+1,cy+1,fill = color, width = 0)


#Chnage the color of the selected file after clicking "Save game"
def changeColor(change,data):
    for index in range(len(data.LoadFileColor)):
        if(index == change):
            data.LoadFileColor[index] = "green"
        else:
            data.LoadFileColor[index] = "blue"

# identify what file to savee
def Choose_FILE(x,y,data):
    if(x > 300 and y > 170 and x < 500 and y < 230):
        changeColor(0,data) 
        return 0
    if(x > 30 and y > 230 and x < 500 and y < 290): 
        changeColor(1,data) 
        return 1
    if(x > 300 and y > 290 and x < 500 and y < 350): 
        changeColor(2,data)  
        return 2
    if(x > 300 and y > 350 and x < 500 and y < 410): 
        changeColor(3,data)  
        return 3
    if(x > 300 and y > 410 and x < 500 and y < 470):
        changeColor(4,data)   
        return 4
    if(x > 300 and y > 470 and x < 500 and y < 530): 
        changeColor(5,data) 
        return 5 

# draw the fiile option 
def drawFlag(canvas,data):
    margin = 60
    start = 200
    width = 800
    canvas.create_text(width//2, start, text = "FILE 0",
        fill = data.LoadFileColor[0], font = "Times 60 bold")
    canvas.create_text(width//2, start + margin, text = "FILE 1",
        fill = data.LoadFileColor[1], font = "Times 60 bold")
    canvas.create_text(width//2, start + margin*2, text = "FILE 2",
        fill = data.LoadFileColor[2], font = "Times 60 bold")
    canvas.create_text(width//2, start + margin*3, text = "FILE 3",
        fill = data.LoadFileColor[3], font = "Times 60 bold")
    canvas.create_text(width//2, start + margin*4, text = "FILE 4",
        fill = data.LoadFileColor[4], font = "Times 60 bold")
    canvas.create_text(width//2, start + margin*5, text = "FILE 5",
        fill = data.LoadFileColor[5], font = "Times 60 bold")


####################################
# playGame mode_Attack
####################################
def drawAttakSequence(data, canvas, Map, player):
    count = 0
    margin = 20
    for item in player.attack_areas:
        start = Map.getIndex(item[0][0],item[0][1])
        end = Map.getIndex(item[1][0],item[1][1])
        Number_a = player.attackNumber[(item[0],item[1])] 
        if(count in data.AS_selected):           
            canvas.create_rectangle(810,data.AS_Height[count][0], 890, 
                data.AS_Height[count][1], fill = "dark blue", width = 0)
        else:
            canvas.create_rectangle(810,data.AS_Height[count][0], 890, 
                data.AS_Height[count][1], fill = "black", width = 0)
        canvas.create_text(850, data.AS_Height[count][2], 
        text = "%d to %d %d" % (start, end, Number_a), fill ="white",
            font = "Times 19 bold")
        count += 1

def isLegal_Attack(player,x,y,Map):
    if(player.selected != None):
        index = Map.getIndex(x, y)
        territory = Map.getIndex(player.selected[0],player.selected[1])
        if(index in Map.adjacent[territory]):
            return True
        return False

def drawAttack_Line(canvas,player):
    for area in player.attack_areas:
        (sx,sy) = (area[0][0] , area[0][1])
        (ex,ey) = (area[1][0], area[1][1])
        (cx,cy) = ((sx + ex)//2, (sy + ey)//2)
        attackNumber = player.attackNumber[((sx,sy),(ex,ey))]
        canvas.create_line(sx, sy, ex, ey, fill = player.attack_color, width = 3)
        canvas.create_oval(cx-10,cy-10,cx+10,cy+10,fill = "grey",width = 0)
        canvas.create_text(cx, cy, text = str(attackNumber), font = "Times 14")

def testInOwnedArea(player, Map, x, y):
    start = 0
    for index in player.center:
        center = Map.getIndex(x,y)
        if(index == center):
            start = Map.centers[index]
            return start
    return None

def ResetToDeploy(data):
    data.player.selected = None
    data.selectedFlag_AMF == 0
    data.AS_selected.clear()
    data.player.attackNumber = {}
    data.player.attack_areas.clear()
    for index in data.player.center:
        territory = data.WorldMap.centers[index]
        data.WorldMap.attack_value[territory] =( 
            data.WorldMap.value[territory] - 1)

####################################
# playGame mode_Confirm
####################################
def drawAttakSequenceAnimation(data, canvas, Map, player):
    count = 0
    margin = 20
    for item in player.attack_areas:
        start = Map.getIndex(item[0][0],item[0][1])
        end = Map.getIndex(item[1][0],item[1][1])
        Number_a = player.attackNumber[(item[0],item[1])] 
        if(count in data.AS_selected):           
            canvas.create_rectangle(800,data.AS_Height[count][0], 900, 
                data.AS_Height[count][1], fill = "dark blue")
        else:
            canvas.create_rectangle(800,data.AS_Height[count][0], 900, 
                data.AS_Height[count][1], fill = "grey")
        canvas.create_text(850, data.AS_Height[count][2], 
        text = "%d to %d %darmies" % (start, end, Number_a), font = "Times 14")
        count += 1

#Calculate the attack sequence in correct order
def ConfirmCalc(data,player1, player2, Map):
    length_P1 = len(player1.attack_areas)
    length_P2 = len(player2.attack_areas)
    P1 = player1.attack_areas.copy()
    P2 = player2.attack_areas.copy()
    if(length_P1 > 0 and length_P2 > 0):
        AttackCalc(data, Map, player1, P1[0])
        P1.pop(0) 
        (index, turn) = (0, 1)
        while(len(P1) > 0 and len(P2) > 0):
            AttackCalc(data, Map, player2, P2[index])
            P2.pop(index)
            if(len(P1) == 0 or len(P2) == 0):break
            AttackCalc(data, Map, player2, P2[index])
            P2.pop(index)
            if(len(P1) == 0 or len(P2) == 0):break
            AttackCalc(data, Map, player1, P1[index])
            P1.pop(index)
            if(len(P1) == 0 or len(P2) == 0):break
            AttackCalc(data, Map, player1, P1[index])
            P1.pop(index)
            turn = turn + 4
        if(len(P1) == 0):
            for index in range(len(P2)):
                AttackCalc(data, Map, player2, P2[index])
        if(len(P2) == 0):
            for index in range(len(P1)):
                AttackCalc(data, Map, player1, P1[index])
    elif(length_P1 > 0 and length_P2 == 0):
        for index in range(len(P1)):
            AttackCalc(data,Map, player1, P1[index])
    elif(length_P1 == 0 and length_P2 > 0):
        for index in range(len(P2)):
            AttackCalc(data, Map, player2, P2[index])
    else:
        No_Attack(data)

# Condition when there is no attack
def No_Attack(data):
    Map = data.WorldMap
    for index in data.player1_MF.center:
        territory = Map.centers[index]
        Map.deploy_value[territory] = Map.attack_value[territory] + 1 
    for index in data.player2_MF.center:
        territory = Map.centers[index]
        Map.deploy_value[territory] = Map.attack_value[territory] + 1 

# It confirm the sequence of the cahce at the end
def Attack_End(data, Map):
    for item in data.cache:
        (end, remain) = item
        Map.value[end] = remain
        Map.deploy_value[end] = remain
        Map.attack_value[end] = remain
    for item in data.tempC1:
        if(item[0] == 1):
            data.player1_MF.center.append(item[1])
        else:
            data.player1_MF.center.remove(item[1])
    for item in data.tempC2:
        if(item[0] == 1):
            data.player2_MF.center.append(item[1])
        else:
            data.player2_MF.center.remove(item[1])

def AttackCalc_Wrapper(remain, index, player, Map, end):
    player.append_center(index)
    Map.value[end] = abs(remain)
    Map.deploy_value[end] = abs(remain)
    Map.attack_value[end] = abs(remain) - 1

# Do calculation for each turn
def AttackCalc(data, Map, player, path):
    start = path[0]
    end = path[1]
    attackNumber = player.attackNumber[(start,end)]
    supplyIndex = Map.getIndex(end[0], end[1])
    start_index = Map.getIndex(start[0], start[1])
    if(supplyIndex in player.center and start_index in player.center):
        Map.value[end] += attackNumber
        Map.deploy_value[end] += attackNumber
        Map.attack_value[end] += attackNumber 
    else:
        luck = random.randint(80,100)
        data.luck[(start,end)] = luck
        real_attack = roundHalfUp((attackNumber * luck)/100)
        remain = Map.value[end] - real_attack
        if(remain < 0):
            index = Map.getIndex(end[0],end[1])
            if(player == data.player1_MF):
                if(index not in data.player2_MF.center):
                  AttackCalc_Wrapper(remain, index, player, Map, end)
                if(index in data.player2_MF.center):
                    data.cache.append((end,abs(remain)))
                    data.tempC1.append((1,index))
                    data.tempC2.append((0,index))
            if(player == data.player2_MF):
                if(index not in data.player1_MF.center):
                    AttackCalc_Wrapper(remain, index, player, Map, end)
                if(index in data.player1_MF.center):
                    data.cache.append((end,abs(remain)))
                    data.tempC2.append((1,index))
                    data.tempC1.append((0,index))
        if(remain == 0):
            Map.value[end] = 1
            Map.deploy_value[end] = 1
            Map.attack_value[end] = 0
        if(remain > 0):
            if(checkEnd(end,data) == False):
                Map.value[end] = remain
                Map.deploy_value[end] = remain
                Map.attack_value[end] = remain - 1
    Map.deploy_value[start] = Map.attack_value[start] + 1 
    Map.value[start] = Map.attack_value[start] + 1

# To check whether end is already in attack arreas
def checkEnd(end,data):
    for item in data.player1_MF.attack_areas:
        if(end == item[0]):
            return True
    for item in data.player2_MF.attack_areas:
        if(end == item[0]):
            return True
    return False

# to add bonus to each player who captured whole bonus area
def bonusCheck(Map, player):
    player.total_Deploy = 5
    for key in Map.bonus:
        flag = True
        for index in Map.bonus[key]:
            if(index not in player.center):
                flag = False
        if(flag == True):
            if(Map.bonusIndex[key] not in player.bonus):
                player.bonus.append(Map.bonusIndex[key])
        if(flag == False):
            if(Map.bonusIndex[key] in player.bonus):
                player.bonus.remove(Map.bonusIndex[key])
    for bonus in player.bonus:
        player.total_Deploy += bonus

def adcy_Update(data):
    for index in data.play_P1data[data.PLAY_1C]:
        coordinates = data.WorldMap.centers[index]
        data.AD_cy[index] = coordinates[1]
    for index in data.play_P1data[data.PLAY_2C]:
        coordinates = data.WorldMap.centers[index]
        data.AD_cy[index] = coordinates[1]

# set up preparation stuff for play mode
def prepareForPlay(data):
    data.play_P1data.clear()
    data.play_P1data.append(data.WorldMap.deploy_value.copy())
    data.play_P1data.append(copy.deepcopy(data.player1_MF.attack_areas))
    data.play_P1data.append(data.WorldMap.value.copy())
    data.play_P1data.append(data.WorldMap.attack_value.copy())
    data.play_P1data.append(data.player1_MF.attackNumber.copy()) 
    data.play_P1data.append(copy.deepcopy(data.player2_MF.attack_areas)) 
    data.play_P1data.append(data.player2_MF.attackNumber.copy()) 
    data.play_P1data.append(data.player2_MF.center.copy())
    data.play_P1data.append(data.player1_MF.center.copy())
    data.play_P1data.append(data.WorldMap.deploy_value.copy())
    data.play_P1data.append(data.player2_MF.center.copy())
    data.play_P1data.append(data.player1_MF.center.copy())
    adcy_Update(data)
    data.AD_oldDeploy = data.WorldMap.deploy_value.copy()

def prepareForPlay_2(data):
    data.play_P2data.clear()
    data.play_P2data.append(data.WorldMap.deploy_value.copy())
    data.play_P2data.append(copy.deepcopy(data.player1_MF.attack_areas))
    data.play_P2data.append(data.WorldMap.value.copy())
    data.play_P2data.append(data.WorldMap.attack_value.copy())
    data.play_P2data.append(data.player1_MF.attackNumber.copy()) 
    data.play_P2data.append(copy.deepcopy(data.player2_MF.attack_areas)) 
    data.play_P2data.append(data.player2_MF.attackNumber.copy()) 
    data.play_P2data.append(data.player2_MF.center.copy())
    data.play_P2data.append(data.player1_MF.center.copy())
    data.play_P2data.append(data.WorldMap.deploy_value.copy())
    data.play_P2data.append(data.player2_MF.center.copy())
    data.play_P2data.append(data.player1_MF.center.copy())
    adcy_Update(data)
    data.AD_oldDeploy = data.WorldMap.deploy_value.copy()

# everything tath need to be changed by each turn
def chanegByTurn(player, data):  
    data.player = player
    player.Already_Deploy = 0
    player.attack_areas.clear()
    player.attackNumber = {}
    player.selected = None
    data.AS_selected.clear()

####################################
# Play
####################################
def Reset_Play_Data(data):
    data.play_index = -1
    data.AD_index = 0
    data.AD_set = set()
    data.AD_oldDeploy = dict()
    data.AD_preIndex = dict()
    data.play_Attackflag  = False  
    data.play_AS = dict()
    data.play_AN = dict()
    data.sx_play = 0
    data.play_AA_flag = ""
    data.play_AM_flag = False
    data.play_turn = 0
    data.replay_A = dict()
    #luck

def fillColor_play(data,canvas,Map,player1,player2,dataplay):
    center_1 = dataplay[data.PLAY_1C_D]
    center_2 = dataplay[data.PLAY_2C_D]
    for item in center_1:
        original = Map.centers[item]
        for item in Map.inside_3Pix[original]:
            (cx,cy) = item
            points = [(cx-4,cy-4),(cx+4,cy-4),(cx+4,cy+4),(cx-4,cy+4)]
            canvas.create_polygon(points,fill = player1.color, width = 0,
                smooth = 1)
        for item in Map.border[original]:
            (cx,cy) = (item[0],item[1])
            color = rgbString(item[2], item[3], item[4])
            canvas.create_rectangle(cx-1,cy-1,cx+1,cy+1,fill = color,
                width = 0)
    for item in center_2:
        original = Map.centers[item]
        for item in Map.inside_3Pix[original]:
            (cx,cy) = item
            points = [(cx-4,cy-4),(cx+4,cy-4),(cx+4,cy+4),(cx-4,cy+4)]
            canvas.create_polygon(points, fill = player2.color,width = 0,
                smooth = 1)
        for item in Map.border[original]:
            (cx,cy) = (item[0],item[1])
            color = rgbString(item[2], item[3], item[4])
            canvas.create_rectangle(cx-1,cy-1,cx+1,cy+1,fill = color,
                width = 0)

def drawFog_Play(canvas,player,Map,data):
    fog = Map.centers.copy()
    for item in player[data.PLAY_1C_D]:
        points = Map.centers[item]
        Index = Map.getIndex(points[0],points[1])
        for index in Map.adjacent[Index]:
            territory = Map.centers[index]
            if(territory in fog):
                fog.remove(territory)
    for item in player[data.PLAY_1C_D]:
        points = Map.centers[item]
        if(points in fog):
            fog.remove(points)
    for cx_cy in fog:
        for item in Map.inside_3Pix[cx_cy]:
            (cx,cy) = item
            points = [(cx-4,cy-4),(cx+4,cy-4),(cx+4,cy+4),(cx-4,cy+4)]
            canvas.create_polygon(points, fill = "black", width = 0,smooth = 1)
        for item in Map.border[cx_cy]:
            (cx,cy) = (item[0],item[1])
            color = rgbString(item[2], item[3], item[4])
            canvas.create_rectangle(cx-1,cy-1,cx+1,cy+1,fill = color, width = 0)

def drawNumbers_Play(canvas, value, Map):
    centers = Map.centers
    for index in range(len(centers)):
        (cx,cy) = centers[index] 
        canvas.create_text(cx, cy ,
            text = str(value[(cx,cy)])
            ,font = "Times 16 bold")

def adjacent_D(data, Map,index):
    for index in Map.adjacent[index]:
        if(index in data.play_P1data[data.PLAY_1C]):
            return True
    return False        

def drawPlay_Deploy(canvas, data):
    count = 0
    if(data.play_Attackflag == False):
        for index in data.play_P1data[data.PLAY_1C]:
            (cx, cy) = data.WorldMap.centers[index]
            increase = (data.play_P1data[data.PLAY_MV][(cx, cy)] - 
                data.play_P1data[data.PLAY_DV][(cx, cy)])
            if(increase != 0):
                data.AD_set.add(index)
        for index in data.play_P1data[data.PLAY_2C]:
            (cx, cy) = data.WorldMap.centers[index]
            increase = (data.play_P1data[data.PLAY_MV][(cx, cy)] - 
                data.play_P1data[data.PLAY_DV][(cx, cy)])
            if(adjacent_D(data,data.WorldMap,index) == True):
                if(increase != 0):
                    data.AD_set.add(index)
            else:
                data.play_P1data[data.PLAY_DV][(cx, cy)] = (
                            data.play_P1data[data.PLAY_MV][(cx, cy)])
    for index in data.AD_set:
        if(count == data.play_index):
            data.play_Deployflag == True
            (cx, cy) = data.WorldMap.centers[index]
            data.AD_index = index 
            data.AD_preIndex[data.play_index] = data.AD_index
            increase = (data.play_P1data[data.PLAY_MV][(cx, cy)] - 
                data.play_P1data[data.PLAY_DV][(cx, cy)])
            if(data.play_Deployflag == True): 
                    canvas.create_oval(cx- 20, data.AD_cy[data.AD_index] - 20, 
                        cx+20, data.AD_cy[data.AD_index] + 20, fill = "white")
                    canvas.create_text(cx,data.AD_cy[data.AD_index], 
                        text = "+" + str(increase), font = "Times 18")
                    if(cy - data.AD_cy[data.AD_index] >= 25):
                        data.play_P1data[data.PLAY_DV][(cx, cy)] = (
                            data.play_P1data[data.PLAY_MV][(cx, cy)])
                        data.AD_cy[data.AD_index] = cy
                        data.play_Deployflag  = False
        count += 1

def helper_PlayA(data, players, index, result):
    data.play_turn += 1
    result[data.play_turn] = players[index]
    players.pop(index)

def Adjacent_play(data, Map, players):
    start = players[0][0]
    end = players[0][1]
    index_S = Map.getIndex(start[0],start[1])
    index_E = Map.getIndex(end[0],end[1])
    for index in data.play_P1data[data.PLAY_1C]:
        adjacent = Map.adjacent[index]
        if(index_S in adjacent or index_E in adjacent):
            return True
    return False

def Play_AA_help(data, players, index, result):
    if(Adjacent_play(data, data.WorldMap, players) == True):
        helper_PlayA(data, players, index, data.play_AS)
        data.play_AN[data.play_turn] = (
            data.play_P1data[data.PLAY_2AN][data.play_AS[data.play_turn]])
    elif(Adjacent_play(data, data.WorldMap, players) == False):
        players.pop(index)

def drawPlay_Attack(canvas, data, Map):
    length_P1 = len(data.play_P1data[data.PlAY_1AA])
    length_P2 = len(data.play_P1data[data.PlAY_2AA])
    P1 = data.play_P1data[data.PlAY_1AA].copy()
    P2 = data.play_P1data[data.PlAY_2AA].copy()
    if(len(data.play_AS) < len(P1)):
        if(length_P1 > 0 and length_P2 > 0):
            data.play_AS[0] = P1[0]
            data.play_AN[0] = data.play_P1data[data.PLAY_1AN][data.play_AS[0]]
            P1.pop(0) 
            (index, data.play_turn) = (0, 0)
            while(len(P1) > 0 and len(P2) > 0):
                Play_AA_help(data, P2, index, data.play_AS)
                if(len(P1) == 0 or len(P2) == 0):break
                Play_AA_help(data, P2, index, data.play_AS)
                if(len(P1) == 0 or len(P2) == 0):break
                helper_PlayA(data, P1, index, data.play_AS)
                data.play_AN[data.play_turn] = (
                data.play_P1data[data.PLAY_1AN][data.play_AS[data.play_turn]])
                if(len(P1) == 0 or len(P2) == 0):break
                helper_PlayA(data, P1, index, data.play_AS)
                data.play_AN[data.play_turn] = (
                data.play_P1data[data.PLAY_1AN][data.play_AS[data.play_turn]])
            if(len(P1) == 0):
                start = len(data.play_AS)
                for index in range(len(P2)):
                    if(Adjacent_play(data, Map, P2) == True):
                        data.play_AS[start] = P2[index]
                        data.play_AN[start] = (
                        data.play_P1data[data.PLAY_2AN][data.play_AS[start]])
                        start += 1
                    else:
                        continue
            if(len(P2) == 0):
                start = len(data.play_AS)
                for index in range(len(P1)):
                    data.play_AS[start] = P1[index]
                    data.play_AN[start] = (
                        data.play_P1data[data.PLAY_1AN][data.play_AS[start]])
                    start += 1
        elif(length_P1 > 0 and length_P2 == 0):
            for index in range(len(P1)):
                data.play_AS[index] = P1[index]
                data.play_AN[index] = (
                    data.play_P1data[data.PLAY_1AN][data.play_AS[index]])
        elif(length_P1 == 0 and length_P2 > 0):
            for index in range(len(P2)):
                if(Adjacent_play(data, Map, P2) == True):
                    data.play_AS[index] = P2[index]
                    data.play_AN[index] = (
                    data.play_P1data[data.PLAY_2AN][data.play_AS[index]])
                else:
                    continue
        else:
            data.play_Attackflag == False
    if(data.play_Attackflag == True):
        count = len(data.AD_set)
        margin = 20
        for key in data.play_AS:
            item = data.play_AS[key]
            start = Map.getIndex(item[0][0],item[0][1])
            end = Map.getIndex(item[1][0],item[1][1])
            if(count == data.play_index):           
                canvas.create_rectangle(810,data.AS_Height[count][0], 880, 
                    data.AS_Height[count][1], fill = "dark blue")
            else:
                canvas.create_rectangle(810,data.AS_Height[count][0], 880, 
                    data.AS_Height[count][1], fill = "black")
            canvas.create_text(850, data.AS_Height[count][2], fill = "white",
            text = "%d to %d" % (start, end), font = "Times 20 bold")
            count += 1

def AttackCalc_play(data, Map, index):
    data.ConquerFlag_play = False
    start = data.play_AS[index][0]
    end = data.play_AS[index][1]
    attackNumber = data.play_AN[index]
    supplyIndex = Map.getIndex(end[0], end[1])
    index_start = Map.getIndex(start[0],start[1])
    if(supplyIndex in data.play_P1data[data.PLAY_1C] and 
        index_start in data.play_P1data[data.PLAY_1C]):
        data.play_P1data[data.PLAY_DV][end] += attackNumber
    else:
        luck = data.luck[(start, end)]
        real_attack = roundHalfUp((attackNumber * luck)/100)
        remain = data.play_P1data[data.PLAY_DV][end] - real_attack
        if(remain < 0):
            index = Map.getIndex(end[0],end[1])
            index_end = Map.getIndex(end[0],end[1]) 
            if(index_start in data.play_P1data[data.PLAY_1C]):
                data.play_P1data[data.PLAY_1C_D].append(index)
                if(index_end in data.play_P1data[data.PLAY_2C]):
                    data.ConquerFlag_play = True
                    data.play_P1data[data.PLAY_2C_D].remove(index)
            if(index_start in data.play_P1data[data.PLAY_2C]):
                data.play_P1data[data.PLAY_2C_D].append(index)
                if(index_end in data.play_P1data[data.PLAY_1C]):
                    data.ConquerFlag_play = True
                    data.play_P1data[data.PLAY_1C_D].remove(index)
            data.play_P1data[data.PLAY_DV][end] = abs(remain)
        if(remain == 0):
            data.play_P1data[data.PLAY_DV][end] = 1
        if(remain > 0):
            data.play_P1data[data.PLAY_DV][end] = remain

def last_Territory(data, ex, ey):
    index = data.WorldMap.getIndex(ex,ey)
    if(index in data.play_P1data[data.PLAY_1C_D]):
        return 1
    if(index in data.play_P1data[data.PLAY_2C_D]):
        return 2
    else:
        return 0

def drawPlay_AttackAnimation(canvas, Map, data):
    if(data.play_Attackflag == True):
        index = data.play_index - len(data.AD_set)
        (sx,sy) = data.play_AS[index][0]
        (ex,ey) = data.play_AS[index][1]
        last = last_Territory(data, ex, ey)
        k = (ey-sy)/(ex-sx)
        y = int(k * data.sx_play + (sy - sx * k))
        if(sx > ex and sy >= ey):data.play_AA_flag = "-"
        if(sx <= ex and sy > ey):data.play_AA_flag = "+"
        if(sx > ex and sy <= ey):data.play_AA_flag = "-"
        if(sx <= ex and sy < ey):data.play_AA_flag = "+"
        if(data.play_AA_flag == "+"):
            if(data.sx_play >= ex):
                if(data.play_AM_flag == True):
                    data.replay_A[((sx,sy),(ex,ey))] = (
                        data.play_P1data[data.PLAY_DV][(ex,ey)],last)
                    AttackCalc_play(data, data.WorldMap, index)
                data.play_AM_flag = False
        if(data.play_AA_flag == "-"):
            if(data.sx_play <= ex):
                if(data.play_AM_flag == True):
                    data.replay_A[((sx,sy),(ex,ey))] = (
                        data.play_P1data[data.PLAY_DV][(ex,ey)],last)
                    AttackCalc_play(data, data.WorldMap, index)
                data.play_AM_flag = False
        if(data.play_AM_flag == True):
            canvas.create_oval(data.sx_play-10,y-10,data.sx_play+10,y+10,
                fill= "white", width = 0)
            canvas.create_text(data.sx_play,y,
                text = str(data.play_AN[index]), font = "Times 14 bold")

####################################
# Play_2
####################################
def drawFog_Play_2(canvas,player,Map,data):
    fog = Map.centers.copy()
    for item in player[data.PLAY_2C_D]:
        points = Map.centers[item]
        Index = Map.getIndex(points[0],points[1])
        for index in Map.adjacent[Index]:
            territory = Map.centers[index]
            if(territory in fog):
                fog.remove(territory)
    for item in player[data.PLAY_2C_D]:
        points = Map.centers[item]
        if(points in fog):
            fog.remove(points)
    for cx_cy in fog:
        for item in Map.inside_3Pix[cx_cy]:
            (cx,cy) = item
            points = [(cx-4,cy-4),(cx+4,cy-4),(cx+4,cy+4),(cx-4,cy+4)]
            canvas.create_polygon(points, fill = "black", width = 0,smooth = 1)
        for item in Map.border[cx_cy]:
            (cx,cy) = (item[0],item[1])
            color = rgbString(item[2], item[3], item[4])
            canvas.create_rectangle(cx-1,cy-1,cx+1,cy+1,fill = color, width = 0)

def adjacent_D_2(data, Map, index):
    for index in Map.adjacent[index]:
        if(index in data.play_P2data[data.PLAY_2C]):
            return True
    return False        

def drawPlay_Deploy_2(canvas, data):
    count = 0
    if(data.play_Attackflag == False):
        for index in data.play_P2data[data.PLAY_2C]:
            (cx, cy) = data.WorldMap.centers[index]
            increase = (data.play_P2data[data.PLAY_MV][(cx, cy)] - 
                data.play_P2data[data.PLAY_DV][(cx, cy)])
            if(increase != 0):
                data.AD_set.add(index)
        for index in data.play_P2data[data.PLAY_1C]:
            (cx, cy) = data.WorldMap.centers[index]
            increase = (data.play_P2data[data.PLAY_MV][(cx, cy)] - 
                data.play_P2data[data.PLAY_DV][(cx, cy)])
            if(adjacent_D_2(data,data.WorldMap,index) == True):
                if(increase != 0):
                    data.AD_set.add(index)
            else:
                data.play_P2data[data.PLAY_DV][(cx, cy)] = (
                            data.play_P2data[data.PLAY_MV][(cx, cy)])
    for index in data.AD_set:
        if(count == data.play_index):
            data.play_Deployflag == True
            (cx, cy) = data.WorldMap.centers[index]
            data.AD_index = index 
            data.AD_preIndex[data.play_index] = data.AD_index
            increase = (data.play_P2data[data.PLAY_MV][(cx, cy)] - 
                data.play_P2data[data.PLAY_DV][(cx, cy)])
            if(data.play_Deployflag == True): 
                    canvas.create_oval(cx- 20, data.AD_cy[data.AD_index] - 20, 
                        cx+20, data.AD_cy[data.AD_index] + 20, fill = "white")
                    canvas.create_text(cx,data.AD_cy[data.AD_index], 
                        text = "+" + str(increase), font = "Times 18")
                    if(cy - data.AD_cy[data.AD_index] >= 25):
                        data.play_P2data[data.PLAY_DV][(cx, cy)] = (
                            data.play_P2data[data.PLAY_MV][(cx, cy)])
                        data.AD_cy[data.AD_index] = cy
                        data.play_Deployflag  = False
        count += 1

def Adjacent_play_2(data, Map, players):
    start = players[0][0]
    end = players[0][1]
    index_S = Map.getIndex(start[0],start[1])
    index_E = Map.getIndex(end[0],end[1])
    for index in data.play_P2data[data.PLAY_2C]:
        adjacent = Map.adjacent[index]
        if(index_S in adjacent or index_E in adjacent):
            return True
    return False

def Play_AA_help_2(data, players, index, result):
    if(Adjacent_play_2(data, data.WorldMap, players) == True):
        helper_PlayA(data, players, index, data.play_AS)
        data.play_AN[data.play_turn] = (
            data.play_P2data[data.PLAY_1AN][data.play_AS[data.play_turn]])
    if(Adjacent_play_2(data, data.WorldMap, players) == False):
        players.pop(index)

def drawPlay_Attack_2(canvas, data, Map):
    length_P1 = len(data.play_P2data[data.PlAY_1AA])
    length_P2 = len(data.play_P2data[data.PlAY_2AA])
    P1 = data.play_P2data[data.PlAY_1AA].copy()
    P2 = data.play_P2data[data.PlAY_2AA].copy()
    if(len(data.play_AS) < len(P2)):
        if(length_P1 > 0 and length_P2 > 0):
            if(Adjacent_play_2(data, data.WorldMap, P1) == True):
                data.play_AS[0] = P1[0]
                data.play_AN[0] = data.play_P2data[data.PLAY_1AN][data.play_AS[0]]
                P1.pop(0) 
                data.play_turn = 0
            else:
                P1.pop(0) 
                data.play_turn = -1  
            index = 0
            while(len(P1) > 0 and len(P2) > 0):
                helper_PlayA(data, P2, index, data.play_AS)
                data.play_AN[data.play_turn] = (
                data.play_P1data[data.PLAY_2AN][data.play_AS[data.play_turn]])
                if(len(P1) == 0 or len(P2) == 0):break
                helper_PlayA(data, P2, index, data.play_AS)
                data.play_AN[data.play_turn] = (
                data.play_P1data[data.PLAY_2AN][data.play_AS[data.play_turn]])
                if(len(P1) == 0 or len(P2) == 0):break
                Play_AA_help_2(data, P1, index, data.play_AS)
                if(len(P1) == 0 or len(P2) == 0):break
                Play_AA_help_2(data, P1, index, data.play_AS)
            if(len(P1) == 0):
                start = len(data.play_AS)
                for index in range(len(P2)):
                    data.play_AS[start] = P2[index]
                    data.play_AN[start] = (
                    data.play_P2data[data.PLAY_2AN][data.play_AS[start]])
                    start += 1
            if(len(P2) == 0):
                start = len(data.play_AS)
                for index in range(len(P1)):
                    if(Adjacent_play(data, Map, P1) == True):
                        data.play_AS[start] = P1[index]
                        data.play_AN[start] = (
                            data.play_P2data[data.PLAY_1AN][data.play_AS[start]])
                        start += 1
                    else:
                        continue
        elif(length_P1 > 0 and length_P2 == 0):
            for index in range(len(P1)):
                if(Adjacent_play(data, Map, P1) == True):
                    data.play_AS[index] = P1[index]
                    data.play_AN[index] = (
                    data.play_P2data[data.PLAY_1AN][data.play_AS[index]])
                else:
                    continue
        elif(length_P1 == 0 and length_P2 > 0):
            for index in range(len(P2)):
                    data.play_AS[index] = P2[index]
                    data.play_AN[index] = (
                    data.play_P2data[data.PLAY_2AN][data.play_AS[index]])
        else:
            data.play_Attackflag == False
    if(data.play_Attackflag == True):
        count = len(data.AD_set)
        margin = 20
        for key in data.play_AS:
            item = data.play_AS[key]
            start = Map.getIndex(item[0][0],item[0][1])
            end = Map.getIndex(item[1][0],item[1][1])
            if(count == data.play_index):           
                canvas.create_rectangle(810,data.AS_Height[count][0], 880, 
                    data.AS_Height[count][1], fill = "dark blue")
            else:
                canvas.create_rectangle(810,data.AS_Height[count][0], 880, 
                    data.AS_Height[count][1], fill = "black")
            canvas.create_text(850, data.AS_Height[count][2], fill = "white",
            text = "%d to %d" % (start, end), font = "Times 20 bold")
            count += 1

def AttackCalc_play_2(data, Map, index):
    data.ConquerFlag_play = False
    start = data.play_AS[index][0]
    end = data.play_AS[index][1]
    attackNumber = data.play_AN[index]
    supplyIndex = Map.getIndex(end[0], end[1])
    index_start = Map.getIndex(start[0],start[1])
    if(supplyIndex in data.play_P2data[data.PLAY_2C] and 
        index_start in data.play_P2data[data.PLAY_2C]):
        data.play_P2data[data.PLAY_DV][end] += attackNumber
    else:
        luck = data.luck[(start, end)]
        real_attack = roundHalfUp((attackNumber * luck)/100)
        remain = data.play_P2data[data.PLAY_DV][end] - real_attack
        if(remain < 0):
            index = Map.getIndex(end[0],end[1])
            index_end = Map.getIndex(end[0],end[1]) 
            if(index_start in data.play_P2data[data.PLAY_1C]):
                data.play_P2data[data.PLAY_1C_D].append(index)
                if(index_end in data.play_P2data[data.PLAY_2C]):
                    data.ConquerFlag_play = True
                    data.play_P2data[data.PLAY_2C_D].remove(index)
            if(index_start in data.play_P2data[data.PLAY_2C]):
                data.play_P2data[data.PLAY_2C_D].append(index)
                if(index_end in data.play_P2data[data.PLAY_1C]):
                    data.ConquerFlag_play = True
                    data.play_P2data[data.PLAY_1C_D].remove(index)
            data.play_P2data[data.PLAY_DV][end] = abs(remain)
        if(remain == 0):
            data.play_P2data[data.PLAY_DV][end] = 1
        if(remain > 0):
            data.play_P2data[data.PLAY_DV][end] = remain

def last_Territory_2(data, ex, ey):
    index = data.WorldMap.getIndex(ex,ey)
    if(index in data.play_P2data[data.PLAY_1C_D]):
        return 1
    if(index in data.play_P2data[data.PLAY_2C_D]):
        return 2
    else:
        return 0

def drawPlay_AttackAnimation_2(canvas, Map, data):
    if(data.play_Attackflag == True):
        index = data.play_index - len(data.AD_set)
        (sx,sy) = data.play_AS[index][0]
        (ex,ey) = data.play_AS[index][1]
        last = last_Territory_2(data, ex, ey)
        k = (ey-sy)/(ex-sx)
        y = int(k * data.sx_play + (sy - sx * k))
        if(sx > ex and sy >= ey):data.play_AA_flag = "-"
        if(sx <= ex and sy > ey):data.play_AA_flag = "+"
        if(sx > ex and sy <= ey):data.play_AA_flag = "-"
        if(sx <= ex and sy < ey):data.play_AA_flag = "+"
        if(data.play_AA_flag == "+"):
            if(data.sx_play >= ex):
                if(data.play_AM_flag == True):
                    data.replay_A[((sx,sy),(ex,ey))] = (
                        data.play_P2data[data.PLAY_DV][(ex,ey)],last)
                    AttackCalc_play_2(data, data.WorldMap, index)
                data.play_AM_flag = False
        if(data.play_AA_flag == "-"):
            if(data.sx_play <= ex):
                if(data.play_AM_flag == True):
                    data.replay_A[((sx,sy),(ex,ey))] = (
                        data.play_P2data[data.PLAY_DV][(ex,ey)],last)
                    AttackCalc_play_2(data, data.WorldMap, index)
                data.play_AM_flag = False
        if(data.play_AM_flag == True):
            canvas.create_oval(data.sx_play-10,y-10,data.sx_play+10,y+10,
                fill= "white", width = 0)
            canvas.create_text(data.sx_play,y,
                text = str(data.play_AN[index]), font = "Times 14 bold")
               

