####################################
# 15112 Term project Ruohai Ge
####################################

from tkinter import *
import random, string, copy, math, time
from helper import *
from PIL import Image, ImageFilter
import sys
import threading
import decimal
import json

####################################
# Class
####################################

class player(object):
    def __init__(self,center,color,attack_color,selected_color):
        self.center = center
        self.color = color
        self.Already_Deploy = 0
        self.total_Deploy = 5
        self.attack_areas = []
        self.selected = None
        self.attackNumber = {}
        self.attack_color = attack_color
        self.selected_color = selected_color
        self.bonus = []
        
    def append_center(self,index):
        self.center.append(index)

    def append_attack(self,index):
        self.attack_areas.append(index)

    def __eq__(self, other):
        if(self.center == other.center and   self.color == other.color):
            return True
        else:
            return False

class gameMap(object):

    def __init__(self, images, txt_Centers, txt_Adjacent,txt_Bonus,
                    txt_Bonus_Index):
        self.pix = images.load()
        self.rgb = images.convert('RGB')
        self.centers = stringToTuple(readFile(txt_Centers).split('*'))
        self.value = self.mapValue()
        self.adjacent_Doc = stringToTuple(readFile(txt_Adjacent).split('*'))
        self.adjacent = self.MapAdjacent()
        self.border = self.getBorder()[1]
        self.WALL = self.getBorder()[0]
        self.inside = self.getBorder()[2]
        self.inside_3Pix = self.getInside()
        self.deploy_value = self.mapValue()
        self.attack_value = self.mapValue()
        self.bonus_doc = stringToTuple(readFile(txt_Bonus).split('*'))
        self.bonus = self.makeBonusDic()
        self.bonusIndex_doc = stringToTuple(readFile(txt_Bonus_Index).split('*'))
        self.bonusIndex = self.makeBonusIndexDic()

    def makeBonusDic(self):
        result = {}
        for index in range(0,6):
            result[index] = self.bonus_doc[index]
        return result

    def makeBonusIndexDic(self):
        result = {}
        for item in self.bonusIndex_doc:
            result[item[0]] = item[1]
        return result


    def getIndex(self, x, y):
        for key in self.inside:
            if((x,y) in self.inside [key]):
                index = self.centers.index(key)
                return index

    def MapAdjacent(self):
        result = {}
        for index in range(len(self.adjacent_Doc)):
            result[index] = self.adjacent_Doc[index]
        return result

    def mapValue(self):
        result = {}
        for item in self.centers:
            result[item] = 2
        return result

    def generatorStarter(self, data, player1, player2):
        temp_map = self.centers.copy()
        while(len(player1.center) < 2):
            index = random.randint(0,len(temp_map)-1)
            item = temp_map[index]
            result = self.centers.index(item)
            player1.append_center(result)
            (self.value[item],self.deploy_value[item]) = (5, 5)
            self.attack_value[item] = 4
            data.AD_cy[result] = item[1]
            temp_map.pop(index)
        while(len(player2.center) < 2):
            length = len(temp_map)
            index = random.randint(0,len(temp_map)-1)
            item = temp_map[index]
            result = self.centers.index(item)
            player2.append_center(result)
            (self.value[item],self.deploy_value[item]) = (5, 5)
            self.attack_value[item] = 4
            data.AD_cy[result] = item[1]
            temp_map.pop(index)

    def drawNumbers(self,canvas):
        for index in range(len(self.centers)):
            (cx,cy) = self.centers[index] 
            canvas.create_text(cx, cy ,text = self.value[(cx,cy)]
                ,font = "Times 16 bold")

    def getInside(self):
        inside = {}
        WALL = self.WALL
        for index in range(len(self.centers)):
            original = self.centers[index]
            inside[original] = {original}
            paintBucket_Inside(original,self.pix,self.rgb,inside,WALL)
        return inside

    def getBorder(self):
        border = {}
        WALL = {}
        inside = {}
        for index in range(len(self.centers)):
            original = self.centers[index]
            inside[original] = {original}
            paintBucket_Border(original,self.pix,self.rgb, border,WALL,inside)
        return (WALL, border,inside)
        
    def fillColor(self,data,canvas,player1,player2):
        for item in player1.center:
            original = self.centers[item]
            for item in self.inside_3Pix[original]:
                (cx,cy) = item
                points = [(cx-4,cy-4),(cx+4,cy-4),(cx+4,cy+4),(cx-4,cy+4)]
                canvas.create_polygon(points,fill = player1.color, width = 0)
            for item in self.border[original]:
                (cx,cy) = (item[0],item[1])
                color = rgbString(item[2], item[3], item[4])
                canvas.create_rectangle(cx-1,cy-1,cx+1,cy+1,fill = color,
                    width = 0)
        for item in player2.center:
            original = self.centers[item]
            for item in self.inside_3Pix[original]:
                (cx,cy) = item
                points = [(cx-4,cy-4),(cx+4,cy-4),(cx+4,cy+4),(cx-4,cy+4)]
                canvas.create_polygon(points, fill = player2.color,width = 0)
            for item in self.border[original]:
                (cx,cy) = (item[0],item[1])
                color = rgbString(item[2], item[3], item[4])
                canvas.create_rectangle(cx-1,cy-1,cx+1,cy+1,fill = color,
                    width = 0)

####################################
# init
####################################
# Tkinter BareBones cited from 15112 Website
def splash(data):
    data.SScolor = ["light Green", "light Green","light Green", "light Green"]
    image_background = PhotoImage(file ="BackGround.gif")
    data.image_background = image_background
    data.startScreenXY = stringToTuple(readFile("SScreenMap.txt").split('*'))
    data.length_SS = len(data.startScreenXY)
    (data.cellSize, data.r, data.ssFlag, data.ssCount) = (0, 40, False, 0)
    (data.index_SS,data.count_SS)  = ([0,1,2,3], 4)

def Help(data):
    data.Hcolor = ["black", "black", "black"]
    Help_image = PhotoImage(file ="Help and Credit Background.gif")
    data.Help_image = Help_image
    data.HelpPage = 0

def credit(data):
    data.Ccolor = "black"
    Credit_image = PhotoImage(file ="Help and Credit Background.gif")
    data.Credit_image = Credit_image
    image_WL = PhotoImage(file ="Warlight.gif")
    data.image_WL = image_WL
    image_RK = PhotoImage(file ="Risk.gif")
    data.image_RK = image_RK

def play_Number_Variable(data):
    data.PLAY_DV = 0
    data.PlAY_1AA = 1
    data.PLAY_MV = 2
    data.PLAY_AV = 3
    data.PLAY_1AN = 4
    data.PlAY_2AA = 5
    data.PLAY_2AN = 6
    data.PLAY_2C = 7
    data.PLAY_1C = 8
    data.PLAY_DV_R = 9
    data.PLAY_2C_D = 10
    data.PLAY_1C_D = 11

def play(data):
    data.play_Deployflag = True
    (data.play_P1data,data.play_P2data) = ([],[])
    play_Number_Variable(data)
    data.play_index = -1
    data.AD_index = 0
    data.AD_cy = {}
    data.AD_set = set()
    data.AD_oldDeploy = dict()
    data.AD_preIndex = dict()
    data.play_Attackflag  = False  
    data.play_AS = dict()
    data.play_AN = dict()
    (data.play_turn,data.sx_play) = (0,0)
    data.play_AA_flag = ""
    (data.play_AM_flag,data.ConquerFlag_play) = (False,False)
    data.replay_A = dict()
    image_ForBack = PhotoImage(file ="ForBack.gif")
    data.image_ForBack = image_ForBack

def gameOver(data):
    data.fontSize_GO  = 60
    data.GOcolor = "green"
    GameOver_image = PhotoImage(file ="Game_Over Background.gif")
    data.GameOver_image =  GameOver_image
    data.Game_Over_Row = data.width//2

def LoadGame(data):
    data.LGcolor = ["white", "white", "white", "white", "white", "white"]
    data.PGSB = ["green", "green"]
    LoadGame_image = PhotoImage(file ="Load_Game Background.gif")
    data.LoadGame_image = LoadGame_image
    data.LoadGame_flag = None
    data.Fileflag = False
    data.LoadFileSet = set()
    data.LoadFile = None
    data.LoadFileColor = ["blue", "blue", "blue", "blue", "blue", "blue"]

def Deploy_MF(data):
    image_Button = PhotoImage(file ="Button.gif")
    data.image_Button = image_Button
    image_Long_Button = PhotoImage(file ="Long_Button.gif")
    data.image_Long_Button = image_Long_Button 
    image_Bar = PhotoImage(file ="Option Bar.gif")
    data.image_Bar = image_Bar
    image_AS = PhotoImage(file ="Attack_Sequence.gif")
    data.image_AS = image_AS
    data.player1_MF = player([],"light green","green","dark green")
    data.player2_MF = player([],"light blue","dark blue","blue")
    data.player = data.player1_MF
    data.playerFlag_MF = 1 

def init_WorldMap(data):
    image_MAP_World_Game = PhotoImage(file ="WorldMap.gif")
    data.image_WorldMap_Game = image_MAP_World_Game
    images_WorldMap = Image.open("WorldMap.gif")
    data.WorldMap = gameMap(images_WorldMap, "WorldMap_Centers.txt",
        "WolrdMap_Adjacent.txt","WorldMap_Deploy_Bonus.txt",
        "WorldMap_Bonus_Index.txt")
    data.WorldMap.generatorStarter(data,data.player1_MF,data.player2_MF)
    data.MapInfoFlag = False

def Attack_MF(data):
    data.selectedFlag_AMF = 0
    data.AS_Height = AS_HeightAndColor()
    data.AS_selected = []
    data.luck = dict()
    data.tempC1 = []
    data.tempC2 = []
    data.cache = []

def Confirm_MF(data):
    data.C_MF_Color = "white"
    image_Next_Turn = PhotoImage(file ="Next_Turn.gif")
    data.image_Next_Turn = image_Next_Turn
    data.Firstflag = True

def init(data):
    # Genral
    data.mode = "splashScreen"
    # SplashScreen
    splash(data)
    Help(data)
    credit(data)
    play(data)
    gameOver(data)
    LoadGame(data)
    #Deploy Multiplayer Offline
    Deploy_MF(data)
    init_WorldMap(data)
    #Attack Multiplayer Offline
    Attack_MF(data) 
    #Confirm Multiplayer Offline 
    Confirm_MF(data)
  
####################################
# mode dispatcher
####################################

def leftMousePressed(event, data):
    if (data.mode == "splashScreen"): splashScreenleftMousePressed(event, data)
    elif (data.mode == "playGame_Deploy_MF"): D_MFleftMousePressed(event, data)
    elif (data.mode == "help"): helpleftMousePressed(event, data)
    elif (data.mode == "playGame_Attack_MF"): A_MFleftMousePressed(event, data)
    elif (data.mode == "playGame_Confirm_MF"): C_MFleftMousePressed(event, data)
    elif (data.mode == "loadGame"): loadGameleftMousePressed(event, data)
    elif (data.mode == "credit"): creditleftMousePressed(event, data)
    elif (data.mode == "gameOver"): gameOverleftMousePressed(event, data)
    elif (data.mode == "play"): playleftMousePressed(event, data)
    elif (data.mode == "play_2"):play_2leftMousePressed(event, data)

def keyPressed(event, data):
    if (data.mode == "splashScreen"): splashScreenKeyPressed(event, data)
    elif (data.mode == "playGame_Deploy_MF"): D_MFKeyPressed(event, data)
    elif (data.mode == "help"): helpKeyPressed(event, data)
    elif (data.mode == "playGame_Attack_MF"): A_MFKeyPressed(event, data)
    elif (data.mode == "playGame_Confirm_MF"): C_MFKeyPressed(event, data)
    elif (data.mode == "loadGame"): loadGameKeyPressed(event, data)
    elif (data.mode == "credit"): creditKeyPressed(event, data)
    elif (data.mode == "gameOver"): gameOverKeyPressed(event, data)
    elif (data.mode == "play"): playKeyPressed(event, data)
    elif (data.mode == "play_2"):play_2KeyPressed(event, data)

def rightMousePressed(event, data):
    if (data.mode == "playGame_Attack_MF"): A_MFrightMousePressed(event, data)
    elif (data.mode == "playGame_Confirm_MF"):C_MFrightMousePressed(event, data)

def timerFired(data):
    if (data.mode == "splashScreen"): splashScreenTimerFired(data)
    elif (data.mode == "playGame_Deploy_MF"): D_MFTimerFired(data)
    elif (data.mode == "help"): helpTimerFired(data)
    elif (data.mode == "playGame_Attack_MF"): A_MFTimerFired(data)
    elif (data.mode == "playGame_Confirm_MF"): C_MFTimerFired(data)
    elif (data.mode == "credit"): creditTimerFired(data)
    elif (data.mode == "loadGame"): loadGameTimerFired(data)
    elif (data.mode == "gameOver"): gameOverTimerFired(data)
    elif (data.mode == "play"): playTimerFired(data)
    elif (data.mode == "play_2"):play_2TimerFired(data)

def redrawAll(canvas, data):
    if (data.mode == "splashScreen"): splashScreenRedrawAll(canvas, data)
    elif (data.mode == "playGame_Deploy_MF"): D_MFRedrawAll(canvas, data)
    elif (data.mode == "help"): helpRedrawAll(canvas, data)
    elif (data.mode == "playGame_Attack_MF"): A_MFRedrawAll(canvas, data)
    elif (data.mode == "playGame_Confirm_MF"): C_MFRedrawAll(canvas, data)
    elif (data.mode == "loadGame"): loadGameRedrawAll(canvas, data)
    elif (data.mode == "credit"): creditRedrawAll(canvas, data)
    elif (data.mode == "gameOver"): gameOverRedrawAll(canvas, data)
    elif (data.mode == "play"): playRedrawAll(canvas, data)
    elif (data.mode == "play_2"): playRedrawAll_2(canvas, data)

def mouseMotion(event,data):
    if (data.mode == "splashScreen"): splashScreenMouseMotion(event,data)
    elif (data.mode == "loadGame"): loadGameMouseMotion(event, data)
    elif (data.mode == "help"): helpMouseMotion(event, data)
    elif (data.mode == "credit"): creditMouseMotion(event, data)
    elif (data.mode == "gameOver"):gameOverMouseMotion(event, data)

####################################
# splashScreen mode
####################################
def splashScreenMouseMotion(event,data):
    (margin, w, h, cx, cy) = (60, [110,120,130,85], 20,150, data.height/2 + 50)   
    if(cx - w[0] < event.x < cx + w[0] and 
        cy- h < event.y < cy + h):
        # inside the letter, draw two arrows and highlight 
        (data.SScolor[0],data.SScolor[1]) = ("blue", "light green")
        (data.SScolor[2],data.SScolor[3]) = ("light green", "light green")
    elif(cx - w[1] < event.x < cx + w[1] and 
        cy + margin - h < event.y < cy + margin + h):
        (data.SScolor[0],data.SScolor[1]) = ("light green", "blue")
        (data.SScolor[2],data.SScolor[3]) = ("light green", "light green")
    elif(cx - w[2] < event.x < cx + w[2] and 
        cy + margin*2- h < event.y < cy + margin*2 + h):
        (data.SScolor[0],data.SScolor[1]) = ("light green", "light green")
        (data.SScolor[2],data.SScolor[3]) = ("blue", "light green")
    elif(cx - w[3] < event.x < cx + w[3] and 
         cy + margin*3- h < event.y < cy + margin*3 + h):
        (data.SScolor[0],data.SScolor[1]) = ("light green", "light green")
        (data.SScolor[2],data.SScolor[3]) = ("light green", "blue")
    else:
        (data.SScolor[0],data.SScolor[1]) = ("light green", "light green")
        (data.SScolor[2],data.SScolor[3]) = ("light green", "light green")

def splashScreenleftMousePressed(event, data):
    (margin, w, h, cx, cy) = (60, [110,120,130,85], 20,150, data.height/2 + 50)
    if(cx - w[0] < event.x < cx + w[0] and cy - h < event.y < cy + h):
        (data.mode, data.timerDelay) = ("playGame_Deploy_MF", 1)
        (data.index_SS,data.count_SS)  = ([0,1,2,3], 4)
    elif(cx - w[1] < event.x < cx + w[1] and 
        cy + margin - h < event.y < cy + margin + h):
        (data.index_SS,data.count_SS)  = ([0,1,2,3], 4)
        (data.mode, data.timerDelay) = ("loadGame", 100) 
        LoadFileSet_Helper(data)
    elif(cx - w[2] < event.x < cx + w[2] and 
        cy + margin*2- h < event.y < cy + margin*2 + h):
        (data.index_SS,data.count_SS)  = ([0,1,2,3], 4) 
        (data.mode, data.timerDelay) = ("help", 100) 
    elif(cx - w[3] < event.x < cx + w[3] and 
         cy + margin*3- h < event.y < cy + margin*3 + h): 
        (data.index_SS,data.count_SS)  = ([0,1,2,3], 4)   
        (data.mode, data.timerDelay) = ("credit", 100) 

def splashScreenKeyPressed(event, data):
    pass

def splashScreenTimerFired(data):
    if(len(data.index_SS) >= data.length_SS):
       data.index_SS = [0, 1, 2, 3]
       data.count_SS = 4
    data.index_SS.append(data.count_SS)
    data.count_SS += 1

def splashScreenRedrawAll(canvas, data):
    canvas.create_image(data.width/2, data.height/2, 
        image = data.image_background)
    (cx, cy)  = (150, data.height/2 + 50)
    (margin, title, distance) = (60, 120, 120)
    canvas.create_text(cx, cy, 
        text="NEW GAME", fill = data.SScolor[0], font="Times 36 bold")
    canvas.create_text(cx, cy + margin,
        text="LOAD GAME", fill = data.SScolor[1], font="Times 36 bold")
    canvas.create_text(cx, cy + 2 * margin,
        text="INSTRUCTION", fill = data.SScolor[2], font="Times 36 bold")
    canvas.create_text(cx, cy + 3 * margin,
        text="CREDITS", fill = data.SScolor[3], font="Times 36 bold")
    drawAnimationSS_initial(canvas, data)
        
####################################
# help mode
####################################
def helpMouseMotion(event, data):
    if(event.x > 510 and event.y > 540 and event.x < 590 and event.y < 580):
        (data.Hcolor[0], data.Hcolor[1]) = ("blue", "black")
        data.Hcolor[2] = "black"
    elif(event.x > 980 and event.y > 540 and event.x < 1100 and event.y < 580):
        (data.Hcolor[0], data.Hcolor[1]) = ("black", "blue")
        data.Hcolor[2] = "black"
    elif(event.x > 10 and event.y > 540 and event.x < 150 and event.y < 580):
        (data.Hcolor[0], data.Hcolor[1]) = ("black", "black")
        data.Hcolor[2] = "blue"
    else:
        (data.Hcolor[0], data.Hcolor[1]) = ("black", "black")
        data.Hcolor[2] = "black"

def helpleftMousePressed(event, data):
    if(event.x > 510 and event.y > 540 and event.x < 590 and event.y < 580):
        data.mode = "splashScreen"
    if(event.x > 950 and event.y > 320 and event.x < 1050 and event.y < 360
        and data.HelpPage < 4):
        data.HelpPage += 1
    if(event.x > 45 and event.y > 320 and event.x < 135 and event.y < 360
        and data.HelpPage > 0):
        data.HelpPage -= 1

def helpKeyPressed(event, data):
    pass

def helpTimerFired(data):
    pass

def helpRedrawAll(canvas, data):
    canvas.create_image(data.width//2, data.height//2, image = data.Help_image)
    canvas.create_text(data.width/2, 120, text = "INSTRUCTION", 
        font = "Times 50 bold")
    canvas.create_text(540,data.height - 120,text = "BACK",
        fill = data.Hcolor[0], font = "Times 30")
    canvas.create_text(1000, data.height//2, text = ">>", 
        fill = data.Hcolor[1], font = "Times 50")
    canvas.create_text(95, data.height//2, text = "<<",
        fill = data.Hcolor[2], font = "Times 50")
    if(data.HelpPage == 0): drawHelp0(canvas,data)
    if(data.HelpPage == 1): drawHelp1(canvas,data)
    if(data.HelpPage == 2): drawHelp2(canvas,data)
    if(data.HelpPage == 3): drawHelp3(canvas,data)
    if(data.HelpPage == 4): drawHelp4(canvas,data)


####################################
# Credit
####################################
def creditMouseMotion(event, data):
    if(event.x > 510 and event.y > 540 and event.x < 590 and event.y < 580):
        data.Ccolor = "blue"
    else:
        data.Ccolor = "black"

def creditleftMousePressed(event, data):
    if(event.x > 510 and event.y > 540 and event.x < 590 and event.y < 580):
        data.mode = "splashScreen"

def creditKeyPressed(event, data):
    pass

def creditTimerFired(data):
    pass

def creditRedrawAll(canvas, data):
    canvas.create_image(data.width//2, data.height//2,
                image = data.Credit_image)
    canvas.create_text(data.width/2, 120, text = "CREDITS", 
        font = "Times 50 bold")
    canvas.create_text(540,data.height - 120,text = "BACK",
        fill = data.Ccolor, font = "Times 30")
    canvas.create_text(540,170,text = "Thanks To Professor Kosbie",
        fill = "Black", font = "Times 30")
    canvas.create_text(540,220,text = "Thanks To my TP Mentor Arman Hezarkhani"  
     , fill = "Black", font = "Times 30") 
    canvas.create_text(540,270,text = "TA Sarah Boyle, Qixiu Han", 
        fill = "Black", font = "Times 30") 
    canvas.create_text(540,320,text = "and all the people who help and teach me" 
        , fill = "Black", font = "Times 30") 
    canvas.create_text(540,370,text = "how to code and how to improve my " +
        "term project", fill = "Black", font = "Times 30") 
    canvas.create_text(540,420,text = "Game design orginated from",
        fill = "Black", font = "Times 30") 
    canvas.create_text(540,470,text = "www.warlight.net and boardgame Risk", 
        fill = "Black", font = "Times 30") 
    canvas.create_image(280,540, image = data.image_WL)
    canvas.create_image(820,540, image = data.image_RK)

####################################
# LOAD GAME
####################################
def loadGameMouseMotion(event,data):
    if(event.x > 980 and event.y > 620 and event.x < 1100 and event.y < 660):
        (data.PGSB[0], data.PGSB[1]) = ("blue", "green")
    elif(event.x > 10 and event.y > 620 and event.x < 110 and event.y < 660):
        (data.PGSB[0], data.PGSB[1]) = ("green", "blue")
    else:
        (data.PGSB[0], data.PGSB[1]) = ("green", "green")



def loadGameleftMousePressed(event, data):
    if(event.x > 10 and event.y > 620 and event.x < 110 and event.y < 660):
        data.mode = "splashScreen"
    elif(event.x > 150 and event.y > 210 and event.x < 450 and event.y < 270):
        data.LGcolor = ["white", "white", "white", "white", "white", "white"]
        data.LGcolor[0] = "blue"
        if(0 in data.LoadFileSet): data.LoadFile = 0
    elif(event.x > 150 and event.y > 360 and event.x < 450 and event.y < 420):
        data.LGcolor = ["white", "white", "white", "white", "white", "white"]
        data.LGcolor[1] = "blue"
        if(1 in data.LoadFileSet):data.LoadFile = 1
    elif(event.x > 150 and event.y > 490 and event.x < 450 and event.y < 550):
        data.LGcolor = ["white", "white", "white", "white", "white", "white"]
        data.LGcolor[2] = "blue"
        if(2 in data.LoadFileSet):data.LoadFile = 2
    elif(event.x > 650 and event.y > 210 and event.x < 950 and event.y < 270):
        data.LGcolor = ["white", "white", "white", "white", "white", "white"]
        data.LGcolor[3] = "blue"
        if(3 in data.LoadFileSet):data.LoadFile = 3
    elif(event.x > 650 and event.y > 360 and event.x < 950 and event.y < 420):
        data.LGcolor = ["white", "white", "white", "white", "white", "white"]
        data.LGcolor[4] = "blue"
        if(4 in data.LoadFileSet):data.LoadFile = 4
    elif(event.x > 650 and event.y > 490 and event.x < 950 and event.y < 550):
        data.LGcolor = ["white", "white", "white", "white", "white", "white"]
        data.LGcolor[5] = "blue"
        if(5 in data.LoadFileSet):data.LoadFile = 5
    elif(event.x > 990 and event.y > 620 and event.x < 1090 and event.y < 660):
        if(data.LoadFile == 0): openLoad(data,"file0.txt")
        if(data.LoadFile == 1): openLoad(data,"file1.txt")
        if(data.LoadFile == 2): openLoad(data,"file2.txt")
        if(data.LoadFile == 3): openLoad(data,"file3.txt")
        if(data.LoadFile == 4): openLoad(data,"file4.txt")
        if(data.LoadFile == 5): openLoad(data,"file5.txt")

def loadGameKeyPressed(event, data):
    pass

def loadGameRedrawAll(canvas, data):
    canvas.create_image(data.width//2, data.height//2,
                image = data.LoadGame_image)
    canvas.create_text(data.width/2, 80, text = "LOAD GAME", 
        font = "Times 50 bold")
    canvas.create_rectangle(150, 210, 450, 270, fill = data.LGcolor[0],width=2)
    canvas.create_rectangle(150, 360, 450, 420, fill = data.LGcolor[1],width=2)
    canvas.create_rectangle(150, 490, 450, 550, fill = data.LGcolor[2],width=2)
    canvas.create_rectangle(650, 210, 950, 270, fill = data.LGcolor[3],width=2)
    canvas.create_rectangle(650, 360, 950, 420, fill = data.LGcolor[4],width=2)
    canvas.create_rectangle(650, 490, 950, 550, fill = data.LGcolor[5],width=2)
    canvas.create_text(1040, data.height - 40, text = "START", 
        fill = data.PGSB[0], font = "Times 30")
    canvas.create_text(60, data.height - 40,text = "BACK",fill = data.PGSB[1], 
        font = "Times 30")
    drawloadFile(canvas, data)

def loadGameTimerFired(data):
    pass

#############################################
# playGame mode_Deploy_Multiplayer Offline
#############################################
def D_MFleftMousePressed(event, data):
    if(event.x > 930 and event.y > 430 and event.x < 1070 and event.y < 470):
        data.player.selected = None
        data.mode = "playGame_Attack_MF"
    elif(event.x > 915 and event.y > 310 and event.x < 995 and event.y < 330):
        startOver(data)
    elif(event.x > 950 and event.y > 490 and event.x < 1050 and event.y < 530):
        data.player.selected = None
        data.mode = "splashScreen"
        init(data)
    elif(event.x > 1002 and event.y > 370 and event.x < 1082 and event.y < 410):
        data.MapInfoFlag = True
    elif(event.x > 1002 and event.y > 310 and event.x < 1082 and event.y < 350):
        data.mode = "gameOver"
    elif(event.x > 915 and event.y > 370 and event.x < 995 and event.y < 410):
        data.Fileflag = True 
    elif(data.Fileflag == True):
        data.LoadGame_flag = Choose_FILE(event.x,event.y,data)
    else:
        data.player.selected = (event.x, event.y)

def D_MFKeyPressed(event, data):
    if(event.keysym == "Up"):
        # WorldMap
        if(data.player.Already_Deploy < data.player.total_Deploy):
            for index in data.player.center:
                point = data.WorldMap.centers[index]
                if(data.player.selected == None):
                    continue
                elif((data.player.selected[0],data.player.selected[1]) 
                            in data.WorldMap.inside[point]):
                    data.WorldMap.value[point] += 1
                    data.WorldMap.attack_value[point] += 1
                    data.player.Already_Deploy += 1
    elif(event.keysym == "Down"):
        # WorldMap
        if(data.player.Already_Deploy >= 1):
            for index in data.player.center:
                point = data.WorldMap.centers[index]
                if(data.player.selected == None):
                    continue
                elif((data.player.selected[0],data.player.selected[1]) 
                            in data.WorldMap.inside[point] and 
                    data.WorldMap.deploy_value[point] < 
                            data.WorldMap.value[point]):
                    data.WorldMap.value[point] -= 1
                    data.WorldMap.attack_value[point] -= 1
                    data.player.Already_Deploy -= 1
    elif(event.keysym == "q"):
        data.MapInfoFlag = False
        data.Fileflag = False
        SaveGame(data)

def D_MFTimerFired(data):
    pass

def drawBackground_Deploy_MF(canvas, data):
    canvas.create_rectangle(920, 100, 1060, 125 , fill = "dark blue", width = 0)
    canvas.create_text(1000, 235, 
    text = "    Click on a territory\n you own to deploy there.", 
        fill = "white", font = "Times 16") 
    canvas.create_text(1000, 280, text = "%d / %d armies" % 
         (data.player.Already_Deploy, data.player.total_Deploy),
            fill = "white", font = "Times 25") 
    canvas.create_image(1000,450,image = data.image_Long_Button)
    canvas.create_text(1000, 450, text = "Attack/Transfer", fill = "white", 
         font = "Times 20") 

def drawInstruction_D(canvas,data):
    canvas.create_text(1000, data.height - 120, text = "Use Up arrow key" 
       ,fill ="green", font = "Times 18")
    canvas.create_text(1000, data.height - 90, text = "Down arrow key to"
      , fill ="green", font = "Times 18")
    canvas.create_text(1000, data.height - 70, 
        text = "change armies", fill ="green", font = "Times 18")
    canvas.create_text(1000, data.height - 50, text = "Click Attack/Trandfer"
        , fill = "green", font = "Times 18" )
    canvas.create_text(1000, data.height - 30, 
        text = "to continue"
        , fill = "green", font = "Times 18" )

def D_MFRedrawAll(canvas, data):
    canvas.create_image(400, data.height//2, image = 
        data.image_WorldMap_Game)
    canvas.create_rectangle(800, 0, 900, data.height, fill = "grey", 
        width = 1)
    canvas.create_rectangle(900, 0, data.width, data.height, fill = "grey", 
        width = 1)
    canvas.create_image(1000, data.height//2, image = data.image_Bar)
    canvas.create_image(850, data.height//2, image = data.image_AS)
    drawBackground_Deploy_MF(canvas, data)
    playGameBackGround(canvas,data)
    drawInstruction_D(canvas,data)
    # WorldMap
    data.WorldMap.fillColor(data,canvas,data.player1_MF,data.player2_MF)
    if(data.playerFlag_MF == 1):
        if(data.MapInfoFlag == False ):
            data.WorldMap.drawNumbers(canvas)
    if(data.playerFlag_MF == -1):
        if(data.MapInfoFlag == False ):
            drawPlayer_1N(data, canvas, data.WorldMap, data.player1_MF) 
    if(data.player.selected != None):
        index = data.WorldMap.getIndex(data.player.selected[0],
                        data.player.selected[1])   
        if(index in data.player.center):
            fillSelected(canvas,index,data.player,
                    data.player.selected_color, data.WorldMap)
    drawFog(canvas,data.WorldMap,data.player)
    if(data.MapInfoFlag == True):
        MapInfo(data.WorldMap,canvas)
        canvas.create_text(800//2, data.height - 30, 
            text = "Press q to leave", fill = "Green", font = "Times 40")
    if(data.Fileflag == True):
        drawFlag(canvas,data)
        canvas.create_text(800//2, data.height - 30, 
            text = "Click one File and Press q to leave", fill = "Green", 
            font = "Times 40")
    
####################################   
# playGame mode_Attack
####################################
def A_MFleftMousePressed(event, data):
    if(event.x > 1002 and event.y > 430 and event.x < 1082 and event.y < 470):
        data.C_MF_Color = "white"
        data.AS_selected.clear()
        data.mode = "playGame_Confirm_MF"
    if(event.x > 915 and event.y > 430 and event.x < 995 and event.y < 470):
        ResetToDeploy(data)
        data.mode = "playGame_Deploy_MF"
    if(event.x > 950 and event.y > 490 and event.x < 1050 and event.y < 530):
        data.mode = "splashScreen"
        init(data)
    if(event.x > 915 and event.y > 310 and event.x < 995 and event.y < 330):
        startOver(data)
    if(event.x > 915 and event.y > 370 and event.x < 995 and event.y < 410):
        data.Fileflag = True 
    if(data.Fileflag == True):
        data.LoadGame_flag = Choose_FILE(event.x,event.y,data)
        SaveGame(data)
    # WorldMap
    if(isLegal_Attack(data.player, event.x, event.y, data.WorldMap) and 
        data.selectedFlag_AMF == 1 and 
        data.WorldMap.attack_value[data.player.selected] > 0):
        index = data.WorldMap.getIndex(event.x, event.y)
        end = data.WorldMap.centers[index]
        start = data.player.selected
        data.player.append_attack((data.player.selected, end))
        if(len(data.player.attack_areas) != len(set(data.player.attack_areas))):
            data.player.attack_areas.remove((data.player.selected,end))
        elif(len(data.player.attack_areas) == len(set(data.player.attack_areas))):
                data.player.attackNumber[(start,end)] = 1
                data.WorldMap.attack_value[data.player.selected] -= 1
    if(event.x > 1010 and event.y > 370 and event.x < 1090 and event.y < 410):
        data.MapInfoFlag = True
    for index in range(len(data.AS_Height)):
        if(len(data.AS_selected) < 2):
            if(event.x > 800 and event.y > data.AS_Height[index][0] and
                event.x < 900 and event.y < data.AS_Height[index][1]): 
                data.AS_selected.append(index)
    if(event.x > 1002 and event.y > 310 and event.x < 1082 and event.y < 350):
        data.mode = "gameOver"

def A_MFrightMousePressed(event, data):
    # WorldMap
    if(testInOwnedArea(data.player,data.WorldMap,event.x,event.y) != None):
        data.selectedFlag_AMF = 1
        start = testInOwnedArea(data.player,data.WorldMap,event.x,event.y)
        data.attackFlag_MF = 1
        data.player.selected = start
    if(testInOwnedArea(data.player,data.WorldMap,event.x,event.y) == None):
        data.selectedFlag_AMF = 0  

def A_MFKeyPressed(event, data):
    if(event.keysym == "d" and len(data.AS_selected) == 1):
        index =  data.AS_selected[0]
        start = data.player.attack_areas[index][0]
        end = data.player.attack_areas[index][1]
        number = data.player.attackNumber[(start,end)]
        data.player.attack_areas.pop(index)
        data.player.attackNumber[(start,end)] = 0
        data.WorldMap.attack_value[data.player.selected] += number
        data.AS_selected.remove(index)
    elif(event.keysym == "Up" and len(data.AS_selected) == 1):
        index =  data.AS_selected[0]
        end = data.player.attack_areas[index][1]
        start = data.player.attack_areas[index][0]
        if(data.WorldMap.attack_value[start] > 0):
            data.player.attackNumber[(start,end)] += 1
            data.WorldMap.attack_value[start] -= 1
    elif(event.keysym == "Down" and len(data.AS_selected) == 1):
        index =  data.AS_selected[0]
        end = data.player.attack_areas[index][1]
        start = data.player.attack_areas[index][0]
        if(data.player.attackNumber[(start,end)] >=2):
            data.player.attackNumber[(start,end)] -= 1
            data.WorldMap.attack_value[start] += 1
    elif(event.keysym == "q"):
        data.MapInfoFlag = False
        data.Fileflag = False
    elif(event.keysym == "c"):
        if(len(data.AS_selected) > 0):
            data.AS_selected.pop()
    elif(event.keysym == "s" and len(data.AS_selected) == 2):
        index = [data.AS_selected[0], data.AS_selected[1]]
        temp = data.player.attack_areas[index[0]]
        data.player.attack_areas[index[0]] = data.player.attack_areas[index[1]]
        data.player.attack_areas[index[1]] = temp

def A_MFTimerFired(data):
    pass

def drawBackground_Attack_MF(canvas, data):
    canvas.create_rectangle(920, 140, 1070, 160, fill = "dark blue", width = 0)
    canvas.create_text(1000, 250, 
    text = "To attack or transfer, Left\nclick on a territory" +
    "\n you own then right click\non one of its neighbors.", fill = "white", 
        font = "Times 14")   
    canvas.create_image(955,450, image = data.image_Button)
    canvas.create_text(955, 450, text = "Deploy", fill = "white", 
         font = "Times 20") 
    canvas.create_image(1042,450,image = data.image_Button)
    canvas.create_text(1042, 450, text = "Confirm", fill = "white", 
         font = "Times 20")

def drawInstruction_A(canvas,data):
    canvas.create_text(1000, data.height - 120, text = "Right click to select" 
       ,fill ="green", font = "Times 18")
    canvas.create_text(1000, data.height - 90, text = "Left click to" + 
        "attack/Transfer", fill ="green", font = "Times 16")
    canvas.create_text(1000, data.height - 70, 
        text = "use c to pop one selection", fill ="green", font = "Times 16")
    canvas.create_text(1000, data.height - 50, 
        text="use s to switch 2 selections", fill = "green", font = "Times 16")
    canvas.create_text(1000, data.height - 30, 
        text = "use d to delete one selection"
        , fill = "green", font = "Times 16" )

def A_MFRedrawAll(canvas, data):
    canvas.create_image(400, data.height//2, image = 
        data.image_WorldMap_Game)
    canvas.create_image(1000, data.height//2, image = data.image_Bar)
    canvas.create_image(850, data.height//2, image = data.image_AS)
    drawBackground_Attack_MF(canvas, data)
    playGameBackGround(canvas, data)
    drawInstruction_A(canvas, data)
    # WorldMap
    data.WorldMap.fillColor(data,canvas,data.player1_MF,data.player2_MF)
    if(data.playerFlag_MF == 1):
        if(data.MapInfoFlag == False ):
            data.WorldMap.drawNumbers(canvas)
    if(data.playerFlag_MF == -1):
        if(data.MapInfoFlag == False ):
            drawPlayer_1N(data, canvas, data.WorldMap, data.player1_MF) 
    if(data.selectedFlag_AMF == 1 and data.player.selected != None):
        index = data.WorldMap.centers.index(data.player.selected)
        fillSelected(canvas,index,data.player,
                    data.player.selected_color, data.WorldMap)
    drawFog(canvas,data.WorldMap,data.player)
    drawAttack_Line(canvas,data.player)
    drawAttakSequence(data,canvas, data.WorldMap, data.player)
    if(data.MapInfoFlag == True):
        MapInfo(data.WorldMap,canvas)
        canvas.create_text(800//2, data.height - 30, 
            text = "Press q to leave", fill = "Green", font = "Times 40")
    if(data.Fileflag == True):
        drawFlag(canvas,data)
        canvas.create_text(800//2, data.height - 30, 
            text = "Click one File and Press q to leave", fill = "Green", 
            font = "Times 40")

def C_MFleftMousePressed(event, data):
    if(event.x > 1002 and event.y > 430 and event.x < 1082 and event.y < 470):
        data.player.selected = None
        data.mode = "playGame_Attack_MF"
    elif(event.x > 1002 and event.y > 310 and event.x < 1082 and event.y < 350):
        data.mode = "gameOver"
    elif(event.x > 915 and event.y > 430 and event.x < 995 and event.y < 470):
        data.player.selected = None
        ResetToDeploy(data)
        data.mode = "playGame_Deploy_MF"
    elif(event.x > 950 and event.y > 490 and event.x < 1050 and event.y < 530):
        data.mode = "splashScreen"
        init(data)
    elif(event.x > 915 and event.y > 370 and event.x < 995 and event.y < 410):
        data.Fileflag = True 
    elif(data.Fileflag == True):
        data.LoadGame_flag = Choose_FILE(event.x,event.y,data)
        SaveGame(data)
    elif(event.x > 915 and event.y > 310 and event.x < 995 and event.y < 330):
        startOver(data)
    elif(event.x > 1040 and event.y > 570 and event.x < 1090 and event.y < 670):
        if(data.player.Already_Deploy == data.player.total_Deploy):
            if(data.playerFlag_MF == -1):
                prepareForPlay(data)
                prepareForPlay_2(data)
                ConfirmCalc(data, data.player1_MF, data.player2_MF, data.WorldMap)
                Attack_End(data, data.WorldMap)
                if(len(data.player1_MF.center) == 0):
                    data.mode = "gameOver"
                elif(len(data.player2_MF.center) == 0):
                    data.playerFlag_MF == 1
                    data.mode = "gameOver"
                bonusCheck(data.WorldMap, data.player1_MF)
                bonusCheck(data.WorldMap, data.player2_MF)
            data.playerFlag_MF = - data.playerFlag_MF
            if(data.playerFlag_MF == 1):
                chanegByTurn(data.player1_MF, data)
                if(data.mode != "gameOver"):
                    data.mode = "play"
            if(data.playerFlag_MF == -1):
                chanegByTurn(data.player2_MF, data)
                data.cache.clear()
                data.tempC2 = []
                data.tempC1 = []
                if(data.Firstflag == True):
                    data.Firstflag  = False
                    if(data.mode != "gameOver"):
                        data.mode = "playGame_Deploy_MF"
                else:
                    if(data.mode != "gameOver"):
                        data.mode = "play_2"
        else:
            data.C_MF_Color = "red"
    elif(event.x > 1002 and event.y > 370 and event.x < 1082 and event.y < 410):
        data.MapInfoFlag = True
            
def C_MFrightMousePressed(event, data):
    pass

def C_MFKeyPressed(event, data):
    if(event.keysym == "q"):
        data.MapInfoFlag = False
        data.Fileflag = False

def C_MFTimerFired(data):
    pass

def drawBackground_Confirm_MF(canvas, data):
    canvas.create_rectangle(910, 180, 1060, 200, fill = "dark blue", width = 0)
    canvas.create_text(1000, 250, 
    text = "You must deploy\nall of " + 
    "your armies\n          first !!!", fill = data.C_MF_Color, 
        font = "Times 20 bold")  
    canvas.create_image(955,450,image = data.image_Button)
    canvas.create_text(955, 450, text = "Deploy", fill = "white", 
         font = "Times 20") 
    canvas.create_image(1042,450,image = data.image_Button)
    canvas.create_text(1042, 450, text = "Attack", fill = "white", 
         font = "Times 20")
    canvas.create_image(1000,620,image = data.image_Next_Turn)

def C_MFRedrawAll(canvas, data):
    canvas.create_image(1000, data.height//2, image = data.image_Bar)
    canvas.create_image(850, data.height//2, image = data.image_AS)
    canvas.create_image(400, data.height//2, image = 
        data.image_WorldMap_Game)
    drawBackground_Confirm_MF(canvas, data)
    playGameBackGround(canvas, data)
    data.WorldMap.fillColor(data,canvas,data.player1_MF,data.player2_MF)
    if(data.playerFlag_MF == 1):
        if(data.MapInfoFlag == False ):
            data.WorldMap.drawNumbers(canvas)
    if(data.playerFlag_MF == -1):
        if(data.MapInfoFlag == False ):
            drawPlayer_1N(data, canvas, data.WorldMap, data.player1_MF) 
    drawFog(canvas,data.WorldMap,data.player)
    drawAttack_Line(canvas,data.player)
    if(data.MapInfoFlag == True):
        MapInfo(data.WorldMap,canvas)
    drawAttakSequence(data,canvas, data.WorldMap, data.player)
    if(data.Fileflag == True):
        drawFlag(canvas,data)

####################################
# Play
####################################
def playleftMousePressed_Wrapper(data):
    data.play_Attackflag = False
    end_now = data.play_AS[0][1]
    start_now = data.play_AS[0][0]
    index_now = data.WorldMap.getIndex(end_now[0],end_now[1])
    data.play_P1data[data.PLAY_DV][(end_now[0],end_now[1])] = (
                data.replay_A[(start_now,end_now)][0])
    data.play_P1data[data.PLAY_DV][(start_now[0],start_now[1])] = (
                data.play_P1data[data.PLAY_DV_R][start_now])
    last_now = data.replay_A[(start_now,end_now)][1]
    if(index_now in data.play_P1data[data.PLAY_1C]):
        if(last_now == 0):
            if(index_now in data.play_P1data[data.PLAY_1C]):
                data.play_P1data[data.PLAY_1C].remove(index_now)
        elif(last_now == 1):pass
        elif(last_now == 2):
            if(index_now in data.play_P1data[data.PLAY_1C]):
                data.play_P1data[data.PLAY_1C].remove(index_now)
                data.play_P1data[data.PLAY_2C].append(index_now)
    elif(index_now in data.play_P1data[data.PLAY_2C]):
        if(last_now == 0):
            if(index_now in data.play_P1data[data.PLAY_2C]):
                data.play_P1data[data.PLAY_2C].remove(index_now)
        elif(last_now == 1):pass
        elif(last_now == 2):
            if(index_now in data.play_P1data[data.PLAY_2C]):
                data.play_P1data[data.PLAY_2C].remove(index_now)
                data.play_P1data[data.PLAY_1C].append(index_now)

def playleftMousePressed(event, data):
    if(event.x > 1010 and event.y > 340 and event.x < 1060 and event.y < 400):
        data.play_index += 1       
        if(data.play_index < len(data.AD_set)):
            data.play_Deployflag = True 
            data.play_Attackflag = False
        elif(data.play_index >= (len(data.AD_set) + len(data.play_AS))):
            Reset_Play_Data(data)
            data.mode = "playGame_Deploy_MF"
        elif(data.play_index >= len(data.AD_set)):
            (data.play_Deployflag,data.play_Attackflag) = (False, True)
            (data.play_AM_flag, index) = (True, data.play_index - len(data.AD_set))
            (start, end) = data.play_AS[index]
            if(data.ConquerFlag_play == False):
                data.play_P1data[data.PLAY_DV][start] -= data.play_AN[index]
            data.sx_play = data.play_AS[index][0][0]
    if(event.x > 940 and event.y > 340 and event.x < 990 and event.y < 400 
            and data.play_index >= 0):
        data.play_index -= 1
        if(data.play_index ==  len(data.AD_set) - 1):
           playleftMousePressed_Wrapper(data)
        if(data.play_index < len(data.AD_set)):
            data.play_Attackflag = False
            now = data.AD_index
            if((data.play_index == len(data.AD_set) - 1) or data.play_index < 0):
                data.play_P1data[data.PLAY_DV][data.WorldMap.centers[now]] =(
                data.AD_oldDeploy[data.WorldMap.centers[now]])
            else:
                pre = data.AD_preIndex[data.play_index]
                data.play_P1data[data.PLAY_DV][data.WorldMap.centers[pre]] = (
                    data.AD_oldDeploy[data.WorldMap.centers[pre]])
                data.play_P1data[data.PLAY_DV][data.WorldMap.centers[now]] = (
                    data.AD_oldDeploy[data.WorldMap.centers[now]]) 
            data.play_Deployflag = True
        else:
            index = data.play_index - len(data.AD_set)
            data.sx_play = (
                data.play_AS[index][0][0]) 
            path_now = data.play_AS[data.play_index - len(data.AD_set)]
            (start_now, end_now) = (path_now[0], path_now[1])
            if((index == len(data.play_AS) - 1) or 
                    data.play_index < len(data.AD_set)):
                data.play_P1data[data.PLAY_DV][(end_now[0],end_now[1])] = (
                        data.replay_A[(start_now,end_now)][0])
                index_now = data.WorldMap.getIndex(end_now[0],end_now[1])
                last_now = data.replay_A[(start_now, end_now)][1]
                if(index_now in data.play_P1data[data.PLAY_1C_D]):
                    if(last_now == 0):
                        if(index_now in data.play_P1data[data.PLAY_1C_D]):
                            data.play_P1data[data.PLAY_1C_D].remove(index_now)
                    elif(last_now == 1):pass
                    elif(last_now == 2):
                        if(index_now in data.play_P1data[data.PLAY_1C_D]):
                            data.play_P1data[data.PLAY_1C_D].remove(index_now)
                            data.play_P1data[data.PLAY_2C_D].append(index_now)
                elif(index_now in data.play_P1data[data.PLAY_2C_D]):
                    if(last_now == 0):
                        if(index_now in data.play_P1data[data.PLAY_2C_D]):
                            data.play_P1data[data.PLAY_2C_D].remove(index_now)
                    elif(last_now == 1):pass
                    elif(last_now == 2):
                        if(index_now in data.play_P1data[data.PLAY_2C_D]):
                            data.play_P1data[data.PLAY_2C_D].remove(index_now)
                            data.play_P1data[data.PLAY_1C_D].append(index_now)
            else:
                path_next = data.play_AS[index + 1]
                (start_next, end_next) = (path_next[0], path_next[1])
                data.play_P1data[data.PLAY_DV][(end_now[0],end_now[1])] = (
                        data.replay_A[(start_now,end_now)][0])
                data.play_P1data[data.PLAY_DV][(start_next[0],start_next[1])] += (
                        data.play_AN[(index + 1)])
                if(end_next != end_now):
                    data.play_P1data[data.PLAY_DV][(end_next[0],end_next[1])] = (
                        data.replay_A[(start_next,end_next)][0])
                index_now = data.WorldMap.getIndex(end_now[0],end_now[1])
                index_next  = data.WorldMap.getIndex(end_next[0],end_next[1])
                last_now = data.replay_A[(start_now,end_now)][1]
                last_next = data.replay_A[(start_next,end_next)][1]
                if(index_now in data.play_P1data[data.PLAY_1C_D] or
                    index_now in data.play_P1data[data.PLAY_2C_D]):
                    if(index_now in data.play_P1data[data.PLAY_1C_D]):
                        if(last_now == 0):
                            if(index_now in data.play_P1data[data.PLAY_1C_D]):
                                data.play_P1data[data.PLAY_1C_D].remove(index_now)
                        elif(last_now == 1):pass
                        elif(last_now == 2):
                            if(index_now in data.play_P1data[data.PLAY_1C_D]):
                                data.play_P1data[data.PLAY_1C_D].remove(index_now)
                                data.play_P1data[data.PLAY_2C_D].append(index_now)
                    elif(index_now in data.play_P1data[data.PLAY_2C_D]):
                        if(last_now == 0):
                            if(index_now in data.play_P1data[data.PLAY_2C_D]):
                                data.play_P1data[data.PLAY_2C_D].remove(index_now)
                        elif(last_now == 2):pass
                        elif(last_now == 1):
                            if(index_now in data.play_P1data[data.PLAY_2C_D]):
                                data.play_P1data[data.PLAY_2C_D].remove(index_now)
                                data.play_P1data[data.PLAY_1C_D].append(index_now)
                if(index_next in data.play_P1data[data.PLAY_1C_D] or
                    index_next in data.play_P1data[data.PLAY_2C_D]):    
                    if(index_next in data.play_P1data[data.PLAY_1C_D]):
                        if(last_next == 0):
                            if(index_next in data.play_P1data[data.PLAY_1C_D]):
                                data.play_P1data[data.PLAY_1C_D].remove(index_next)
                        elif(last_next == 1):pass
                        elif(last_next == 2):
                            if(index_next in data.play_P1data[data.PLAY_1C_D]):
                                data.play_P1data[data.PLAY_1C_D].remove(index_next)
                                data.play_P1data[data.PLAY_2C_D].append(index_next)
                    elif(index_next in data.play_P1data[data.PLAY_2C_D]):
                        if(last_next == 0):
                            if(index_next in data.play_P1data[data.PLAY_2C_D]):
                                data.play_P1data[data.PLAY_2C_D].remove(index_next)
                        elif(last_next == 2):pass
                        elif(last_next == 1):
                            if(index_next in data.play_P1data[data.PLAY_2C_D]):
                                data.play_P1data[data.PLAY_2C_D].remove(index_next)
                                data.play_P1data[data.PLAY_1C_D].append(index_next)
                data.play_AM_flag = True
    if(event.x > 950 and event.y > 440 and event.x < 1050 and event.y < 480):
        Reset_Play_Data(data)
        data.mode = "playGame_Deploy_MF"
       

def playKeyPressed(event, data):
    pass

def playTimerFired(data):
    if(data.play_Deployflag == True):
        if(data.AD_index in data.AD_cy):
            data.AD_cy[data.AD_index] -= 3
    if(data.play_AM_flag == True):
        if(data.play_AA_flag == "+"):
            data.sx_play += 3
        if(data.play_AA_flag == "-"):
            data.sx_play -= 3

def playBackground(canvas, data):
    canvas.create_image(400, data.height//2, image = data.image_WorldMap_Game)
    canvas.create_image(1000, data.height//2, image = data.image_Bar)
    canvas.create_image(850, data.height//2, image = data.image_AS)
    canvas.create_text(1000, 70, text = "Replay",
        fill = "white", font = "Times 30 bold")
    canvas.create_text(1000, 170, 
        text = "Start from deploy stage\n    and move by your\n"
          + "    attack sequences", fill = "white", font = "Times 17 bold")
    canvas.create_text(1000, 270, text = "STEPS", fill = "white", 
        font = "Times 30") 
    canvas.create_image(1000,370, image = data.image_ForBack)
    canvas.create_image(1000,460,image = data.image_Button)
    canvas.create_text(1000, 460, text = "Skip", fill = "white", 
        font = "Times 20 bold") 


def playRedrawAll(canvas, data):
    playBackground(canvas, data)
    # WorldMap
    fillColor_play(data, canvas,data.WorldMap,data.player1_MF,data.player2_MF,
        data.play_P1data)
    drawFog_Play(canvas,data.play_P1data,data.WorldMap,data)
    drawNumbers_Play(canvas, data.play_P1data[data.PLAY_DV], data.WorldMap)
    drawPlay_Deploy(canvas, data)
    drawPlay_Attack(canvas, data, data.WorldMap)
    drawPlay_AttackAnimation(canvas, data.WorldMap, data)
    
####################################
# Play_2
####################################
def play_2leftMousePressed(event, data):
    if(event.x > 1010 and event.y > 340 and event.x < 1060 and event.y < 400):
        data.play_index += 1       
        if(data.play_index < len(data.AD_set)):
            data.play_Deployflag = True 
            data.play_Attackflag = False
        elif(data.play_index >= (len(data.AD_set) + len(data.play_AS))):
            Reset_Play_Data(data)
            data.mode = "playGame_Deploy_MF"
        elif(data.play_index >= len(data.AD_set)):
            (data.play_Deployflag,data.play_Attackflag) = (False, True)
            (data.play_AM_flag, index) = (True, data.play_index - len(data.AD_set))
            (start, end) = data.play_AS[index]
            if(data.ConquerFlag_play == False):
                data.play_P2data[data.PLAY_DV][start] -= data.play_AN[index]
            data.sx_play = data.play_AS[index][0][0]
    if(event.x > 940 and event.y > 340 and event.x < 990 and event.y < 400 
            and data.play_index >= 0):
        data.play_index -= 1
        if(data.play_index ==  len(data.AD_set) - 1):
            data.play_Attackflag = False
            end_now = data.play_AS[0][1]
            start_now = data.play_AS[0][0]
            index_now = data.WorldMap.getIndex(end_now[0],end_now[1])
            data.play_P2data[data.PLAY_DV][(end_now[0],end_now[1])] = (
                        data.replay_A[(start_now,end_now)][0])
            data.play_P2data[data.PLAY_DV][(start_now[0],start_now[1])] = (
                        data.play_P2data[data.PLAY_DV_R][start_now])
            last_now = data.replay_A[(start_now,end_now)][1]
            if(index_now in data.play_P2data[data.PLAY_1C]):
                if(last_now == 0):
                    if(index_now in data.play_P2data[data.PLAY_1C]):
                        data.play_P2data[data.PLAY_1C].remove(index_now)
                elif(last_now == 1):pass
                elif(last_now == 2):
                    if(index_now in data.play_P2data[data.PLAY_1C]):
                        data.play_P2data[data.PLAY_1C].remove(index_now)
                        data.play_P2data[data.PLAY_2C].append(index_now)
            elif(index_now in data.play_P2data[data.PLAY_2C]):
                if(last_now == 0):
                    if(index_now in data.play_P2data[data.PLAY_2C]):
                        data.play_P2data[data.PLAY_2C].remove(index_now)
                elif(last_now == 1):pass
                elif(last_now == 2):
                    if(index_now in data.play_P2data[data.PLAY_2C]):
                        data.play_P2data[data.PLAY_2C].remove(index_now)
                        data.play_P2data[data.PLAY_1C].append(index_now)
        if(data.play_index < len(data.AD_set)):
            data.play_Attackflag = False
            now = data.AD_index
            if((data.play_index == len(data.AD_set) - 1) or data.play_index < 0):
                data.play_P2data[data.PLAY_DV][data.WorldMap.centers[now]] =(
                data.AD_oldDeploy[data.WorldMap.centers[now]])
            else:
                pre = data.AD_preIndex[data.play_index]
                data.play_P2data[data.PLAY_DV][data.WorldMap.centers[pre]] = (
                    data.AD_oldDeploy[data.WorldMap.centers[pre]])
                data.play_P2data[data.PLAY_DV][data.WorldMap.centers[now]] = (
                    data.AD_oldDeploy[data.WorldMap.centers[now]]) 
            data.play_Deployflag = True
        else:
            index = data.play_index - len(data.AD_set)
            data.sx_play = (
                data.play_AS[index][0][0]) 
            path_now = data.play_AS[data.play_index - len(data.AD_set)]
            (start_now, end_now) = (path_now[0], path_now[1])
            if((index == len(data.play_AS) - 1) or 
                    data.play_index < len(data.AD_set)):
                data.play_P2data[data.PLAY_DV][(end_now[0],end_now[1])] = (
                        data.replay_A[(start_now,end_now)][0])
                index_now = data.WorldMap.getIndex(end_now[0],end_now[1])
                last_now = data.replay_A[(start_now, end_now)][1]
                if(index_now in data.play_P2data[data.PLAY_1C_D]):
                    if(last_now == 0):
                        if(index_now in data.play_P2data[data.PLAY_1C_D]):
                            data.play_P2data[data.PLAY_1C_D].remove(index_now)
                    elif(last_now == 1):pass
                    elif(last_now == 2):
                        if(index_now in data.play_P2data[data.PLAY_1C_D]):
                            data.play_P2data[data.PLAY_1C_D].remove(index_now)
                            data.play_P2data[data.PLAY_2C_D].append(index_now)
                elif(index_now in data.play_P2data[data.PLAY_2C_D]):
                    if(last_now == 0):
                        if(index_now in data.play_P2data[data.PLAY_2C_D]):
                            data.play_P2data[data.PLAY_2C_D].remove(index_now)
                    elif(last_now == 1):pass
                    elif(last_now == 2):
                        if(index_now in data.play_P2data[data.PLAY_2C_D]):
                            data.play_P2data[data.PLAY_2C_D].remove(index_now)
                            data.play_P2data[data.PLAY_1C_D].append(index_now)
            else:
                path_next = data.play_AS[index + 1]
                (start_next, end_next) = (path_next[0], path_next[1])
                data.play_P2data[data.PLAY_DV][(end_now[0],end_now[1])] = (
                        data.replay_A[(start_now,end_now)][0])
                data.play_P2data[data.PLAY_DV][(start_next[0],start_next[1])] += (
                        data.play_AN[(index + 1)])
                if(end_next != end_now):
                    data.play_P2data[data.PLAY_DV][(end_next[0],end_next[1])] = (
                        data.replay_A[(start_next,end_next)][0])
                index_now = data.WorldMap.getIndex(end_now[0],end_now[1])
                index_next  = data.WorldMap.getIndex(end_next[0],end_next[1])
                last_now = data.replay_A[(start_now,end_now)][1]
                last_next = data.replay_A[(start_next,end_next)][1]
                if(index_now in data.play_P2data[data.PLAY_1C_D] or
                    index_now in data.play_P2data[data.PLAY_2C_D]):
                    if(index_now in data.play_P2data[data.PLAY_1C_D]):
                        if(last_now == 0):
                            if(index_now in data.play_P2data[data.PLAY_1C_D]):
                                data.play_P2data[data.PLAY_1C_D].remove(index_now)
                        elif(last_now == 1):pass
                        elif(last_now == 2):
                            if(index_now in data.play_P2data[data.PLAY_1C_D]):
                                data.play_P2data[data.PLAY_1C_D].remove(index_now)
                                data.play_P2data[data.PLAY_2C_D].append(index_now)
                    elif(index_now in data.play_P2data[data.PLAY_2C_D]):
                        if(last_now == 0):
                            if(index_now in data.play_P2data[data.PLAY_2C_D]):
                                data.play_P2data[data.PLAY_2C_D].remove(index_now)
                        elif(last_now == 2):pass
                        elif(last_now == 1):
                            if(index_now in data.play_P2data[data.PLAY_2C_D]):
                                data.play_P2data[data.PLAY_2C_D].remove(index_now)
                                data.play_P2data[data.PLAY_1C_D].append(index_now)
                if(index_next in data.play_P2data[data.PLAY_1C_D] or
                    index_next in data.play_P2data[data.PLAY_2C_D]):    
                    if(index_next in data.play_P2data[data.PLAY_1C_D]):
                        if(last_next == 0):
                            if(index_next in data.play_P2data[data.PLAY_1C_D]):
                                data.play_P2data[data.PLAY_1C_D].remove(index_next)
                        elif(last_next == 1):pass
                        elif(last_next == 2):
                            if(index_next in data.play_P2data[data.PLAY_1C_D]):
                                data.play_P2data[data.PLAY_1C_D].remove(index_next)
                                data.play_P2data[data.PLAY_2C_D].append(index_next)
                    elif(index_next in data.play_P2data[data.PLAY_2C_D]):
                        if(last_next == 0):
                            if(index_next in data.play_P2data[data.PLAY_2C_D]):
                                data.play_P2data[data.PLAY_2C_D].remove(index_next)
                        elif(last_next == 2):pass
                        elif(last_next == 1):
                            if(index_next in data.play_P2data[data.PLAY_2C_D]):
                                data.play_P2data[data.PLAY_2C_D].remove(index_next)
                                data.play_P2data[data.PLAY_1C_D].append(index_next)
                data.play_AM_flag = True
    if(event.x > 950 and event.y > 440 and event.x < 1050 and event.y < 480):
        Reset_Play_Data(data)
        data.mode = "playGame_Deploy_MF"
       
def play_2KeyPressed(event, data):
    pass

def play_2TimerFired(data):
    pace = 3
    if(data.play_Deployflag == True):
        if(data.AD_index in data.AD_cy):
            data.AD_cy[data.AD_index] -= pace
    if(data.play_AM_flag == True):
        if(data.play_AA_flag == "+"):
            data.sx_play += pace
        if(data.play_AA_flag == "-"):
            data.sx_play -= pace

def playRedrawAll_2(canvas, data):
    playBackground(canvas, data)
    # WorldMap
    fillColor_play(data, canvas,data.WorldMap,data.player1_MF,data.player2_MF,
        data.play_P2data)
    drawFog_Play_2(canvas,data.play_P2data,data.WorldMap,data)
    drawNumbers_Play(canvas, data.play_P2data[data.PLAY_DV], data.WorldMap)
    drawPlay_Deploy_2(canvas, data)
    drawPlay_Attack_2(canvas, data, data.WorldMap)
    drawPlay_AttackAnimation_2(canvas, data.WorldMap, data)

####################################
# Game Over
####################################
def gameOverMouseMotion(event, data):
    if(event.x > 510 and event.y > 620 and event.x < 590 and event.y < 660):
        data.GOcolor = "blue"
    else:
        data.GOcolor = "green"

def gameOverKeyPressed(event,data):
    pass

def gameOverleftMousePressed(event,data):
    if(event.x > 510 and event.y > 620 and event.x < 590 and event.y < 660):
        init(data)
        data.mode = "splashScreen"

def gameOverTimerFired(data):
    data.fontSize_GO += 1
    size = 30
    maximum = 120
    if(data.fontSize_GO == maximum):
        data.fontSize_GO = size

def gameOverRedrawAll(canvas,data):
    canvas.create_image(data.width//2, data.height//2,
                image = data.GameOver_image)
    canvas.create_text(540, data.height - 40, text = "EXIT", font = 
        "Times 30 bold", fill = data.GOcolor)
    if(data.playerFlag_MF == 1): 
        canvas.create_text(data.width//2, data.height//2, 
            text = "PLAYER 2 WIN ^_^", fill = "magenta", 
            font = "Times " + str(data.fontSize_GO) + " bold")
    else:
        canvas.create_text(data.width//2, data.height//2, 
            text = "PLAYER 1 WIN ^_^", fill = "magenta", 
            font = "Times " + str(data.fontSize_GO) + " bold")

####################################
# use the run function as-is
####################################

def Warlight(width=500, height=500):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()    

    def leftMousePressedWrapper(event, canvas, data):
        leftMousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def rightMousePressedWrapper(event, canvas, data):
        rightMousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def mouseMotionWrapper(event, canvas, data):
        mouseMotion(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.height = 680
    ratio = 0.618
    data.width = data.height / ratio
    data.timerDelay = 1 # milliseconds
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    init(data)
    root.bind("<Button-1>", lambda event:
                            leftMousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    canvas.bind("<Motion>", lambda event:
                            mouseMotionWrapper(event, canvas, data))
    root.bind("<Button-2>", lambda event:
                            rightMousePressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

Warlight()