# File created by: Domenico DiStefano
'''
Game Structure:
Goals, Rules, Feedback, Freedom

Sources:
https://stackoverflow.com/questions/41348333/how-to-freeze-a-sprite-for-a-certain-amount-of-time-in-pygame
https://stackoverflow.com/questions/30720665/countdown-timer-in-pygame

Goal 1: create projectiles sprite ☑️
Goal 2: create score & healthbar ☑️
Goal 3: create start & end screen ☑️
Goal 4: make it replayable ☑️
Goal 5: add an upgrade system ☑️
Goal 6: add music
Goal 7: particles
Goal 8: enemy wave system/enemies come from off screen (maybe)
Goal 9: bullets that go to mouse pos
'''
# import libs
import pygame as pg
import os
# import settings 
from settings import *
from sprites import *
import time
from os import path
# from pg.sprite import Sprite

# set up assets folders
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "images")
sound_folder = os.path.join(game_folder, "sounds")


# create game class in order to pass properties to the sprites file
class Game:
    def __init__(self):
        # initiate game window and game settings
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("ALIEN SWARM (⌐■_■)")
        self.clock = pg.time.Clock()
        self.running = True
        self.startgame = False
        self.playmusic = False
    

        # no damage mode for testing
        self.godmode = False

        # counter for time survived
        self.alive = False
        self.timeelapsed = 0
        self.survivecounter = pg.USEREVENT+1
        pg.time.set_timer(self.survivecounter, 1000)

        # upgrade sreen settings and upgrade settings
        self.upgradescreen = False
        self.lifestealamount = 1
        self.money = 0
        self.teleport = False
        self.multishot = 1

        # timestop settings
        self.timestopamount = 0
        self.timestop = False
        self.timestopcounter = False
        self.counter = 3
        self.timestoptimer = pg.USEREVENT+1
        pg.time.set_timer(self.timestoptimer, 1000)

        # firerate settings
        self.firerate = 1
        self.fireratescore = 1
        self.togglefire = False
        self.lastshot = time.time()
    
    def load_data(self):
        self.bgmusic = pg.mixer.music.load(path.join(sound_folder, "gamemusic2.mp3"))

    # method that adds sprites  
    def new(self):
        # starting a new game and adding sprites to groups
        # separate groups for buttons and bullets so I can remove them individually
        # self.load_data()
        self.bullet_list = pg.sprite.Group()
        self.button_list = pg.sprite.Group()
        self.all_sprites = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.player1 = pg.sprite.Group()
        self.player = Player(self)
        self.all_sprites.add(self.player)
        self.player1.add(self.player)

        # creating buttons
        self.button1 = Button(self, 200, 25, BLACK, WIDTH/2, 357)
        self.button2 = Button(self, 250, 25, BLACK, WIDTH/2, 407)
        self.button3 = Button(self, 280, 25, BLACK, WIDTH/2, 457)
        self.button4 = Button(self, 300, 25, BLACK, WIDTH/2, 507)
        self.button5 = Button(self, 350, 25, BLACK, WIDTH/2, 557)

        # makes range of mobs and adds them to all sprites group
        for i in range(0,10):
            self.mob1 = Mob(self, self.player, 20, 20,GREEN)
            self.all_sprites.add(self.mob1)
            self.enemies.add(self.mob1)
        
        # background music
        pg.mixer.music.load(path.join(sound_folder, "gamemusic2.mp3"))

        self.run()

    # method for running the game
    def run(self):
        if self.playmusic:
            pg.mixer.music.play(loops=-1)
        self.playing = True
        # pg.mixer.music.fadeout(500)
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
            
            
    # method for detecting events in game
    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                # button for exiting game 
                if event.key == pg.K_ESCAPE:
                    self.startgame = True
                    self.playing = False
                    self.running = False

                # creates projectile on player location and adds it to all sprites and bullet list toggle on/off
                if event.key == pg.K_SPACE:
                    if not self.togglefire:
                        self.togglefire = True
                    else:
                        self.togglefire = False

                # key that starts game and resets game settings and upgrades
                if event.key == pg.K_p:
                    self.startgame = True
                    self.playing = False
                    self.timestopamount = 0
                    self.teleport = False
                    self.playmusic = True
                    self.timeelapsed = 0
                    self.mob1.enemyspeed = 0.05
                    self.money = 0
                    self.lifestealamount = 1
                    self.firerate = 1
                    self.fireratescore = 1
                    self.multishot = 1
                
                # button for upgrade screen
                if event.key == pg.K_u:
                    if not self.upgradescreen:
                        self.upgradescreen = True
                    else:
                        self.upgradescreen = False

                # cheats for dev testing
                if event.key == pg.K_0:
                    self.money += 1000
                if event.key == pg.K_9:
                    if not self.godmode:
                        self.godmode = True
                    else:
                        self.godmode = False

                # teleport
                if event.key == pg.K_e:
                    mouse_coords = pg.mouse.get_pos()
                    if self.teleport:
                        self.player.pos = mouse_coords

                # timestop
                if event.key == pg.K_q:
                    if self.timestopamount >= 1:
                        self.timestopamount -= 1
                        self.counter = 3
                        self.timestopcounter = True
            if event.type == pg.MOUSEBUTTONUP:
                self.mousecollide()
            if self.timestopcounter:
                if event.type == self.timestoptimer:
                    self.counter -= 1
                    self.timestop = True
                    if self.counter == 0:
                        self.timestop = False
                        self.timestopcounter = False
            
            # togglefire and multishot
            if self.togglefire:
                if time.time() - self.lastshot > 1/self.firerate:
                    for x in range(0, self.multishot):
                        bullet = Projectile(self, self.mob1, self.player)
                        bullet.rect.x = self.player.rect.x +20
                        bullet.rect.y = self.player.rect.y +20
                        self.all_sprites.add(bullet)
                        self.bullet_list.add(bullet)
                    self.lastshot = time.time()
            
            # time elapsed counter
            if self.alive:
                if event.type == self.survivecounter:
                    self.timeelapsed += 1
                    
    def lifesteal(self):
        self.player.hp += self.lifestealamount


    # method that updates the game at 1/60th of a second
    def update(self):
        

        self.button_list.update()
        if not self.upgradescreen and not self.timestop:
            self.all_sprites.update()
        elif not self.upgradescreen and self.timestop:
            self.player1.update()
        for bullet in self.bullet_list:
        # See if it hit a block
            self.enemy_hit_list = pg.sprite.spritecollide(bullet, self.enemies, True)
            # For each enemy hit, remove the bullet and add to the score
            for block in self.enemy_hit_list:
                self.bullet_list.remove(bullet)
                self.all_sprites.remove(bullet)
                self.player.score += 1
                self.money += 5
                # adds a new enemy after one dies
                self.mob1 = Mob(self, self.player, 20, 20,(0,255,0))
                self.all_sprites.add(self.mob1)
                self.enemies.add(self.mob1)

                # makes mobs path better as you kill them and replenish hp on kill
                self.mob1.enemyspeed += 0.01 
                self.lifesteal()

            # removes bullet if it exceeds a certain height or width
            if bullet.rect.y > HEIGHT:
                self.bullet_list.remove(bullet)
                self.all_sprites.remove(bullet)
            if bullet.rect.y < 0:
                self.bullet_list.remove(bullet)
                self.all_sprites.remove(bullet)
            if bullet.rect.x > WIDTH:
                self.bullet_list.remove(bullet)
                self.all_sprites.remove(bullet)
            if bullet.rect.x < 0:
                self.bullet_list.remove(bullet)
                self.all_sprites.remove(bullet)

    # method for detecting mouse collisions with buttons
    def mousecollide(self):
        mouse_coords = pg.mouse.get_pos()
        if self.button1.rect.collidepoint(mouse_coords):
            if self.money >= 100 and not self.teleport:
                self.teleport = True
                self.money -= 100
        elif self.button2.rect.collidepoint(mouse_coords):
            if self.money >= 50:
                self.timestopamount += 1
                self.money -= 50
        elif self.button3.rect.collidepoint(mouse_coords):
            if self.money >= 25:
                self.lifestealamount += 1
                self.money -= 25
        elif self.button4.rect.collidepoint(mouse_coords):
            if self.money >= 10 and self.firerate <= 10:
                self.firerate += 1
                self.fireratescore += 1
                self.money -= 10
        elif self.button5.rect.collidepoint(mouse_coords):
            if self.money >= 5:
                self.multishot += 1
                self.money -= 5
        

    # method for displaying the game and displaying end screen when player hp = 0
    def draw(self):
        # start screen
        if not self.startgame:
            self.screen.fill(BLACK)
            self.draw_text("ALIEN SWARM", 100, GREEN, WIDTH/2, 250)
            self.draw_text("PRESS P TO PLAY", 40, WHITE, WIDTH/2, 330)
            self.draw_text("WASD TO MOVE", 30, WHITE, WIDTH/2, 420)
            self.draw_text("SPACE TO SHOOT", 30, WHITE, WIDTH/2, 450)
            self.draw_text("KILL THE ALIENS TO REGAIN HP", 25, WHITE, WIDTH/2, 490)
            self.draw_text("PRESS U TO UPGRADE", 25, WHITE, WIDTH/2, 510)
        elif self.startgame and self.player.hp > 0 and self.upgradescreen:
            if not self.teleport:
                self.alive = False
                self.togglefire = False
                self.screen.fill(BLACK)
                self.button_list.draw(self.screen)
                self.draw_text("UPGRADES", 100, WHITE, WIDTH/2, 250)
                self.draw_text("MONEY: $" + str(self.money), 30, WHITE, WIDTH/2, 600)
                self.draw_text("COST $100 - TELEPORT ABILITY", 30, WHITE, WIDTH/2, 350)
                self.draw_text("COST $50 - TIMESTOP ABILITY: " + str(self.timestopamount), 30, WHITE, WIDTH/2, 400)
                self.draw_text("COST $25 - LIFESTEAL AMOUNT: " + str(self.lifestealamount), 30, WHITE, WIDTH/2, 450)
                if self.fireratescore < 10:
                    self.draw_text("COST $10 - FIRERATE: " + str(self.fireratescore) + "/SEC", 30, WHITE, WIDTH/2, 500)
                else:
                    self.draw_text("FIRERATE MAXED", 30, WHITE, WIDTH/2, 500)
                self.draw_text("COST $5 - MULTISHOT AMOUNT: " + str(self.multishot), 30, WHITE, WIDTH/2, 550)
                # adds clickable buttons with button class
                self.button_list.add(self.button1)
                self.button_list.add(self.button2)
                self.button_list.add(self.button3)
                self.button_list.add(self.button4)
                self.button_list.add(self.button5)
                self.draw_text("PRESS Q TO TIMESTOP", 30, WHITE, WIDTH/2, 650)
            elif self.teleport:
                self.alive = False
                self.togglefire = False
                self.screen.fill(BLACK)
                self.button_list.draw(self.screen)
                self.draw_text("UPGRADES", 100, WHITE, WIDTH/2, 250)
                self.draw_text("MONEY: $" + str(self.money), 30, WHITE, WIDTH/2, 600)
                self.draw_text("TELEPORT ABILITY GAINED", 30, WHITE, WIDTH/2, 350)
                self.draw_text("COST $50 - TIMESTOP ABILITY: " + str(self.timestopamount), 30, WHITE, WIDTH/2, 400)
                self.draw_text("COST $25 - LIFESTEAL AMOUNT: " + str(self.lifestealamount), 30, WHITE, WIDTH/2, 450)
                if self.fireratescore < 10:
                    self.draw_text("COST $10 - FIRERATE: " + str(self.fireratescore) + "/SEC", 30, WHITE, WIDTH/2, 500)
                else:
                    self.draw_text("FIRERATE MAXED", 30, WHITE, WIDTH/2, 500)
                self.draw_text("COST $5 - MULTISHOT AMOUNT: " + str(self.multishot+1), 30, WHITE, WIDTH/2, 550)
                # adds clickable buttons with button class
                self.button_list.add(self.button1)
                self.button_list.add(self.button2)
                self.button_list.add(self.button3)
                self.button_list.add(self.button4)
                self.button_list.add(self.button5)
                self.draw_text("PRESS E TO TELEPORT", 30, WHITE, WIDTH/2, 670)
                self.draw_text("PRESS Q TO TIMESTOP", 30, WHITE, WIDTH/2, 650)
        
            
        else:
            # main game screen
            if self.player.hp > 0:
                self.alive = True
                self.screen.fill(BLACK)
                self.all_sprites.draw(self.screen)
                self.draw_text("HP: " + str(self.player.hp), 30,WHITE, 1100, HEIGHT/32)
                self.draw_text("ELIMINATIONS: " + str(self.player.score), 30,WHITE, 120, HEIGHT/32)
                self.draw_text("TIME SURVIVED: " + str(self.timeelapsed) + " SECONDS", 30, WHITE, WIDTH/2, HEIGHT/32)
                self.draw_text("MONEY: $" + str(self.money), 30, WHITE, 83, HEIGHT/32 +30)
                self.draw_text("TIMESTOPS: " + str(self.timestopamount), 30, WHITE, 106, HEIGHT/32 +60)
            # end screen
            elif self.player.hp <= 0:
                self.alive = False
                self.togglefire = False
                self.screen.fill(BLACK)
                self.draw_text("YOU DIED", 100, RED, WIDTH/2, 250)
                self.draw_text("PLAY AGAIN? (P)", 30, WHITE, WIDTH/2, 450)
                self.draw_text("ELIMINATIONS: " + str(self.player.score), 30, WHITE, WIDTH/2, 350)
                self.draw_text("TIME SURVIVED: " + str(self.timeelapsed) + " SECONDS", 30, WHITE, WIDTH/2, 400)
                # removes all sprites to stop any updates while not visible
                self.all_sprites.empty()

    

        pg.display.flip()
    
    # method for drawing text
    def draw_text(self, text, size, color, x, y):
        font_name = pg.font.match_font('Monaco')
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x,y)
        self.screen.blit(text_surface, text_rect)
    
# instantiate the game class
g = Game()
# starts the game loop
while g.running:
    g.new()
pg.quit()