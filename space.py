import pygame
import os
import time
import random
import playsound
from pygame import mixer
pygame.font.init()
pygame.mixer.init()
import time


WIDTH,HEIGHT = 750,750
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Space Shooter @Advait")

# Loading SPACE_SHIP Images

RED_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_blue_small.png"))
WHITE_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_white_small.png"))
GREY_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_grey_small.png"))

YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_yellow.png"))

# Loading LASER Images
RED_LASER = pygame.image.load(os.path.join("assets","pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets","pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets","pixel_laser_blue.png"))
WHITE_LASER = pygame.image.load(os.path.join("assets","pixel_laser_white.png"))
GREY_LASER = pygame.image.load(os.path.join("assets","pixel_laser_grey.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets","pixel_laser_yellow.png"))

# Loading the BACKGROUND
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets","background-black.png")),(WIDTH,HEIGHT))


# Loading LIFE image
LIFE = pygame.image.load(os.path.join("assets","heart.png"))

# Loading ICON image
ICON = pygame.image.load(os.path.join("assets","icon.png"))
pygame.display.set_icon(ICON)

kills  = 0

class Lives:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.img = LIFE
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self,window):
        window.blit(self.img,(self.x,self.y)) 
    
    def move(self,vel):
        self.y += vel

    def off_screen(self,height):
        return not(self.y <= height and self.y >=0) 

    def collision(self,obj):
        return collide(self,obj)              

class Laser:
    def __init__(self,x,y,img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self,window):
        window.blit(self.img,(self.x,self.y))

    def move(self,vel):
        self.y += vel

    def off_screen(self,height):
        return not(self.y <= height and self.y >=0)                

    def collision(self,obj):
        return collide(self,obj)


class Ship:
    COOLDOWN = 30
    def __init__(self,x,y,health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0 

    def draw(self,window):
        #pygame.draw.rect(window,(255,0,0),(self.x,self.y,50,50),0)
        window.blit(self.ship_img,(self.x,self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self,vel,obj):
        self.cooldown()

        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser) 

            elif laser.collision(obj):
                playsound.playsound("Soundtracks/got_hit.mp3",False)
                obj.health -=10 
                self.lasers.remove(laser)         

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter>0:
            self.cool_down_counter +=1


    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()  

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x,y,health)

        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self,vel,objs):
        self.cooldown()

        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser) 

            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        global kills
                        kills += 1
                        playsound.playsound("Soundtracks/enemy_died.mp3",False)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self,window):
        super().draw(window)
        self.healthbar(window)



    def healthbar(self,window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER),
                "white": (WHITE_SPACE_SHIP, WHITE_LASER),
                "grey": (GREY_SPACE_SHIP, GREY_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            


def collide(obj1,obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y 
    return obj1.mask.overlap(obj2.mask,(offset_x,offset_y)) != None





def main():
    time.sleep(1.5)
    run = True
    FPS = 60
    level = 0
    lives = 5
    global kills
    main_font = pygame.font.SysFont("comicsans",50)
    lost_font = pygame.font.SysFont("comicsans",80)
    enemies = []   # Stores all the enemies in this list
    wave_length = 5 
    enemy_vel = 1
    laser_vel = 6
    

    lost = False
    lost_count = 0
    critical_flag = 1

    health_kit = []
    no_of_health_kit = 1
    health_kit_vel = 1

    #playsound.playsound("BGM.mp3",False)
    mixer.music.load("Soundtracks/BGM.mp3")
    mixer.music.play(-1)
    mixer.music.set_volume(0.3)


    player_vel = 5
    player = Player(300,630)

    clock = pygame.time.Clock()

    def redraw_window():
        WIN.blit(BG,(0,0))

        # draw text 
        lives_lable = main_font.render(f"Lives : {lives}",1,(255,255,255))
        level_lable = main_font.render(f"Level : {level}",1,(255,255,255))
        kill_lable = main_font.render(f"Kills : {kills}",1,(255,0,0))

        

        WIN.blit(lives_lable,(10,10))
        WIN.blit(kill_lable,(WIDTH - kill_lable.get_width() + 20 - WIDTH/2 ,10))
        WIN.blit(level_lable,(WIDTH - level_lable.get_width()-10,10))

        
        for enemy in enemies:
            enemy.draw(WIN)

        for life in health_kit:
            life.draw(WIN)    

        player.draw(WIN)

        if lost:
            lost_lable = lost_font.render("Game  Over",1,(255,255,255))
            WIN.blit(lost_lable,(WIDTH/2 - lost_lable.get_width()/2,350))
        pygame.display.update()



    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <=0:
            lost = True
            lost_count +=1
            if lost_count == 1:
                mixer.music.fadeout(1000)
                playsound.playsound("Soundtracks/death.wav",False)
                time.sleep(1)
                playsound.playsound("Soundtracks/game_over.wav",False)

        if player.health <=20 and critical_flag:
            playsound.playsound("Soundtracks/critical_health.mp3",False)

            #critical_sound = pygame.mixer.Sound("critical_health.mp3")    
            #critical_sound.play()
            critical_flag = 0

        if lost:
            if lost_count > FPS * 2:
                run = False
                
            else:
                continue        

        if len(enemies) == 0:
            level += 1
            if(level != 1):
                playsound.playsound("Soundtracks/next_level.mp3",False)

            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green","white","grey"]))
                enemies.append(enemy)


        if len(health_kit) == 0:
            
            no_of_health_kit = 1
            for i in range(no_of_health_kit):
                happy = Lives(random.randrange(50, WIDTH-100), random.randrange(-2000, -100))
                health_kit.append(happy)






        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()


        keys = pygame.key.get_pressed()
        if  keys[pygame.K_LEFT] and player.x - player_vel > 0 :  # left arrow
            player.x -=  player_vel

        if  keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH:  # right arrow
            player.x +=  player_vel

        if  keys[pygame.K_UP] and player.y - player_vel > 0:  # UP arrow
            player.y -=  player_vel

        if  keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() +15 < HEIGHT:  # Down arrow
            player.y +=  player_vel

        if  keys[pygame.K_SPACE]:
            playsound.playsound("Soundtracks/fire.mp3",False)
            player.shoot()
                             

        for enemy in enemies[:]:
            enemy.move(enemy_vel)    
            enemy.move_lasers(laser_vel,player)

            if random.randrange(0,2 * FPS) == 1:
    
                enemy.shoot()
                

            if collide(enemy,player):
                player.health -=10
                kills +=1
                playsound.playsound("Soundtracks/ship_collision.mp3",False)  
                enemies.remove(enemy) 

            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                playsound.playsound("Soundtracks/crossing_boundary.mp3",False)  
                enemies.remove(enemy)


        for happy in health_kit[:]:
            happy.move(health_kit_vel)    

            if collide(happy,player):
                player.health = 100
                critical_flag = 1
                playsound.playsound("Soundtracks/health_up.mp3",False)
                health_kit.remove(happy)  

            elif happy.y > HEIGHT:
                  health_kit.remove(happy) 
  

        player.move_lasers(-laser_vel,enemies)  

def main_menu():
    lost_font = pygame.font.SysFont("comicsans",70)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_lable = lost_font.render("Click here to begin..",1,(255,255,255))
        WIN.blit(title_lable,(WIDTH/2 - title_lable.get_width()/2,350))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run == False
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                playsound.playsound("Soundtracks/begin.wav",False)

                main()
    pygame.quit()

main_menu()            
