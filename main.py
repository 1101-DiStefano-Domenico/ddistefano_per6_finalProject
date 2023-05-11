# File created by: Domenico DiStefano
'''
Game Structure:
Goals, Rules, Feedback, Freedom

Sources:
https://stackoverflow.com/questions/41348333/how-to-freeze-a-sprite-for-a-certain-amount-of-time-in-pygame
https://stackoverflow.com/questions/30720665/countdown-timer-in-pygame
Mr. Cozort for pathing and particles
https://www.youtube.com/watch?v=g1jo_qsO5c4&ab_channel=KidsCanCode

Goals:
Goal 1: create projectiles sprite ☑️
Goal 2: create score & healthbar ☑️
Goal 3: create start & end screen ☑️
Goal 4: make it replayable ☑️
Goal 5: add an upgrade system ☑️
Goal 6: add music ☑️
Goal 7: enemy wave system ☑️ / enemies come from off screen (maybe) ☑️
Goal 8: bullets that go to mouse pos ☑️
Goal 9: particles ☑️
Goal 10: animations and space themed pixel art
    - Player: UFO or Spaceship
    - Enemies: Aliens or UFOS
    - Background: Space ☑️
'''
# import libraries
import pygame as pg
import os
import time
from os import path
from math import floor
# import settings and sprites
from settings import *
from sprites import *


# set up assets folders
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "images")
sound_folder = os.path.join(game_folder, "sounds")

# class for cooldown timers
class Cooldown():
    def __init__(self):
        self.current_time = 0
        self.event_time = 0
        self.delta = 0
    def ticking(self):
        self.current_time = floor((pg.time.get_ticks())/1000)
        self.delta = self.current_time - self.event_time
        # print(self.delta)
    def reset(self):
        self.event_time = floor((pg.time.get_ticks())/1000)
    def timer(self):
        self.current_time = floor((pg.time.get_ticks())/1000)

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
        self.last_update = 0
        self.togglefire = False
        background = pg.image.load(os.path.join(img_folder, "backgroundgame.png")).convert()
        self.background = pg.transform.scale(background, (WIDTH, HEIGHT))

        # mob waves
        self.wavetimer = 10
        self.wavetimeadd = 10
        self.mobamount = 10
        self.hurtincrease = 0

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

    # method to set up game sounds
    def load_data(self):
        self.bgmusic = pg.mixer.music.load(path.join(sound_folder, "gamemusic2.mp3"))

    # method that adds sprites  
    def new(self):
        self.cd = Cooldown()
        # starting a new game and adding sprites to groups
        # separate groups for each sprite so I can effect them individually
        self.bullet_list = pg.sprite.Group()
        self.button_list = pg.sprite.Group()
        self.all_sprites = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.particle = pg.sprite.Group()
        self.player1 = pg.sprite.Group()
        self.player = Player(self)
        self.all_sprites.add(self.player)
        self.player1.add(self.player)

        # creating buttons
        self.button1 = Button(self, 350, 25, BLACK, WIDTH/2, 357)
        self.button2 = Button(self, 350, 25, BLACK, WIDTH/2, 407)
        self.button3 = Button(self, 350, 25, BLACK, WIDTH/2, 457)

        # makes range of mobs and adds them to all sprites group
        for i in range(0, self.mobamount):
            self.mob1 = Mob(self)
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
            self.dt = self.clock.tick(FPS)
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
                    if self.player.hp > 0:
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
                    self.money = 0
                    self.lifestealamount = 1
                    self.mobamount = 10
                    self.wavetimer = 10
                    self.wavetimeadd = 10
                    self.player.hurtamount = 1
                    self.hurtincrease = 0
                
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
                    mouse_pos = pg.mouse.get_pos()
                    mouse_x = mouse_pos[0]
                    mouse_y = mouse_pos[1]
                    pos_x = self.player.pos.x
                    pos_y = self.player.pos.y
                    if self.teleport:
                        # check if the length of the player position vector is greater than zero
                        if pg.math.Vector2(pos_x, pos_y).length() > 0:
                            for i in range(15):
                                p1 = Particle(pos_x, pos_y, 5,5, PURPLE)
                                self.all_sprites.add(p1)
                            # gets direction of mouse and moves player 250 units towards that position
                            direction = pg.math.Vector2(mouse_x, mouse_y) - self.player.pos
                            self.player.pos += direction.normalize() * 250

                # timestop
                if event.key == pg.K_q:
                    if self.timestopamount >= 1:
                        self.timestopamount -= 1
                        self.counter = 3
                        self.timestopcounter = True

            # clicking calls method
            if event.type == pg.MOUSEBUTTONUP:
                self.mousecollide()
            
            # counter for timestopping
            if self.timestopcounter:
                if event.type == self.timestoptimer:
                    self.counter -= 1
                    self.timestop = True
                    if self.counter == 0:
                        self.timestop = False
                        self.timestopcounter = False
            
            # togglefire
            if self.togglefire:
                now = pg.time.get_ticks()
                mouse_pos = pg.mouse.get_pos()
                mouse_x = mouse_pos[0]
                mouse_y = mouse_pos[1]
                if now - self.last_update > 100:
                    self.last_update = now
                    bullet = Projectile(self, (mouse_x, mouse_y))
                    self.all_sprites.add(bullet)
                    self.bullet_list.add(bullet)
            
            # time elapsed counter
            if self.alive and not self.timestop:
                if event.type == self.survivecounter:
                    self.timeelapsed += 1

            # rudimentary wave system
            if self.timeelapsed == self.wavetimer:
                    if self.wavetimeadd < 20:
                        self.wavetimeadd += 5
                    self.wavetimer += self.wavetimeadd
                    self.mobamount += 7
                    # increases mob damage over time
                    if self.hurtincrease < 2:
                        self.hurtincrease += 1
                    else:
                        self.player.hurtamount += 1
                        self.hurtincrease = 0
                    # adds mob amount proportional to self.mobamount
                    for i in range(0, self.mobamount):
                        self.mob1 = Mob(self)
                        self.all_sprites.add(self.mob1)
                        self.enemies.add(self.mob1)

    # method for lifesteal
    def lifesteal(self):
        self.player.hp += self.lifestealamount

    # method that updates the game at 1/60th of a second
    def update(self):
        # updates the timer for cooldown class
        self.cd.ticking()
        # updates button sprite group
        self.button_list.update()
        # if/else statement for timestopping
        if not self.upgradescreen and not self.timestop:
            self.all_sprites.update()
        elif not self.upgradescreen and self.timestop:
            self.player1.update()
        for bullet in self.bullet_list:
        # See if bullet hits an enemy
            self.enemy_hit_list = pg.sprite.spritecollide(bullet, self.enemies, True)
            # For each enemy hit, remove the bullet, add to the score & money, lifesteal, and add particles
            for e in self.enemy_hit_list:
                pos_x = self.enemy_hit_list[0].rect.x
                pos_y = self.enemy_hit_list[0].rect.y
                for i in range(5):
                    p2 = Particle(pos_x, pos_y, 5,5, GREEN)
                    self.all_sprites.add(p2)
                self.bullet_list.remove(bullet)
                self.all_sprites.remove(bullet)
                self.player.score += 1
                self.money += 5

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
        
    # method for displaying the game and displaying end screen when player hp = 0
    def draw(self):
        # start screen
        if not self.startgame:
            self.screen.blit(self.background, (0, 0))
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
                self.draw_text("UPGRADES", 100, WHITE, WIDTH/2, 250)
                self.draw_text("MONEY: $" + str(self.money), 30, WHITE, WIDTH/2, 600)
                self.draw_text("COST $100 - TELEPORT ABILITY", 30, WHITE, WIDTH/2, 350)
                self.draw_text("COST $50 - TIMESTOP ABILITY: " + str(self.timestopamount), 30, WHITE, WIDTH/2, 400)
                self.draw_text("COST $25 - LIFESTEAL AMOUNT: " + str(self.lifestealamount), 30, WHITE, WIDTH/2, 450)
                # adds clickable buttons with button class
                self.button_list.add(self.button1)
                self.button_list.add(self.button2)
                self.button_list.add(self.button3)
                self.draw_text("PRESS Q TO TIMESTOP", 30, WHITE, WIDTH/2, 650)
            elif self.teleport:
                self.alive = False
                self.togglefire = False
                self.screen.fill(BLACK)
                self.draw_text("UPGRADES", 100, WHITE, WIDTH/2, 250)
                self.draw_text("MONEY: $" + str(self.money), 30, WHITE, WIDTH/2, 600)
                self.draw_text("TELEPORT ABILITY GAINED", 30, WHITE, WIDTH/2, 350)
                self.draw_text("COST $50 - TIMESTOP ABILITY: " + str(self.timestopamount), 30, WHITE, WIDTH/2, 400)
                self.draw_text("COST $25 - LIFESTEAL AMOUNT: " + str(self.lifestealamount), 30, WHITE, WIDTH/2, 450)
                # adds clickable buttons with button class
                self.button_list.add(self.button1)
                self.button_list.add(self.button2)
                self.button_list.add(self.button3)
                self.draw_text("PRESS E TO TELEPORT", 30, WHITE, WIDTH/2, 670)
                self.draw_text("PRESS Q TO TIMESTOP", 30, WHITE, WIDTH/2, 650)
            
        else:
            # main game screen
            if self.player.hp > 0:
                self.alive = True
                self.screen.blit(self.background, (0, 0))
                self.all_sprites.draw(self.screen)
                self.draw_text("HULL INTEGRITY: " + str(self.player.hp), 30,WHITE, 1000, HEIGHT/32)
                self.draw_text("ELIMINATIONS: " + str(self.player.score), 30,WHITE, 120, HEIGHT/32)
                self.draw_text("TIME SURVIVED: " + str(self.timeelapsed) + " SECONDS", 30, WHITE, WIDTH/2, HEIGHT/32)
                self.draw_text("MONEY: $" + str(self.money), 30, WHITE, 83, HEIGHT/32 +30)
                self.draw_text("TIMESTOPS: " + str(self.timestopamount), 30, WHITE, 106, HEIGHT/32 +60)
            # end screen
            elif self.player.hp <= 0:
                self.alive = False
                self.togglefire = False
                self.screen.blit(self.background, (0, 0))
                self.draw_text("YOU DIED", 100, RED, WIDTH/2, 250)
                self.draw_text("PLAY AGAIN? (P)", 30, WHITE, WIDTH/2, 500)
                self.draw_text("ELIMINATIONS: " + str(self.player.score), 30, WHITE, WIDTH/2, 350)
                self.draw_text("TIME SURVIVED: " + str(self.timeelapsed) + " SECONDS", 30, WHITE, WIDTH/2, 400)
                self.draw_text("TOTAL SCORE: " + str(self.timeelapsed+(self.player.score*2)), 30, WHITE, WIDTH/2, 450)
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