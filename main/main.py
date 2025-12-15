from tkinter import *
from tkinter import font
import math, os, ctypes, time, random, pygame
from PIL import Image, ImageTk, ImageOps


#x, y값 갖는 벡터값
#pos[0], pos[1] 보다는 pos.x, pos.y 가 직관적이라고 생각해서 제작
class Vector2:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    #값 변환.
    def setValue(self, x, y):
        self.x = x
        self.y = y

    #값을 다른 벡터의 값으로 변환
    def setValueToVec(self, vec):
        self.setValue(vec.x, vec.y)

    #값에 곱해서 변경
    def multiple(self, value):
        self.setValue(self.x * value, self.y * value)

    #다른 벡터 더해서 값 변경
    def add(self, addvec):
        self.setValue(self.x + addvec.x, self.y + addvec.y)

    #튜플로 반환
    def getTuple(self):
        return (self.x, self.y)
    
    #곱한 벡터 반환
    def getMultiple(self, value):
        return Vector2(self.x * value, self.y * value)
    
    #자기 자신 반환 - 기본 스텟 복사용
    def getSelf(self):
        return Vector2(self.x, self.y)
    
    
    @staticmethod
    #두 지점 사이의 거리 반환
    def _getDistance(A, B):
        return math.sqrt((B.x - A.x) ** 2 + (B.y - A.y) ** 2)
    @staticmethod
    def _getRadian(A, B):
        return math.atan2(B.y - A.y, B.x - A.x)
    
    @staticmethod
    def _getVectorFromRadian(radian, multiple = 1):
        return Vector2(math.cos(radian) * multiple, math.sin(radian) * multiple)
    
    @staticmethod
    def _getSum(A, B):
        return Vector2(A.x + B.x, A.y + B.y)

#사운드매니저
class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        
        self.is_initialized = True
        self.sfx_sounds = {}    # 효과음을 저장할 딕셔너리
        self.music_file = None  # 현재 배경음악 파일 경로
        
        self.sfx_volume = 0.5   # 기본 효과음 볼륨 (0.0 ~ 1.0)
        self.music_volume = 0.3 # 기본 배경음악 볼륨 (0.0 ~ 1.0)

    ## 배경음악 관리
    def load_music(self, file_path, initial_volume=None):
        if not self.is_initialized:
            return
        
        if not os.path.exists(file_path):
            return

        #사용할 볼륨 값 결정
        if initial_volume is not None:
            volume_to_set = max(0.0, min(1.0, initial_volume))
            self.music_volume = volume_to_set 
        else:
            volume_to_set = self.music_volume

        #파일 로드
        pygame.mixer.music.load(file_path)
        self.music_file = file_path
            
        #로드 후 볼륨 설정
        pygame.mixer.music.set_volume(volume_to_set)
            
            
            

    def play_music(self, loops=-1): #-1 = 무한반복
        if not self.is_initialized or not self.music_file:
            return
        
        
        pygame.mixer.music.play(loops)
            


    def stop_music(self):
        if not self.is_initialized:
            return
        
        pygame.mixer.music.stop()
        
    
    #배경음악 볼륨 설정
    def set_music_volume(self, volume):
        if not self.is_initialized:
            return
        
        self.music_volume = max(0.0, min(1.0, volume)) # 0.0에서 1.0 사이로 제한
        pygame.mixer.music.set_volume(self.music_volume)

    #효과음 관리
    def load_sfx(self, name, file_path, initial_volume=0.5):
        if not self.is_initialized:
            return
        
        if not os.path.exists(file_path):
            return

        sound = pygame.mixer.Sound(file_path)

        self.sfx_volume = max(0.0, min(1.0, initial_volume)) # 인스턴스 변수에 저장
        sound.set_volume(self.sfx_volume) 
            
        self.sfx_sounds[name] = sound
            


    def play_sfx(self, name):
        if not self.is_initialized:
            return

        sound = self.sfx_sounds.get(name)
        if sound:
            sound.play()

    def set_sfx_volume(self, name, volume):
        if not self.is_initialized:
            return
        
        sound = self.sfx_sounds.get(name)
        if sound:
            # 0.0 ~ 1.0 사이로 제한
            new_volume = max(0.0, min(1.0, volume)) 
            sound.set_volume(new_volume)


    #종료 처리
    def quit(self):
        if self.is_initialized:
            self.stop_music()
            pygame.mixer.quit()

#애니메이션 오브젝트
class AnimationObject:
    def __init__(self, firstImage, pos, size, moveSpeed=0, animationSpeed = 0):
        self.pos = Vector2(pos[0], pos[1])
        self.size = Vector2(size[0], size[1])

        self.animations = [[self.LoadImage(firstImage, self.size.getTuple())]]
        self.nowAnimationIndex = 0 #현재 재생중인 애니메이션 인덱스
        self.animationTick = 0
        self.animationSpeed = animationSpeed
        self.nowFrame = 0

        self.image = ImageTk.PhotoImage(self.animations[0][0])
        self.me = Game.instance.canvas.create_image(self.pos.x, self.pos.y, image=self.image)

        self.radian = 0
        self.vec = Vector2()
        self.moveSpeed = moveSpeed
        self.isLookRight = True
        self.isdead = False

    #애니메이션 추가
    def addAnimation(self, animation):
        temp = [self.LoadImage(x, self.size.getTuple()) for x in animation]
        self.animations.append(temp)
    
    #애니메이션 수정
    def setAnimation(self, index, animation):
        if (index < len(self.animations)):
            temp = [self.LoadImage(x, self.size.getTuple()) for x in animation]
            self.animations[index] = temp
            if self.nowAnimationIndex == index:
                self.changeImage(self.animations[self.nowAnimationIndex][self.nowFrame])


    #애니메이션 프레임 전환
    def nextFrame(self):
        if self.animationSpeed != 0:
            self.animationTick += Game.instance.deltatime
            if self.animationTick > self.animationSpeed:
                self.animationTick = 0
                if self.isdead:
                    if self.nowFrame < len(self.animations[self.nowAnimationIndex]):
                        self.changeImage(self.animations[self.nowAnimationIndex][self.nowFrame])
                        self.nowFrame += 1
                    else:
                        self.destroy()
                else:
                    self.changeImage(self.animations[self.nowAnimationIndex][self.nowFrame])
                    self.nowFrame = (self.nowFrame + 1) % len(self.animations[self.nowAnimationIndex])
    
    #재생할 애니메이션 전환
    def changeAnimation(self, index, frame = 0):
        self.nowAnimationIndex = index
        self.nowFrame = frame
        self.changeImage(self.animations[self.nowAnimationIndex][self.nowFrame])

    #이미지 전환
    def changeImage(self, img):
        self.image = ImageTk.PhotoImage(img)
        Game.instance.canvas.itemconfig(self.me, image=self.image)

    #사망 애니메이션 재생 후 제거
    def kill(self, animation):
        if animation == None:
            self.destroy()
            return
        self.isdead = True
        self.addAnimation(animation)
        self.changeAnimation(len(self.animations) - 1)
    
    #이미지 불러오기
    def LoadImage(self, image, size):
        image = Image.open(image) #이미지
        image = image.resize(size, Image.Resampling.LANCZOS)
        image = image.rotate(0, expand=True)
        return image
    
    #이미지 뒤집기
    def flip(self):
        self.isLookRight = not self.isLookRight
        for x in range(len(self.animations)):
            for y in range(len(self.animations[x])):
                self.animations[x][y] = ImageOps.mirror(self.animations[x][y])

        self.changeImage(self.animations[self.nowAnimationIndex][self.nowFrame])

    #오브젝트 이동(절대)
    def goto(self, x, y):
        self.pos.setValue(x, y)
        Game.instance.canvas.coords(self.me, self.pos.x, self.pos.y)
    
    #오브젝트 이동(상대)
    def move(self, dx, dy):
        self.goto(self.pos.x + dx, 
                  self.pos.y + dy)
    
    #제거
    def destroy(self):
        Game.instance.canvas.delete(self.me)

#플레이어
class Player(AnimationObject):
    def __init__(self, keys):
        firstImage ="player/Boy_idle1.png"
        pos = (640, 360)
        size = (50, 50)
        animationSpeed = 0.1
        movespeed = 100
        super().__init__(firstImage, pos, size, movespeed, animationSpeed)

        self.setAnimation(0, [f"player/Boy_idle{i}.png"
          for i in [1,2,3,4,3,2]])
        self.addAnimation([f"player/Boy_walk{i}.png"
          for i in range(1,7)])
        
        self.keys = keys
        self.isMoving = False
    
    #키 입력
    def keyAction(self):
        left = 1 if (37 in self.keys or 65 in self.keys) else 0
        up = 1 if (38 in self.keys or 87 in self.keys) else 0
        right = 1 if (39 in self.keys or 68 in self.keys) else 0
        down = 1 if (40 in self.keys or 83 in self.keys) else 0

        self.moving(right - left, down - up)
        self.detectCollision()
        
    #플레이어 움직임
    def moving(self, dx, dy):
        if dx == 0 and dy == 0:
            self.vec.setValue(0, 0)
            if self.isMoving:
                self.changeAnimation(0)
                self.isMoving = False
        else:
            self.radian = math.atan2(dy, dx)
            self.vec.setValue(round(math.cos(self.radian) * self.moveSpeed, 2), round(math.sin(self.radian) * self.moveSpeed, 2))
            if not self.isMoving:
                self.changeAnimation(1)
                self.isMoving = True

            direction = self.radian * 180 / math.pi

            #움직이는 방향에 따른 좌우반전
            if self.isLookRight and (direction > 90 or direction < -90):
                self.flip()
            elif not self.isLookRight and (direction < 90 and direction > -90):
                self.isLookRight = self.isLookRight
                self.flip()

        self.move(self.vec.x * Game.instance.deltatime, self.vec.y * Game.instance.deltatime)

        #화면 밖으로 안나가게 제한
        if self.pos.x < self.size.x:
            self.pos.setValue(self.size.x, self.pos.y)
        if self.pos.x > Game.instance.screenWidth - self.size.x:
            self.pos.setValue(Game.instance.screenWidth - self.size.x, self.pos.y)
        if self.pos.y < self.size.y:
            self.pos.setValue(self.pos.x, self.size.y)
        if self.pos.y > Game.instance.screenHeight - self.size.y:
            self.pos.setValue(self.pos.x, Game.instance.screenHeight - self.size.y)
    #충돌 감지
    def detectCollision(self):
        for mob in Game.instance.enemys:
            if (Vector2._getDistance(self.pos, mob.pos) < (self.size.x + mob.size.x) / 4):
                self.isdead = True
                return


#상점
class Shop:
    def __init__(self, weapons, myfont, keys):
        #상점 배경 생성
        self.size = Vector2(176 * 2, 192 * 2)
        self.pos = Vector2(640, 360)
        self.weapons = weapons
        self.myfont = myfont
        self.keys = keys

        self.image = self.LoadImage("shop/Shop.png", self.size)
        self.image = ImageTk.PhotoImage(self.image)

        self.me = Game.instance.canvas.create_image(self.pos.x, self.pos.y, image=self.image)
        self.shopIconPoses = [Vector2(525, 245), 
                              Vector2(640, 245), 
                              Vector2(750, 245), 
                              Vector2(525, 415), 
                              Vector2(640, 415), 
                              Vector2(750, 415)]
        
        self.icons = [] #무기 아이콘
        self.texts = [] #레벨 텍스트
        self.buttons = [] #버튼
        self.prices = [] #가격

        self.createIcons()
        self.createText()
        self.createButtons()
        self.createPrice()
        Game.instance.window.bind("<Button-1>", self.onClick) #클릭 바인딩
        for i in range(1, 7): #1~6번 키 바인딩
            Game.instance.window.bind(f"<Key-{i}>", self.onKey)
        
    
    def LoadImage(self, image, size):
        image = Image.open(image) #이미지
        image = image.resize(size.getTuple(), Image.Resampling.LANCZOS)
        image = image.rotate(0)
        return image

    def close(self):
        #아이템 제거
        for icon in self.icons:
            Game.instance.canvas.delete(icon)
        for text in self.texts:
            Game.instance.canvas.delete(text)
        for button in self.buttons:
            Game.instance.canvas.delete(button.me)
        for price in self.prices:
            Game.instance.canvas.delete(price)

        self.icons = []
        self.texts = []
        self.buttons = []
        self.prices = []

        #상점 배경 제거
        Game.instance.canvas.delete(self.me)
        self.image = None
        self.me = None

        Game.instance.window.unbind("<Button-1>")
        for i in range(1, 7):
            Game.instance.window.unbind(f"<Key-{i}>")

    #아이콘 생성
    def createIcons(self):
        for i in range(6):
            icon = self.LoadImage(self.weapons[i].image, Vector2(70, 70)) 
            icon = ImageTk.PhotoImage(icon)
            Game.instance.canvas.create_image(self.shopIconPoses[i].x, self.shopIconPoses[i].y, image=icon)
            self.icons.append(icon)
    
    #텍스트 생성
    def createText(self):
        for i in range(6):
            text = Game.instance.canvas.create_text(
                self.shopIconPoses[i].x,
                self.shopIconPoses[i].y + 55,
                text=str(self.weapons[i].level) + "lv",
                fill="black",
                font=self.myfont
            )
            self.texts.append(text)

    #버튼 생성
    def createButtons(self):
        for i in range(6):
            button = ShopButton(self.shopIconPoses[i].x, self.shopIconPoses[i].y + 85, self.weapons[i])
            self.buttons.append(button)

    def createPrice(self):
        for i in range(6):
            price = Game.instance.canvas.create_text(
                self.shopIconPoses[i].x,
                self.shopIconPoses[i].y + 110,
                text=str(min(math.floor(Game.instance.money / self.weapons[i].price * 100), 100)) + "%",
                fill="black",
                font=(self.myfont, 10)
            )
            self.prices.append(price)

    def updatePrice(self):
        for i in range(6):
            Game.instance.canvas.itemconfig(self.prices[i], text=str(min(math.floor(Game.instance.money / self.weapons[i].price * 100), 100)) + "%")
    
    #클릭 감지
    def onClick(self, event):
        for btn in self.buttons:
            if btn.isClicked(event.x, event.y) and Game.instance.money >= btn.targetWeapon.price:
                btn.targetWeapon.levelup()
                self.updateLevel()
                self.updatePrice()
                return
    
    #키 입력 감지 및 처리 메서드 추가
    def onKey(self, event):
        try:
            # event.keysym은 '1', '2' 등의 문자열을 반환
            key_number = int(event.keysym)
        except ValueError:
            return

        if 1 <= key_number <= 6:
            button_index = key_number - 1 # 1번 키는 인덱스 0
            
            if button_index < len(self.buttons):
                btn = self.buttons[button_index]
                # 구매 조건 검사
                if Game.instance.money >= btn.targetWeapon.price:
                    btn.targetWeapon.levelup()
                    self.updateLevel()
                    self.updatePrice()
        

    #무기 레벨 갱신
    def updateLevel(self):
        Game.instance.sm.play_sfx("clickSound")
        for i in range(6):
            Game.instance.canvas.itemconfig(self.texts[i], text=str(self.weapons[i].level) + "lv")
#상점 버튼
class ShopButton:
    def __init__(self, x, y, targetWeapon):
        self.pos = Vector2(x, y)
        self.targetWeapon = targetWeapon
        self.size = Vector2(26 * 2, 14 * 2)

        self.image = self.LoadImage("shop/Button_BUY.png", self.size, 0)
        self.image = ImageTk.PhotoImage(self.image)
        self.me = Game.instance.canvas.create_image(self.pos.x, self.pos.y, image=self.image)
    
    def LoadImage(self, image, size, rotate):
        image = Image.open(image) #이미지
        image = image.resize(size.getTuple(), Image.Resampling.LANCZOS)
        image = image.rotate(rotate)
        return image
    
    #클릭 감지
    def isClicked(self, mx, my):
        halfW = self.size.x // 2
        halfH = self.size.y // 2
        return (self.pos.x - halfW <= mx <= self.pos.x + halfW and
                self.pos.y - halfH <= my <= self.pos.y + halfH)

#돈 표시 UI
class MoneyUI:
    def __init__(self, font):
        self.pos = Vector2(Game.instance.screenWidth - 10, 10)
        self.myfont = font
        self.me = Game.instance.canvas.create_text(
                self.pos.x,
                self.pos.y,
                text=str(Game.instance.money) + "GOLD",
                fill="black",
                font=self.myfont,
                anchor="ne"
            )
        self.nowShowingMoney = Game.instance.money
        self.moneyUpdateTime = 0.5
        self.deltaMoney = 0
    def addMoney(self, value):
        Game.instance.money += value
        self.deltaMoney = (Game.instance.money - self.nowShowingMoney)
    
    def updateData(self):
        temp = self.deltaMoney / self.moneyUpdateTime * Game.instance.deltatime
        if (abs(Game.instance.money - self.nowShowingMoney) < abs(temp)):
            self.nowShowingMoney = Game.instance.money
            self.deltaMoney = 0
        else:
            self.nowShowingMoney += temp
    

        Game.instance.canvas.itemconfig(self.me, text=str(math.floor(self.nowShowingMoney)) + " GOLD")
        Game.instance.canvas.coords(self.me, self.pos.x, self.pos.y)

class ScoreUI:
    def __init__(self, font):
        self.pos = Vector2(10, 10)
        self.myfont = font
        self.me = Game.instance.canvas.create_text(
                self.pos.x,
                self.pos.y,
                text="SCORE : " + str(Game.instance.killScore),
                fill="black",
                font=self.myfont,
                anchor="nw"
            )

    def updateData(self):
        Game.instance.canvas.itemconfig(self.me, text="SCORE : " + str(Game.instance.killScore),)
        Game.instance.canvas.coords(self.me, self.pos.x, self.pos.y)

    def addScore(self, value):
        Game.instance.killScore += value

#공격
class WeaponBasic:
    def __init__(self, image, level, sword):
        self.image = image
        self.level = level
        self.sword = sword #무기에 할당할 검

        self.priceDefault = 100
        self.price = self.priceDefault

        #기본스텟
        self.statsDefault = {}

        #배수가 적용된 스텟
        self.stats = {}

    #가격 상승
    def levelup(self):
        Game.instance.moneyUI.addMoney(-self.price)
        self.level += 1
        self.price = math.floor(self.priceDefault * (1.1 ** self.level))

    #프레임마다 실행
    def action(self):
        pass

    #기본 스텟에 있는 스텟들을 stats에 생성
    def setStatsDefault(self):
        for key, value in self.statsDefault.items():
            if isinstance(value, Vector2):
                #Vector2라면 새로운 객체를 생성하여 stats에 할당
                self.stats[key] = value.getSelf()
            else:
                #일반 값이라면 그대로 복사
                self.stats[key] = value

    #무기 정보 갱신용 함수. #상점 닫으면 1회씩 실행
    def updateData(self):
        pass

#지속성 무기
class WeaponContinue(WeaponBasic):
    def __init__(self, image, level, sword):
        super().__init__(image, level, sword)
        self.swordList = [] #무기 정보 갱신용 리스트
        self.nowSwordcount = 0 #현재 소환된 검 개수

        #상점을 닫으면 검 갯수 갱신
    def updateData(self):
        if self.level > 0:
            while(self.nowSwordcount < self.stats["count"]):#검 개수에 맞춰 소환
                newSword = self.sword(self.image, self.stats)

                Game.instance.swords.append(newSword)
                self.swordList.append(newSword)

                self.nowSwordcount += 1
 
#투사체
class SwordBasic:
    def __init__(self, image, stats):
        self.stats = stats

        self.angle = 0 #회전 방향
        self.radian = 0 #진행 방향
        self.pos = Vector2(Game.instance.player.pos.x, Game.instance.player.pos.y) #좌표
        self.vec = Vector2() #움직임 벡터

        self.originalImage = Image.open(image).convert("RGBA") #원본 이미지
        self.resizingImage = self.originalImage.resize((math.floor(self.stats["size"].x), math.floor(self.stats["size"].y)), Image.Resampling.LANCZOS) #원본 이미지에 크기를 반영한 이미지
        self.rotatingImage = self.resizingImage.rotate(-45, expand=True, fillcolor=(0, 0, 0, 0)) #크기 반영 이미지에 회전값을 반영한 이미지

        self.tkiamge = ImageTk.PhotoImage(self.rotatingImage)
        
        self.me = Game.instance.canvas.create_image(self.pos.x, self.pos.y, image=self.tkiamge)

        Game.instance.swords.append(self) #투사체 리스트에 추가

        self.AttackedMob = [] #다단히트 방지용 리스트

    def move(self, dx, dy):
        self.goto(self.pos.x + dx, self.pos.y + dy)
        
    def goto(self, x, y):
        self.pos.setValue(x, y)
        Game.instance.canvas.coords(self.me, self.pos.x, self.pos.y)
    
    def destroy(self):
        Game.instance.canvas.delete(self.me)
        if self in Game.instance.swords:
            Game.instance.swords.remove(self)

    #진행방향 변경
    def turn(self, radian):
        self.radian = (self.radian + radian + math.pi) % (2 * math.pi) - math.pi

    #이미지 회전
    def rotate(self, angle):
        self.angle = angle
        self.rotatingImage = self.resizingImage.rotate(-self.angle - 45, expand=True, fillcolor=(0, 0, 0, 0)) #원본 이미지가 45도 기울어져 있기에 보정
        self.tkiamge = ImageTk.PhotoImage(self.rotatingImage)

        Game.instance.canvas.itemconfig(self.me, image=self.tkiamge)

    #크기 변경
    def resize(self, x, y):
        self.resizingImage = self.originalImage.resize((math.floor(x), math.floor(y)), Image.Resampling.LANCZOS)
        self.rotatingImage = self.resizingImage.rotate(-self.angle - 45, expand=True, fillcolor=(0, 0, 0, 0))
        self.tkiamge = ImageTk.PhotoImage(self.rotatingImage)

        Game.instance.canvas.itemconfig(self.me, image=self.tkiamge)


    #타겟 몬스터 리스트 반환
    #기준 좌표 중심으로 범위 안의 몬스터를 sortType에 맞게 정렬해서 반환
    #만약 범위안에 아무것도 없다면 None 반환
    #0 = 검에서 가장 가까운 순서
    #1 = 플레이어에게서 가장 가까운 순서
    #2 = 가장 체력 비율이 낮은 순서
    #3 = 무작위 정렬
    def getTargetMonsterList(self, distance, sortType, getfirst):
        mobInDistance = []
        #사거리 내의 몬스터들 분류
        for mob in Game.instance.enemys:
            if (Vector2._getDistance(mob.pos, Game.instance.player.pos) < distance
                and not mob.isdead):
                mobInDistance.append(mob)

        #정렬 타입에 따라 정렬
        if len(mobInDistance) > 0:
            if sortType == 0: #검에서 가장 가까운 순서
                mobInDistance.sort(key=lambda mob: Vector2._getDistance(mob.pos, self.pos))
            if sortType == 1: #플레이어에게서 가장 가까운 순서
                mobInDistance.sort(key=lambda mob: Vector2._getDistance(mob.pos, Game.instance.player.pos))
            if sortType == 2: #가장 체력 비율이 낮은 순서
                mobInDistance.sort(key=lambda mob: mob.hp / mob.hpDafault)
            if sortType == 3: #무작위 정렬
                random.shuffle(mobInDistance)

            if getfirst:
                return mobInDistance[0] #getfirst가 true면 가장 앞 객체만 반환
            else:
                return mobInDistance
        else: 
            return None
        
    
    def AttackMob(self, damage, range):
        #피격 범위 안의 몬스터 공격, 공격한 적은 리스트에 담아 연속공격 방지, 이미 사망한 적 또한 제외
        for mob in Game.instance.enemys:
            if (Vector2._getDistance(self.pos, mob.pos) < range 
                and mob not in self.AttackedMob 
                and not mob.isdead):
                self.AttackedMob.append(mob)
                mob.hit(damage)
        
        #이미 공격했던 적들 중 피격 범위를 벗어난 대상 제거
        for mob in self.AttackedMob:
            if Vector2._getDistance(self.pos, mob.pos) > range:
                self.AttackedMob.remove(mob)

    #프레임마다 실행
    def action(self):
        pass

#가장 가까운 적에게 투척 공격
class Weapon1(WeaponBasic):
    def __init__(self, image, level, sword):
        super().__init__(image, level, sword)

        self.statsDefault.update({
            "size" : Vector2(30, 30),
            "atRange" : 500,
            "damage" : 5,
            "atSpeed" : 0.5,
            "count" : 2,
            "penetrate" : 1,
            "shootSpeed" : 300
        })
        
        self.setStatsDefault()

        self.tick = 0
        self.shootCount = 0
        self.shootTick = 0
        self.radian = 0
        
        self.target = None

    def action(self):
        if self.level > 0:
            self.tick += Game.instance.deltatime 
            if self.tick > 1 / self.stats["atSpeed"]:
                self.target = self.getTargetMob()
                if self.target != None:
                    self.radian = Vector2._getRadian(Game.instance.player.pos, self.target.pos)
                    self.shootCount += self.stats["count"]
                    self.tick = 0
            
            #발사 횟수만큼 연속 발사
            if self.shootCount > 0:
                self.shootTick += Game.instance.deltatime
                if self.shootTick > 1 / self.stats["atSpeed"] / 10:
                    Game.instance.swords.append(self.sword(self.image, self.stats, self.radian))
                    self.shootTick = 0
                    self.shootCount -= 1
        

    #무기에서 타겟을 정해서 투척하는 무기기에 따로 타겟을 구함
    def getTargetMob(self):
        mobInDistance = []
        #사거리 내의 몬스터들 분류
        for mob in Game.instance.enemys:
            if (Vector2._getDistance(mob.pos, Game.instance.player.pos) < self.stats["atRange"]
                and not mob.isdead):
                mobInDistance.append(mob)
        
        if len(mobInDistance) > 0:
            mobInDistance.sort(key=lambda mob: Vector2._getDistance(mob.pos, Game.instance.player.pos)) #가장 가까운 적 반환
            return mobInDistance[0]
        else:
            return None

        
    def levelup(self):
        super().levelup()
        self.stats.update({
            "damage" : self.statsDefault["damage"] * (1.05 ** self.level),
            "atSpeed" : self.statsDefault["atSpeed"] * (1.05 ** self.level),
            "count" : self.statsDefault["count"] + (self.level // 10),
            "penetrate" : self.statsDefault["penetrate"] + (self.level // 5)
        })

class Sword1(SwordBasic):
    def __init__(self, image, stats, radian): #방향을 정해서 날리기에 radian을 받아줌
        super().__init__(image, stats)
        #변경되면 안 되거나, 각 개체에서 따로 사용하는 변수들만 따로 저장
        self.damage = self.stats["damage"] #날아가는 칼은 데미지가 변경되면 안 됨
        self.moveSpeed = self.stats["shootSpeed"] #날아가는 칼은 속도가 바뀌면 안 됨
        self.penetrate = self.stats["penetrate"] #각 칼의 잔여 관통 횟수가 다 다름

        self.radian = radian
        
        self.vec = Vector2._getVectorFromRadian(self.radian, self.moveSpeed)
        self.rotate(self.radian * 180 / math.pi)

    def action(self):
        self.move(self.vec.x * Game.instance.deltatime, self.vec.y * Game.instance.deltatime)
        self.AttackMob(self.damage, self.stats["size"].x)
        #화면 밖으로 나가면 삭제
        if self.pos.x > Game.instance.screenWidth or self.pos.x < 0 or self.pos.y > Game.instance.screenHeight or self.pos.y < 0:
            self.destroy()
        
    def AttackMob(self, damage, range):
        #피격 범위 안의 몬스터 공격, 공격한 적은 리스트에 담아 연속공격 방지, 이미 사망한 적 또한 제외
        for mob in Game.instance.enemys:
            if (Vector2._getDistance(self.pos, mob.pos) < range 
                and mob not in self.AttackedMob 
                and not mob.isdead):
                self.AttackedMob.append(mob)
                mob.hit(damage)
                if self.penetrate > 0:
                    self.penetrate -= 1
                else:
                    self.destroy()
                    return
        
        #이미 공격했던 적들 중 피격 범위를 벗어난 대상 제거
        for mob in self.AttackedMob:
            if Vector2._getDistance(self.pos, mob.pos) > range:
                self.AttackedMob.remove(mob)

#제일 앞 검 기준으로 제일 가까운 적을 추적 공격, 그 뒤의 검들은 각각 앞의 검을 따라감
class Weapon2(WeaponContinue):
    def __init__(self, image, level, sword):
        super().__init__(image, level, sword)

        self.statsDefault.update({
            "size" : Vector2(30, 30),
            "damage" : 5,
            "atSpeed" : 100,
            "count" : 1,
            "atRange" : 900,
            "rotateSpeed" : 120
        })

        self.setStatsDefault()

    def levelup(self):
        super().levelup()
        self.stats.update({
            "damage" : self.statsDefault["damage"] * (1.05 ** self.level),
            "atSpeed" : self.statsDefault["atSpeed"] * (1.05 ** self.level),
            "count" : self.statsDefault["count"] + (self.level // 10),
            "rotateSpeed" : self.statsDefault["rotateSpeed"] * (1.05 ** self.level)
        })
    
    #검을 생성할 떄 추적 대상을 지정해줘야 하기에 따로 updateData함수 생성
    def updateData(self):
        if self.level > 0:
            while(self.nowSwordcount < self.stats["count"]):#검 개수에 맞춰 소환
                newSword = None
                if len(self.swordList) == 0:
                    newSword = self.sword(self.image, self.stats)
                else:
                    newSword = self.sword(self.image, self.stats, self.swordList[-1])

                Game.instance.swords.append(newSword)
                self.swordList.append(newSword)

                self.nowSwordcount += 1

class Sword2(SwordBasic):
    def __init__(self, image, stats, traceTarget = None):
        super().__init__(image, stats)
        self.traceTarget = traceTarget

        self.target = None

    def action(self):
        if self.traceTarget == None: #제일 앞 검은 적을 추적

            self.target = self.getTargetMonsterList(self.stats["atRange"], 0, True)
            if self.target != None:
                self.trace(self.target)
            else: #공격할 적이 없으면 제자리에서 회전
                self.RotatingInPlace()

        else: #그 뒤 검은 바로 앞 검을 추적
            if Vector2._getDistance(self.pos, self.traceTarget.pos) > self.stats["size"].x:
                self.trace(self.traceTarget)
            else: #앞의 칼이 너무 가까워지면 제자리에서 회전
                self.RotatingInPlace()
    #추적
    def trace(self, target):
        self.turn(self.getRotateRadianInSec(target))
        self.vec = Vector2._getVectorFromRadian(self.radian, self.stats["atSpeed"])
        self.move(self.vec.x * Game.instance.deltatime, self.vec.y * Game.instance.deltatime)
        self.AttackMob(self.stats["damage"], self.stats["size"].x)
        self.rotate(self.radian * 180 / math.pi)

    #제자리 회전
    def RotatingInPlace(self):
        self.turn(self.stats["rotateSpeed"] / 180 * math.pi * Game.instance.deltatime)
        self.rotate(self.radian * 180 / math.pi)

    #sin을 이용해서 초당 회전 각도 구하기
    def getRotateRadianInSec(self, target):
        target_radian = Vector2._getRadian(self.pos, target.pos)

        diff = (target_radian - self.radian + math.pi) % (2 * math.pi) - math.pi

        max_turn = self.stats["rotateSpeed"] / 180 * math.pi * Game.instance.deltatime

        # 회전 속도 제한
        if abs(diff) > max_turn:
            return math.copysign(max_turn, diff)
        else:
            return diff

#무작위 적을 지정, 지정된 적에게 가속하면서 날아감, 속도에 따른 데미지 증가
class Weapon3(WeaponContinue):
    def __init__(self, image, level, sword):
        super().__init__(image, level, sword)
        self.statsDefault.update({
            "size" : Vector2(30, 30),
            "damage" : 5,
            "atSpeed" : 2,
            "count" : 1,
            "atRange" : 900,
            "damageMagnification" : 1
        })

        self.setStatsDefault()
    
    def levelup(self):
        super().levelup()
        self.stats.update({
            "damageMagnification" : self.statsDefault["damageMagnification"] * (1 + self.level / 50),
            "damage" : self.statsDefault["damage"] * (1.05 ** self.level),
            "atSpeed" : self.statsDefault["atSpeed"] * (1.03 ** self.level) ,
            "count" : self.statsDefault["count"] + (self.level // 10)
        })

class Sword3(SwordBasic):
    def __init__(self, image, stats):
        super().__init__(image, stats)
        self.nowSpeed = 0 #현재 속력
        self.target = None

    def action(self):
        if self.target != None: #타겟이 없다면 제자리에서 대기하면서 계속 탐색
            #타겟을 추적 중 사라지거나 사망한 경우, 타겟 재탐색
            if (self.target not in Game.instance.enemys or self.target.isdead):
                self.target = self.getTargetMonsterList(self.stats["atRange"], 3, True)
            else:
                self.acceleration()
        else:
            self.radian = 0.5 * math.pi
            self.rotate(self.radian * 180 / math.pi)
            self.vec.setValue(0, 0)

            self.target = self.getTargetMonsterList(self.stats["atRange"], 3, True)
            

    #가속
    def acceleration(self):
        self.radian = Vector2._getRadian(self.pos, self.target.pos)
        self.accelVec = Vector2._getVectorFromRadian(self.radian, self.stats["atSpeed"])
        self.vec.add(self.accelVec)

        #계속 가속하면 안되기에 타겟과 일정 거리 이상 떨어져 있다면 감속
        if Vector2._getDistance(self.pos, self.target.pos) > self.stats["size"].x * 2:
            self.vec.multiple(0.99)

        self.nowSpeed = math.sqrt(self.vec.x ** 2 + self.vec.y ** 2)

        self.move(self.vec.x * Game.instance.deltatime, self.vec.y * Game.instance.deltatime)
        self.AttackMob(self.stats["damage"] * self.nowSpeed / 50 * self.stats["damageMagnification"], self.stats["size"].x)
        self.rotate(math.atan2(self.vec.y, self.vec.x) * 180 / math.pi)

#계속 움직이며 벽에 튕김
class Weapon4(WeaponContinue):
    def __init__(self, image, level, sword):
        super().__init__(image, level, sword)
        self.statsDefault.update({
            "damage" : 20,
            "atSpeed" : 200,
            "count" : 2,
            "size" : Vector2(30, 30)
        })

        self.setStatsDefault()

    def levelup(self):
        super().levelup()

        self.stats["size"].setValueToVec(self.statsDefault["size"].getMultiple(1.03 ** self.level))

        self.stats.update({
            "damage" : self.statsDefault["damage"] * (1.05 ** self.level),
            "atSpeed" : self.statsDefault["atSpeed"] * (1.05 ** self.level) ,
            "count" : self.statsDefault["count"] + (self.level // 5)
        })
    
    #무기 크기가 바뀌는 무기기에 따로 갱신해줌
    def updateData(self):
        super().updateData()
        for sword in self.swordList:
            sword.resize(self.stats["size"].x, self.stats["size"].y)
    
class Sword4(SwordBasic):
    def __init__(self, image, stats):
        super().__init__(image, stats)
        self.radian = random.randint(-180, 180) / 180 * math.pi #소환되면 무작위 방향으로 전진
        self.rotate(self.radian * 180 / math.pi)
        self.vec = Vector2._getVectorFromRadian(self.radian, self.stats["atSpeed"])
    
    def action(self):#반사를 제외하면 vec
        self.move(self.vec.x * Game.instance.deltatime, self.vec.y * Game.instance.deltatime)
        self.reflect()
        self.AttackMob(self.stats["damage"], self.stats["size"].x)
    
    #튕기기
    def reflect(self): #한쪽 벽에 껴버리는것을 방지하기 위해 각 벽마다 조건을 따로 세움
        if ((self.pos.x < self.stats["size"].x and (self.radian > 0.5 * math.pi or self.radian < -0.5 * math.pi)) or
            (self.pos.x > Game.instance.screenWidth - self.stats["size"].x and (self.radian < 0.5 * math.pi and self.radian > -0.5 * math.pi))): 
            self.radian = (math.pi * 2 - self.radian) % (2 * math.pi) - math.pi
        
        if ((self.pos.y < self.stats["size"].y and (self.radian > -math.pi and self.radian < 0)) or 
            (self.pos.y > Game.instance.screenHeight - self.stats["size"].y and (self.radian < math.pi and self.radian > 0))):
            self.radian = -self.radian
            

        self.vec = Vector2._getVectorFromRadian(self.radian, self.stats["atSpeed"])
        self.rotate(self.radian * 180 / math.pi)

#플레이어 주변을 공전
class Weapon5(WeaponContinue):
    def __init__(self, image, level, sword):
        super().__init__(image, level, sword)
        self.statsDefault.update({
            "damage" : 5,
            "atSpeed" : 90 / 180 * math.pi,
            "count" : 2,
            "atRange" : 70,
            "size" : Vector2(60, 60)
        })

        self.setStatsDefault()

        self.hostRadian = 0 #회전 기준
    
    def levelup(self):
        super().levelup()

        self.stats["size"].setValueToVec(self.statsDefault["size"].getMultiple(1.03 ** self.level))

        self.stats.update({
            "damage" : self.statsDefault["damage"] * (1.05 ** self.level),
            "atSpeed" : self.statsDefault["atSpeed"] * (1.05 ** self.level),
            "count" : self.statsDefault["count"] + (self.level // 5),
            "atRange" : self.statsDefault["atRange"] * (1.03 ** self.level),
        })

    def updateData(self):
        super().updateData()
        for sword in self.swordList:
            sword.resize(self.stats["size"].x, self.stats["size"].y)

    def action(self):
        self.hostRadian += self.stats["atSpeed"] * Game.instance.deltatime
        self.hostRadian %= 2 * math.pi

        for i in range(len(self.swordList)):
            self.setSwordState(self.swordList[i], i)
    
    #입력된 인덱스에 따라 검의 방향과 위치를 설정
    def setSwordState(self, sword, index):
        resultRadian = self.hostRadian + (2 * math.pi / len(self.swordList) * index)
        resultRadian %= 2 * math.pi

        sword.rotate(resultRadian * 180 / math.pi)

        resultpos = Vector2._getSum(Game.instance.player.pos, Vector2._getVectorFromRadian(resultRadian, self.stats["atRange"]))

        sword.goto(resultpos.x, resultpos.y)
    
class Sword5(SwordBasic):
    def __init__(self, image, stats):
        super().__init__(image, stats)

    def action(self):
        self.AttackMob(self.stats["damage"], self.stats["size"].x)
    
#가장 체력이 적은 적한테 투척, 적을 죽이고 나서 남은 데미지는 다음으로 체력이 적은 적한테 이월
#투척형 무기기에 Weapon1을 상속
class Weapon6(Weapon1):
    def __init__(self, image, level, sword):
        super().__init__(image, level, sword)

        self.statsDefault.update({
            "size" : Vector2(30, 30),
            "atRange" : 600,
            "damage" : 30,
            "atSpeed" : 0.3,
            "count" : 1,
            "shootSpeed" : 400,
            "rotateSpeed" : 360
        })
        
        self.radian = 0

        self.setStatsDefault()
    
    def levelup(self):
        super().levelup()

        self.stats.update({
            "damage" : self.statsDefault["damage"] * (1.07 ** self.level),
            "atSpeed" : self.statsDefault["atSpeed"] * (1.05 ** self.level),
            "shootSpeed" : self.statsDefault["shootSpeed"] * (1.03 ** self.level),
        })

    def getTargetMob(self):
        mobInDistance = []
        #사거리 내의 몬스터들 분류
        for mob in Game.instance.enemys:
            if (Vector2._getDistance(mob.pos, Game.instance.player.pos) < self.stats["atRange"]
                and not mob.isdead):
                mobInDistance.append(mob)
        
        if len(mobInDistance) > 0:
            mobInDistance.sort(key=lambda mob: mob.hp / mob.hpDafault) #가장 체력이 적은 적 반환
            return mobInDistance[0]
        else:
            return None

class Sword6(Sword2): #추적 방식이나 등등이 Sword2와 비슷하기에 Sword2를 상속
    def __init__(self, image, stats, radian): #방향을 정해서 날리기에 radian을 받아줌
        super().__init__(image, stats)
        self.radian = radian #초기 방향
        self.vec = Vector2._getVectorFromRadian(self.radian, self.stats["shootSpeed"])
        self.rotate(self.radian * 180 / math.pi)
        self.lastDamage = self.stats["damage"] #남은 데미지

    def action(self):
        if self.target != None:
            self.trace(self.target)
            if self.target.isdead:
                self.target = self.getTargetMonsterList(self.stats["atRange"], 2, True)
        else: #공격할 적이 없으면 직진
            self.move(self.vec.x * Game.instance.deltatime, self.vec.y * Game.instance.deltatime)
            self.AttackMob()
            self.target = self.getTargetMonsterList(self.stats["atRange"], 2, True)
            if self.pos.x > Game.instance.screenWidth or self.pos.x < 0 or self.pos.y > Game.instance.screenHeight or self.pos.y < 0: #화면 밖으로 나가면 삭제
                self.destroy()
            
        
    def trace(self, target):
        self.turn(self.getRotateRadianInSec(target))
        self.vec = Vector2._getVectorFromRadian(self.radian, self.stats["shootSpeed"])
        self.move(self.vec.x * Game.instance.deltatime, self.vec.y * Game.instance.deltatime)
        self.AttackMob()
        self.rotate(self.radian * 180 / math.pi)

    #혼자 최대데미지를 제한하는 계산식을 쓰기에 따로 계산
    def AttackMob(self): 
        for mob in Game.instance.enemys:
            if (Vector2._getDistance(self.pos, mob.pos) < self.stats["size"].x
                and mob not in self.AttackedMob 
                and not mob.isdead):
                self.AttackedMob.append(mob)

                hitdamage = min(self.lastDamage, mob.hp) #타격데미지. 적의 최대 HP 이상으로 데미지를 입히지 않음
                mob.hit(hitdamage)
                self.lastDamage -= hitdamage

                if self.lastDamage <= 0: #잔여 데미지가 0 이하일 경우 제거
                    self.destroy()
        
        for mob in self.AttackedMob:
            if Vector2._getDistance(self.pos, mob.pos) > self.stats["size"].x:
                self.AttackedMob.remove(mob)

#적 소환
class SummonManager:
    def __init__(self):
        self.moblist = [Mob1, Mob2, Mob3]
        self.mobMagnification = 0 #몬스터 배율
        self.deltaMagnification = 1 #몬스터 배율 변화량
        self.mobReinfoceTime = 30 #몬스터 배율 변화 시간
        self.mobReinfoceTick = 0
        self.mobSummonLen = 100

    def updateSummonTick(self):
        for mob in self.moblist:
            mob.summonTick += Game.instance.deltatime
            if mob.summonTick > mob.summonTime:
                for _ in range(math.floor(mob.summonCount * (1 + self.mobMagnification / 10))):
                    Game.instance.enemys.append(mob(self.randomOutOfWindow(), self.mobMagnification))
                mob.summonTick = 0

        self.mobReinfoceTick += Game.instance.deltatime
        if self.mobReinfoceTick > self.mobReinfoceTime:
            self.mobReinfoceTick = 0
            self.mobMagnification += self.deltaMagnification

     #무작위 화면 밖 좌표 반환
    def randomOutOfWindow(self):
        directrion = random.randint(0, 3) #상하좌우 어느 방향에서 나올 것인가?
        if directrion == 0: #위
            return (random.randint(-self.mobSummonLen, Game.instance.screenWidth + self.mobSummonLen), -self.mobSummonLen)
        elif directrion == 1: #아래
            return (random.randint(-self.mobSummonLen, Game.instance.screenWidth + self.mobSummonLen), Game.instance.screenHeight + self.mobSummonLen)
        elif directrion == 2: #좌
            return (-self.mobSummonLen, random.randint(-self.mobSummonLen, Game.instance.screenHeight + self.mobSummonLen))
        elif directrion == 3: #우
            return (Game.instance.screenWidth + self.mobSummonLen, random.randint(-self.mobSummonLen, Game.instance.screenHeight + self.mobSummonLen))
        
    def reset(self):
        self.mobMagnification = 1 #몬스터 배율
        self.deltaMagnification = 1 #몬스터 배율 변화량
        self.mobReinfoceTime = 50 #몬스터 배율 변화 시간
        self.mobReinfoceTick = 0
        for mob in self.moblist:
            mob.summonTick = 0

#적
class MobBasic(AnimationObject):
    def __init__(self, firstImage, pos, size, hp, moveSpeed, animationspeed, gold, score):
        self.lookDirection = 0 #보고있는 방향 0~3 각각 아래, 위, 왼쪽, 오른쪽
        super().__init__(firstImage, pos, size, moveSpeed, animationspeed)
        self.hpDafault = hp
        self.hp = hp
        
        self.deathMoney = gold
        self.deathScore = score

    def action(self):
        if not self.isdead:
            #플레이어를 향해 이동
            self.radian = self._getRadianToPlayer()
            self.vec.setValue(math.cos(self.radian) * self.moveSpeed, math.sin(self.radian) * self.moveSpeed )
            self.move(self.vec.x * Game.instance.deltatime, self.vec.y * Game.instance.deltatime)

            #이동 방향에 따라 애니메이션 변경
            self.lookDirection = self.getLookDirection()
            self.changeAnimation(self.lookDirection, self.nowFrame)

        self.nextFrame()

    #피격
    def hit(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            deathAnimation = self.getDeathAnimation()
            Game.instance.moneyUI.addMoney(self.deathMoney)
            Game.instance.scoreUI.addScore(self.deathScore)
            Game.instance.sm.play_sfx("slimeDeath")
            self.kill(deathAnimation)
        else:
            Game.instance.sm.play_sfx("swordSlash")

    def getDeathAnimation(self):
        return None

    #플레이어를 향하는 방향 구하기
    def _getRadianToPlayer(self):
        return math.atan2(Game.instance.player.pos.y - self.pos.y, Game.instance.player.pos.x - self.pos.x)

    #바라보고 있는 방향 구하기
    def getLookDirection(self):
        direction = self.radian * 180 / math.pi
        #Y좌표축은 반대이기에 위 아래 애니메이션을 보이는 것과 반대로 재생
        if (direction >= 45 and direction < 135):
            return 0
        elif (direction >= -135 and direction < -45):
            return 1
        elif (direction >= 135 and direction <= 180) or (direction >= -180 and direction < -135):
            return 2
        elif (direction >= -45 and direction < 45):
            return 3
        
    def destroy(self):
        super().destroy()
        Game.instance.enemys.remove(self)
#기본 적
class Mob1(MobBasic):
    walkAnimation_up = [f"mobs/slime1/walk/{i}.png" for i in range(9, 17)]
    walkAnimation_down = [f"mobs/slime1/walk/{i}.png" for i in range(1,9)]
    walkAnimation_left = [f"mobs/slime1/walk/{i}.png" for i in range(17, 25)]
    walkAnimation_right = [f"mobs/slime1/walk/{i}.png" for i in range(25, 33)]
    
    summonTime = 5
    summonCount = 2

    summonTick = 0

    def __init__(self, pos, mag):
        size = (100, 100)
        moveSpeed = 50 + mag
        animationSpeed = 0.1
        hp = 10 * (1 + mag / 5)
        gold = 7
        score = 5
        super().__init__("mobs/slime1/walk/9.png", pos, size, hp, moveSpeed, animationSpeed, gold, score)
        #애니메이션 지정
        self.setAnimation(0, Mob1.walkAnimation_down) #이동_아래
        self.addAnimation(Mob1.walkAnimation_up) #이동_위
        self.addAnimation(Mob1.walkAnimation_left) #이동_왼쪽
        self.addAnimation(Mob1.walkAnimation_right) #이동_오른쪽

    def getDeathAnimation(self):
        return [f"mobs/slime1/death/{self.lookDirection * 10 + i + 1}.png" for i in range(10)]
#빠른 적
class Mob2(MobBasic):
    walkAnimation_up = [f"mobs/slime2/walk/{i}.png" for i in range(9, 17)]
    walkAnimation_down = [f"mobs/slime2/walk/{i}.png" for i in range(1,9)]
    walkAnimation_left = [f"mobs/slime2/walk/{i}.png" for i in range(17, 25)]
    walkAnimation_right = [f"mobs/slime2/walk/{i}.png" for i in range(25, 33)]
    
    summonTime = 13
    summonCount = 5

    summonTick = 0

    def __init__(self, pos, mag):
        size = (90, 90)
        moveSpeed = 70 + mag * 2
        animationSpeed = 0.1
        hp = 7 * (1 + mag / 7)
        gold = 5
        score = 3
        super().__init__("mobs/slime2/walk/9.png", pos, size, hp, moveSpeed, animationSpeed, gold, score)
        #애니메이션 지정
        self.setAnimation(0, Mob2.walkAnimation_down) #이동_아래
        self.addAnimation(Mob2.walkAnimation_up) #이동_위
        self.addAnimation(Mob2.walkAnimation_left) #이동_왼쪽
        self.addAnimation(Mob2.walkAnimation_right) #이동_오른쪽

    def getDeathAnimation(self):
        return [f"mobs/slime2/death/{self.lookDirection * 10 + i + 1}.png" for i in range(10)]
#튼튼한 적
class Mob3(MobBasic):
    walkAnimation_up = [f"mobs/slime3/walk/{i}.png" for i in range(9, 17)]
    walkAnimation_down = [f"mobs/slime3/walk/{i}.png" for i in range(1,9)]
    walkAnimation_left = [f"mobs/slime3/walk/{i}.png" for i in range(17, 25)]
    walkAnimation_right = [f"mobs/slime3/walk/{i}.png" for i in range(25, 33)]
    
    summonTime = 10
    summonCount = 1

    summonTick = 0

    def __init__(self, pos, mag):
        size = (150, 150)
        moveSpeed = 30 + (mag // 2)
        animationSpeed = 0.1
        hp = 30 * (1 + mag / 3)
        gold = 10
        score = 7
        super().__init__("mobs/slime3/walk/9.png", pos, size, hp, moveSpeed, animationSpeed, gold, score)
        #애니메이션 지정
        self.setAnimation(0, Mob3.walkAnimation_down) #이동_아래
        self.addAnimation(Mob3.walkAnimation_up) #이동_위
        self.addAnimation(Mob3.walkAnimation_left) #이동_왼쪽
        self.addAnimation(Mob3.walkAnimation_right) #이동_오른쪽

    def getDeathAnimation(self):
        return [f"mobs/slime3/death/{self.lookDirection * 10 + i + 1}.png" for i in range(10)]

#배경
class Backgournd():
    def __init__(self):
        self.width = Game.instance.screenWidth
        self.height = Game.instance.screenHeight
        self.tileSize = Vector2(64, 72)
        self.tilePlace = [[None for _ in range(self.width // self.tileSize.x)] for _ in range(self.height // self.tileSize.y)] #생성된 타일이나 환경오브젝트가 들어갈 리스트
        self.placedObjects = []

        #사용할 소스들
        self.tiles = {
            "outline" : "backgroud/tiles/FieldsTile_grass.png",
            "middle" : [f"backgroud/tiles/FieldsTile_middle ({i + 1}).png" for i in range(3)],
            #경계선타일
            "left" : [f"backgroud/tiles/FieldsTile_left ({i + 1}).png" for i in range(3)],
            "right" : [f"backgroud/tiles/FieldsTile_right ({i + 1}).png" for i in range(3)],
            "up" : [f"backgroud/tiles/FieldsTile_up ({i + 1}).png" for i in range(3)],
            "down" : [f"backgroud/tiles/FieldsTile_down ({i + 1}).png" for i in range(3)],
            #모서리타일
            "LD" : "backgroud/tiles/FieldsTile_LD.png",
            "RD" : "backgroud/tiles/FieldsTile_RD.png",
            "LU" : "backgroud/tiles/FieldsTile_LU.png",
            "RU" : "backgroud/tiles/FieldsTile_RU.png",
        }


        self.objects = {
            "stone" : [f"backgroud/stones/{i + 1}.png" for i in range(6)],
            "grass" : [f"backgroud/grasses/{i + 1}.png" for i in range(6)],
            "flower" : [f"backgroud/flowers/{i + 1}.png" for i in range(12)],
            "bush" : [f"backgroud/bushs/{i + 1}.png" for i in range(6)]
        }

        self.objectNum = {
            "stone" : 10,
            "grass" : 70,
            "flower" : 20,
            "bush" : 3
        }


        self.objectSizeMag = 2 #오브젝트 크기 배율


        

        self.imageReference = []

        self.buildTiles()
        self.buildObjects()

    #타일 배치
    def buildTiles(self):
        for i in range(len(self.tilePlace)):
            for j in range(len(self.tilePlace[0])):
                if (i == 0 or i == len(self.tilePlace) - 1 or j == 0 or j == len(self.tilePlace[0]) - 1): #제일 가장자리는 잔디 타일
                    self.placeTile(self.tiles["outline"], self.tileSize, (j, i))

                elif (i == 1): #가장자리와 중간의 경계선은 방향마다 다른 타일 배치
                    if (j == 1):
                        self.placeTile(self.tiles["LU"], self.tileSize, (j, i)) #모서리 타일 배치
                    elif (j == len(self.tilePlace[0]) - 2):
                        self.placeTile(self.tiles["RU"], self.tileSize, (j, i))
                    else:
                        self.placeTile(random.choice(self.tiles["up"]), self.tileSize, (j, i))

                elif (i == len(self.tilePlace) - 2):
                    if (j == 1):
                        self.placeTile(self.tiles["LD"], self.tileSize, (j, i))
                    elif (j == len(self.tilePlace[0]) - 2):
                        self.placeTile(self.tiles["RD"], self.tileSize, (j, i))
                    else:
                        self.placeTile(random.choice(self.tiles["down"]), self.tileSize, (j, i))

                elif (j == 1):
                    if (i == 1):
                        self.placeTile(self.tiles["LU"], self.tileSize, (j, i))
                    elif (i == len(self.tilePlace) - 2):
                        self.placeTile(self.tiles["LD"], self.tileSize, (j, i))
                    else:
                        self.placeTile(random.choice(self.tiles["left"]), self.tileSize, (j, i))

                elif (j == len(self.tilePlace[0]) - 2):
                    if (i == 1):
                        self.placeTile(self.tiles["RU"], self.tileSize, (j, i))
                    elif (i == len(self.tilePlace) - 2):
                        self.placeTile(self.tiles["RD"], self.tileSize, (j, i))
                    else:
                        self.placeTile(random.choice(self.tiles["right"]), self.tileSize, (j, i))
                
                else:
                    self.placeTile(random.choice(self.tiles["middle"]), self.tileSize, (j, i))
    
    #오브젝트 배치
    def buildObjects(self):
        for key in self.objects.keys():
            for _ in range(self.objectNum[key]):
                self.placeObject(random.choice(self.objects[key]), self.objectSizeMag)

    #타일 설치
    def placeTile(self, image, size, cell):
        if (self.tilePlace[cell[1]][cell[0]] == None):
            img = Image.open(image) #이미지
            img = img.resize(size.getTuple(), Image.Resampling.LANCZOS)
            img = img.rotate(0, expand=True)
            img = ImageTk.PhotoImage(img)

            self.imageReference.append(img)

            self.tilePlace[cell[1]][cell[0]] = Game.instance.canvas.create_image((cell[0] + 0.5) * self.tileSize.x, (cell[1] + 0.5) * self.tileSize.y, image=img)

    #오브젝트 설치
    def placeObject(self, image, sizeMag):
        img = Image.open(image) #이미지
        img = img.resize((img.size[0] * sizeMag, img.size[1] * sizeMag), Image.Resampling.LANCZOS)
        img = img.rotate(0, expand=True)
        tkimg = ImageTk.PhotoImage(img)

        self.imageReference.append(tkimg)

        pos = Vector2(random.randint(0, self.width),
                      random.randint(0, self.height))

        self.placedObjects.append(Game.instance.canvas.create_image(pos.x - (img.size[0] / 2), pos.y - (img.size[1] / 2), image=tkimg))


    def destroy(self):
        for x in self.list:
            Game.instance.canvas.delete(x)
        self.imageReference = []

#루프
class Game:
    instance = None

    def __init__(self):
        Game.instance = self
        #게임 진행 상태
        #0 = 게임 시작
        #1 = 게임 진행
        #2 = 게임 오버
        self.gameState = 0 

        self.screenWidth = 1280
        self.screenHeight = 720

        self.window = Tk()
        self.window.geometry(f"{self.screenWidth}x{self.screenHeight}")
        self.window.title("game")
        self.window.protocol("WM_DELETE_WINDOW", self.onClose)

        self.nowtime = time.time()
        self.lastTime = self.nowtime

        self.money = 0
        self.killScore = 0
        self.enemys = []
        self.swords = []

        #폰트
        self.myfont = font.Font(family="Times", size=24)

        #키바인드 설정
        self.keys = set()
        self.window.bind("<KeyPress>", self.KeyPressHandler)
        self.window.bind("<KeyRelease>", self.KeyReleaseHandler)
 
        #캔버스 생성
        self.canvas = Canvas(self.window, bg="white")
        self.canvas.pack(expand=True, fill='both')

        #플레이어 생성
        self.player = Player(self.keys)

        #UI 생성
        self.scoreUI = ScoreUI(self.myfont)
        self.moneyUI = MoneyUI(self.myfont)

        #사운드매니저 생성
        self.sm = SoundManager()

        self.sm.load_music("sounds/bgm.wav", 0.2)
        self.sm.load_sfx("slimeDeath", "sounds/slimeDeathSound.wav", 0.05)
        self.sm.load_sfx("swordSlash", "sounds/swordSlashSound.wav", 0.05)
        self.sm.load_sfx("clickSound", "sounds/clickSound.wav", 0.3)

        #무기 생성
        self.weapons = [
            Weapon1("weapons/weapon1.png", 0, Sword1),
            Weapon2("weapons/weapon2.png", 0, Sword2),
            Weapon3("weapons/weapon3.png", 0, Sword3),
            Weapon4("weapons/weapon4.png", 0, Sword4),
            Weapon5("weapons/weapon5.png", 0, Sword5),
            Weapon6("weapons/weapon6.png", 0, Sword6)
            ]
        
        #몹 소환 매니저 생성
        self.summonManger = SummonManager()

        self.shop = None 
        self.isShoping = False #게임루프 일시정지용 변수
        
        self.showStartScreen()

        self.update()
        self.window.mainloop()

    #루프
    def update(self):
        self.getDeltaTime()
        self.moneyUI.updateData()
        self.scoreUI.updateData()

        if self.gameState == 1:
            if not self.isShoping:
                self.player.keyAction()
                self.player.nextFrame()

                #적 소환
                self.summonManger.updateSummonTick()

                #적들 움직임
                for mob in self.enemys:
                    mob.action()
                #무기 공격
                for weapon in self.weapons:
                    weapon.action()
                #투사체 움직임
                for sword in self.swords:
                    sword.action()

            if self.player.isdead:
                Game.instance.setGameOver()

        self.window.after(16, self.update)
    
    #게임 시작
    def startGame(self):
        # 이전 화면 숨기기 (시작 화면 또는 게임 오버 화면)
        self.hideStartScreen()
        self.hideGameOverScreen()
        
        # 게임 상태 변경
        self.gameState = 1
        
        # 게임 데이터 초기화
        self.money = 200
        self.killScore = 0
        self.enemys = []
        self.swords = []
        
        # 캔버스 초기화
        self.canvas.delete("all")
        
        # 배경화면 생성
        self.background = Backgournd()

        # 플레이어 재설정
        self.player = Player(self.keys)

        self.scoreUI = ScoreUI(self.myfont)
        self.moneyUI = MoneyUI(self.myfont)


        self.summonManger.reset()
        
        # 무기 레벨/데이터 초기화
        self.weapons = [
            Weapon1("weapons/weapon1.png", 0, Sword1),
            Weapon2("weapons/weapon2.png", 0, Sword2),
            Weapon3("weapons/weapon3.png", 0, Sword3),
            Weapon4("weapons/weapon4.png", 0, Sword4),
            Weapon5("weapons/weapon5.png", 0, Sword5),
            Weapon6("weapons/weapon6.png", 0, Sword6)
            ]
        
        # 사운드 재생
        self.sm.play_music()
    
    #게임오버
    def setGameOver(self):
        # 이미 게임 오버 상태라면 중복 실행 방지
        if self.gameState == 2:
            return
            
        # 게임 상태 변경
        self.gameState = 2
        self.isShoping = False # 상점 강제 닫기

        # 모든 적, 투사체 제거
        for mob in self.enemys:
            self.canvas.delete(mob.me)
        for sword in self.swords:
            self.canvas.delete(sword.me)
        self.enemys = []
        self.swords = []

        # 플레이어 제거
        self.canvas.delete(self.player.me)
        self.player = None
        
        # 배경 음악 중지
        self.sm.stop_music()
        
        # 게임 오버 화면 표시
        self.showGameOverScreen()

    #게임 시작 화면 띄우기
    def showStartScreen(self):
        # 캔버스 초기화
        self.canvas.delete("all")

        # 시작 화면 텍스트 생성 및 저장
        self.startText = self.canvas.create_text(
            self.screenWidth // 2, 
            self.screenHeight // 2, 
            text="START GAME (Press Space)", 
            fill="black", 
            font=self.myfont
        )

    #게임 시작 화면 숨기기
    def hideStartScreen(self):
        # 시작 화면 텍스트 제거
        if hasattr(self, 'startText') and self.startText:
            self.canvas.delete(self.startText)
            self.startText = None

    #게임 오버 화면 띄우기
    def showGameOverScreen(self):
        # 게임 오버 텍스트 생성 및 저장
        self.gameOverText = self.canvas.create_text(
            self.screenWidth // 2, 
            self.screenHeight // 2, 
            text=f"GAME OVER\nScore : {self.killScore}\nPress Space to Restart", 
            fill="black", 
            font=self.myfont,
            justify='center'
        )

    #게임 오버 화면 숨기기
    def hideGameOverScreen(self):
        # 게임 오버 화면 텍스트 제거
        if hasattr(self, 'gameOverText') and self.gameOverText:
            self.canvas.delete(self.gameOverText)
            self.gameOverText = None

    #deltatime 구하기
    def getDeltaTime(self):
        self.nowtime = time.time()
        self.deltatime = self.nowtime - self.lastTime
        self.lastTime = self.nowtime

    #키 입력
    def KeyPressHandler(self, event):
        self.keys.add(event.keycode)
        
        # 어느 화면에서든 ESC 키 입력시 게임 종료
        if 27 in self.keys:
            self.onClose()

        if self.gameState == 0:
            #스페이스바 눌렸을 때 게임 시작
            if 32 in self.keys:
                self.startGame()
                self.sm.play_sfx("clickSound")
        
        elif self.gameState == 1:
            if 32 in self.keys: #스페이스바 입력 시 상점 열기/닫기
                if self.isShoping:
                    self.closeShop()
                    self.isShoping = False
                else:
                    self.openShop()
                    self.isShoping = True
        
        # 게임 오버 상태에서 재시작 (Spacebar: 32)
        elif self.gameState == 2:
            #스페이스바 눌렸을 때 시작 화면으로 전환 
            if 32 in self.keys:
                self.gameState = 0
                self.hideGameOverScreen()
                self.showStartScreen()
                self.sm.play_sfx("clickSound")

        


    #키 해제
    def KeyReleaseHandler(self, event):
        if event.keycode in self.keys:
            self.keys.remove(event.keycode)

    def openShop(self):
        self.shop = Shop(self.weapons, self.myfont, self.keys)
    
    def closeShop(self):
        if self.shop != None:
            self.shop.close()
        for weapon in self.weapons:
            weapon.updateData()

    def onClose(self):
        self.sm.quit()
        self.window.destroy()
        


Game()