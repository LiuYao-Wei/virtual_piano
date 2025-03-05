
import os.path
import cv2
import mediapipe as mp
import pygame
import random

##//////變數宣告區/////##
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
LINE = (0,255,0)
rockColor = (150,150,150)
WIDTH = 800
HEIGHT = 500
totoal_rect = 0     #總方塊數
score = 0           #為家得分
#定義琴鍵的寬度、高度、間隔
rect_width = WIDTH // 10
rect_height = (HEIGHT // 2) // 2
rect_margin = 50
#方框生成位置
boxList = [200,280,360,440,520]
##///////////////////##

#↓↓↓開鏡頭，0為筆電本身↓↓↓
cap = cv2.VideoCapture(0)
#↓↓↓宣告使用手部模型↓↓↓
mpHands = mp.solutions.hands
#Hands()
hands = mpHands.Hands(max_num_hands=2,min_detection_confidence=0.8,min_tracking_confidence=0.8)
#畫點的方法
myDraw = mp.solutions.drawing_utils
#設定draw_landmarks方法畫出的圖案

#設定pygame初始值
pygame.init()
pygame.display.set_caption("虛擬鋼琴")
pygame.mixer.init()
#設定pygame的螢幕大小
screen = pygame.display.set_mode((WIDTH,HEIGHT))
#DrawingSpec(點的顏色(bgr), 點的粗度, 點的半徑)
#handStyle為點的樣式
handStyle = myDraw.DrawingSpec(color=(0,0,255), thickness=5)

#handConStyle為線的樣式
handConStyle = myDraw.DrawingSpec(color=(0,255,0), thickness=10)

#拇指、食指、中指、無名指、小指
tipId = [4,8,12,16,20]
#fignerlist = []
presslist = [0,0,0,0,0]

#載入音樂
do_sound = pygame.mixer.Sound(os.path.join("sound","Do_new.wav"))
re_sound = pygame.mixer.Sound(os.path.join("sound","Re_new.wav"))
mi_sound = pygame.mixer.Sound(os.path.join("sound","Me_new.wav"))
fa_sound = pygame.mixer.Sound(os.path.join("sound","Fa_new.wav"))
so_sound = pygame.mixer.Sound(os.path.join("sound","So_new.wav"))

class Box(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((40,50))
        self.image.fill(rockColor)
        self.rect = self.image.get_rect()           #把image的東西用rect方框框起來
        self.ID = random.randrange(0,5)   #ID為對應於手指的編號位置
        self.rect.x = boxList[self.ID]
        self.rect.y = 0
        self.speedy = random.randrange(2,6)

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()
            boxs = Box()
            all_sprites.add(boxs)
            boxGroup.add(boxs)

    def getID(self):
        return self.ID

##///////////////////////##
#Group設定，將每個元素放入各自group中
all_sprites = pygame.sprite.Group()
boxGroup = pygame.sprite.Group()

#產生落下的方塊，隨機數量
for i in range(1,3):
    boxs = Box()
    all_sprites.add(boxs)
    boxGroup.add(boxs)
    totoal_rect = totoal_rect + 1

##///////////////////////##
while True:

    #↓↓↓ pygame程式區 ↓↓↓

    #判斷遊戲結束區域
    if totoal_rect > 50:
        break



    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
    # -------pygame的畫面設定----------
    screen.fill(WHITE)  #將畫面設定成白色
    #rect_x = 5 * rect_width + rect_margin
    for i in range(3,8):
        rect_x = (i * rect_width + rect_margin) - 100
        rect_y = HEIGHT // 2 + rect_margin
        rect_color = RED if presslist[i-3] == 1 else BLACK
        #寬 : rect_width - 2 * rect_margin, 高 : rect_height - 2 * rect_margin
        #rect畫法 : (畫面 、 顏色 、 座標(左上角x座標 , 左上角y座標 , 長方形寬度 , 長方形高度))
        pygame.draw.rect(screen, rect_color,(rect_x, rect_y, 60, 105))
    #pygame.draw.rect(screen, LINE, (0, HEIGHT // 2 + rect_margin, WIDTH, 10))
    all_sprites.update()        #將sprits內的所有元素更新(XY座標等等)

    #判斷碰撞
    for box in boxGroup:
        #print('rect_y=',rect_y)
        #print(presslist[box.getID()])
        #print('box.rect.bottom=',box.rect.bottom)
        #判斷方塊是否在鍵盤的按鍵下//300、405
        if (box.rect.bottom > rect_y and box.rect.bottom < (rect_y + 105) and presslist[box.getID()] == 1) or (box.rect.top > rect_y and box.rect.top < (rect_y + 105) and presslist[box.getID()] == 1):
            #print('delete--------------------------------------------------------------------------------------------------')
            box.kill()
            boxs = Box()
            all_sprites.add(boxs)
            boxGroup.add(boxs)
            totoal_rect = totoal_rect + 1
            score = score + 1


    all_sprites.draw(screen)    #將sprits的所有元素畫出
    pygame.display.update()     #更新畫面，將顏色顯示在pygame的視窗中

    #↓↓↓ 以下為手部偵測程式區 ↓↓↓
    ret,img = cap.read()

    if ret:
        #↓↓↓ 將opencv擷取到的圖片，從bgr轉成rgb ↓↓↓
        imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

        # ↓↓↓ img為整個畫面，shape[0]為畫面的Y軸也就是高度、shape[1]為X軸也就是寬度 ↓↓↓
        imgHeight = img.shape[0]
        imgWidth = img.shape[1]

        result = hands.process(imgRGB)
        #print(result)
        #print(result.mult_hand_landmarks)
        #↓↓↓↓ if 有偵測到手的話 ↓↓↓↓
        if result.multi_hand_landmarks:
            #print(result.multi_hand_landmarks)
            #↓↓↓ 偵測到的結果(21個點)存入handLms
            for handLms in result.multi_hand_landmarks:
                #draw_landmarks(畫的圖片, 偵測的點, 點的連線)
                myDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
                #enumerate(index, value)，所以回傳哪個點與點的數值
                # ↓↓↓↓ fignerlist存入0~20點的座標與x,y的位置 ↓↓↓↓
                #print(handLms.landmark)
                fignerlist = [[i , int(lm.x * imgWidth), int(lm.y * imgHeight)] for i, lm in enumerate(handLms.landmark)]
                print(fignerlist)

                if len(fignerlist) != 0:    #有偵測到手指座標
                    #id為偵測tipID中的每個手指座標
                    for id in range(0,5):
                        #到fignerlist中取得tipId中的手指座標，並判斷其Y座標-->[][2]，2為Y座標。
                        if fignerlist[tipId[id]][2] > fignerlist[0][2]:     #判斷tipID中的手指是否比掌心還低
                            presslist[id] = 1
                            print(f'{tipId[id]}按下')                        #顯示手指是否有按下
                        else:
                            presslist[id] = 0
                        #print(presslist)                                    #顯示指尖陣列 --> 1代表按下、0代表沒按下
                    if presslist[0] == 1:
                        do_sound.play()
                    if presslist[1] == 1:
                        re_sound.play()
                    if presslist[2] == 1:
                        mi_sound.play()
                    if presslist[3] == 1:
                        fa_sound.play()
                    if presslist[4] == 1:
                        so_sound.play()



                # i為點的號碼， lm為點在螢幕中的比例位置，並使用.x與.y來回傳lm此參數的x與y座標(lm.x會顯示0.5代表該點在螢幕的中間)
                #print(i, lm.x, lm.y)


                # ↓↓↓ 將比例乘上實際的寬高，得到實際座標 ↓↓↓
                #xP = int(lm.x * imgWidth)
                #yP = int(lm.y * imgHeight)
                #print(i, xP, yP)


        cv2.imshow('img',img)
    if cv2.waitKey(1) == ord('q'):
        break

