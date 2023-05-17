import pygame as pg
from pygame.sprite import Sprite
from settings import *
from random import randint
import random
import math
import datetime
from math import *
from secrets import choice


vec = pg.math.Vector2

class Cooldown():
    def __init__(self):
        self.current_time = 0
        self.event_time = 0
        self.delta = 0
    def ticking(self):
        self.current_time = floor((pg.time.get_ticks())/1000)
        self.delta = self.current_time - self.event_time
        # print(self.delta)
    def timer(self):
        self.current_time = floor((pg.time.get_ticks())/1000)

# player class
class Player(Sprite):
    def __init__(self, game):
        Sprite.__init__(self)
        self.game = game
        self.image = pg.Surface((50,50))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.pos = vec(WIDTH/2, HEIGHT/2)
        self.rect.center = self.pos
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.hp = HEALTH
        self.score = SCORE
        self.hurtamount = 1
        self.steer = vec(0,0)
    
    def input(self):
        keystate = pg.key.get_pressed()
        if keystate[pg.K_c]:
            self.vel.x *= 0
            self.vel.y *= 0

    def seek(self, target):
        self.desired = (target - self.pos).normalize() * MAX_SPEED
        self.steer = (self.desired - self.vel)
        if self.steer.length() > MAX_FORCE:
            self.steer.scale_to_length(MAX_FORCE)

    def seek_with_approach(self, target):
        self.desired = (target - self.pos) * 0.1
        if self.desired.length() > MAX_SPEED:
            self.desired.scale_to_length(MAX_SPEED)
        self.steer = (self.desired - self.vel)
        if self.steer.length() > MAX_FORCE:
            self.steer.scale_to_length(MAX_FORCE)

    def seek_with_approach2(self, target):
        # more intelligent slowing
        desired = (target - self.pos)
        d = desired.length()
        desired.normalize_ip()
        if d < APPROACH_RADIUS:
            desired *= d / APPROACH_RADIUS * MAX_SPEED
        else:
            desired *= MAX_SPEED
        steer = (desired - self.vel)
        if steer.length() > MAX_FORCE:
            steer.scale_to_length(MAX_FORCE)
        return steer
    
    def separate(self):
        # move away from other mobs
        desired = vec(0, 0)
        steer = vec(0, 0)
        count = 0
        for mob in self.game.enemies:
            if mob != self:
                d = self.pos.distance_to(mob.pos)
                if d < SEPARATION:
                    diff = (self.pos - mob.pos).normalize()
                    desired += diff
                    count += 1
        if count > 0:
            desired /= count
            desired.scale_to_length(MAX_SPEED)
            steer = (desired - self.vel)
            if steer.length() > MAX_FORCE:
                steer.scale_to_length(MAX_FORCE)
        return steer

    # this is a method that will keep the sprite on screen
    def inbounds(self):
        width = 50
        height = 50
        if self.rect.x > WIDTH - width:
            self.pos.x = WIDTH - width/2
            self.vel.x = 0
        if self.rect.x < 0:
            self.pos.x = width/2
            self.vel.x = 0
        if self.rect.y > HEIGHT - height:
            self.pos.y = HEIGHT - height/2
            self.vel.y = 0
        if self.rect.y < 0:
            self.pos.y = height/2
            self.vel.y = 0
    
    # method that detects mob collision and then subtracts from hp pool and slows player when colliding
    def mob_collide(self):
        hits = pg.sprite.spritecollide(self, self.game.enemies, False)
        if hits and not self.game.godmode:
            self.vel.x *= .75
            self.vel.y *= .75
            self.hp -= self.hurtamount
    
    # method that updates values every 1/60th of a second
    def update(self):
        mpos = vec(pg.mouse.get_pos())
        self.inbounds()
        self.mob_collide()
        seek = self.seek_with_approach2(mpos)
        self.vel += seek * SEEK_WEIGHT
        if self.vel.length() > MAX_SPEED:
            self.vel.scale_to_length(MAX_SPEED)
        avoid = self.separate() * AVOID_WEIGHT
        self.vel += avoid
        if self.vel.length() > MAX_SPEED:
            self.vel.scale_to_length(MAX_SPEED)
        self.pos += self.vel
        self.rect.center = self.pos

class Mob(pg.sprite.Sprite):
    def __init__(self, game):
        Sprite.__init__(self)
        self.game = game
        self.image = pg.Surface((16, 16))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        
        # calculate a random angle, offset, and distance
        distance = 1200
        angle = random.uniform(0, 2 * math.pi)
        offset = vec(math.cos(angle) * distance, math.sin(angle) * distance)
        # adds the offset to the player's position to get the initial position of the mob
        self.pos = self.game.player.pos + offset

        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.steer = vec(0, 0)

    # method for seeking player
    def seek(self, target):
        self.desired = (target - self.pos).normalize() * MAX_MOBSPEED
        self.steer = (self.desired - self.vel)
        if self.steer.length() > MAX_MOBFORCE:
            self.steer.scale_to_length(MAX_MOBFORCE)

    # method that determines speed and steering ability
    def seek_with_approach(self, target):
        self.desired = (target - self.pos) * 0.1
        if self.desired.length() > MAX_MOBSPEED:
            self.desired.scale_to_length(MAX_MOBSPEED)
        self.steer = (self.desired - self.vel)
        if self.steer.length() > MAX_MOBFORCE:
            self.steer.scale_to_length(MAX_MOBFORCE)

    # slows down or speeds up mob to more accurately follow player
    def seek_with_approach2(self, target):
        # more intelligent slowing
        desired = (target - self.pos)
        d = desired.length()
        desired.normalize_ip()
        if d < APPROACH_RADIUS:
            desired *= d / APPROACH_RADIUS * MAX_MOBSPEED
        else:
            desired *= MAX_MOBSPEED
        steer = (desired - self.vel)
        if steer.length() > MAX_MOBFORCE:
            steer.scale_to_length(MAX_MOBFORCE)
        return steer

    # method that moves mobs away from each other while still allowing them to somewhat overlap
    def separate(self):
        # move away from other mobs
        desired = vec(0, 0)
        steer = vec(0, 0)
        count = 0
        for mob in self.game.all_sprites:
            if mob != self:
                d = self.pos.distance_to(mob.pos)
                if d < SEPARATION:
                    diff = (self.pos - mob.pos).normalize()
                    desired += diff
                    count += 1
        if count > 0:
            desired /= count
            desired.scale_to_length(MAX_MOBSPEED)
            steer = (desired - self.vel)
            if steer.length() > MAX_MOBFORCE:
                steer.scale_to_length(MAX_MOBFORCE)
        return steer
    
    # method for player collision
    def player_collide(self):
        hits = pg.sprite.spritecollide(self, self.game.player1, False)
        if hits:
            self.vel.x *= 0
            self.vel.y *= 0

    def update(self):
        self.player_collide()
        seek = self.seek_with_approach2(self.game.player.pos)
        self.vel += seek * SEEK_WEIGHT
        if self.vel.length() > MAX_MOBSPEED:
            self.vel.scale_to_length(MAX_MOBSPEED)
        avoid = self.separate() * AVOID_WEIGHT
        self.vel += avoid
        if self.vel.length() > MAX_MOBSPEED:
            self.vel.scale_to_length(MAX_MOBSPEED)
        self.pos += self.vel
        self.rect.center = self.pos

# projectile class
class Projectile(pg.sprite.Sprite):
    def __init__(self, game, direction):
        pg.sprite.Sprite.__init__(self)
        # allowing the projectile to access the game instance
        self.game = game
        self.image = pg.Surface((7, 7))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        # initialized to a vector with x and y coordinates based on the player's position plus an offset of (25, 25).
        self.pos = vec(self.game.player.rect.x + 25, self.game.player.rect.y + 25)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.speed = MAX_BULLETSPEED
        self.direction = direction
    
    def update(self):
        # checks if the velocity of the projectile is zero
        if self.vel.length() == 0:
            targetx, targety = self.direction
            distance_x = targetx - self.rect.x
            distance_y = targety - self.rect.y
            # calculates the angle between the current position of the projectile and the target position (player)
            angle = atan2(distance_y, distance_x)
            # multiplying the speed with the cosine and sine of the angle
            speed_x = self.speed * cos(angle)
            speed_y = self.speed * sin(angle)
            self.vel = vec(speed_x, speed_y)
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos

        
class Button(Sprite):
    # parameters for mob class
    def __init__(self, game, width, height, color,x,y):
        Sprite.__init__(self)
        # allows us to use the player and game's parameters inside for the mob (used in the inbounds method)
        self.game = game
        self.width = width
        self.height = height
        self.image = pg.Surface((self.width,self.height))
        self.color = color
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        # randomizes starting position and velocity
        self.pos = vec(x,y)
    
    def update(self):
        # self.mousecollide()
        self.rect.center = self.pos

# particle class
class Particle(Sprite):
    def __init__(self, x, y, w, h, color):
        Sprite.__init__(self)
        self.image = pg.Surface((w, h))
        self.color = color
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.pos = (self.rect.x,self.rect.y)
        self.speedx = randint(2,5)*choice([-1,1])
        self.speedy = randint(2,5)*choice([-1,1])
        self.countdown = Cooldown()
        self.countdown.event_time = floor(pg.time.get_ticks()/1000)
    def update(self):
        # starts timer and applies speed values to x and y
        self.countdown.ticking()
        self.rect.x += self.speedx
        self.rect.y += self.speedy+GRAVITY
        self.pos = (self.rect.x, self.rect.y)
        # removes particle after one second
        if self.countdown.delta > 1:
            self.kill()