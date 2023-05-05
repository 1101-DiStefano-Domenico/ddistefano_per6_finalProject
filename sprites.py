import pygame as pg
from pygame.sprite import Sprite
from settings import *
from random import randint
import math
import datetime
from math import floor


vec = pg.math.Vector2

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

    # method that takes user input and applies acceleration to the sprite
    def input(self):
        keystate = pg.key.get_pressed()

        if keystate[pg.K_a]:
            self.acc.x = -PLAYER_ACC
        if keystate[pg.K_d]:
            self.acc.x = PLAYER_ACC
        if keystate[pg.K_w]:
            self.acc.y = -PLAYER_ACC
        if keystate[pg.K_s]:
            self.acc.y = PLAYER_ACC
    
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
        for mob in self.game.all_sprites:
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
            self.vel.x *= 0
            self.vel.y *= 0
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
        self.pos = vec(randint(25, WIDTH - 25), randint(25, HEIGHT - 25))
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.steer = vec(0, 0)

    def seek(self, target):
        self.desired = (target - self.pos).normalize() * MAX_MOBSPEED
        self.steer = (self.desired - self.vel)
        if self.steer.length() > MAX_MOBFORCE:
            self.steer.scale_to_length(MAX_MOBFORCE)

    def seek_with_approach(self, target):
        self.desired = (target - self.pos) * 0.1
        if self.desired.length() > MAX_MOBSPEED:
            self.desired.scale_to_length(MAX_MOBSPEED)
        self.steer = (self.desired - self.vel)
        if self.steer.length() > MAX_MOBFORCE:
            self.steer.scale_to_length(MAX_MOBFORCE)

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

    def update(self):
        # mpos = vec(pg.mouse.get_pos())
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

# class for projectiles
class Projectile(pg.sprite.Sprite):
    def __init__(self, game):
        Sprite.__init__(self)
        self.game = game
        self.image = pg.Surface((10, 10))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.pos = vec(self.game.player.rect.x +25, self.game.player.rect.y +25)
        # self.pos = vec(randint(25, WIDTH - 25), randint(25, HEIGHT - 25))
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.steer = vec(0, 0)

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
        for mob in self.game.all_sprites:
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

    def update(self):
        # mpos = vec(pg.mouse.get_pos())'
        for e in self.game.enemies:
            seek = self.seek_with_approach2(e.pos)
        self.vel += seek * SEEK_WEIGHT
        if self.vel.length() > MAX_SPEED:
            self.vel.scale_to_length(MAX_SPEED)
        avoid = self.separate() * AVOID_WEIGHT
        self.vel += avoid
        if self.vel.length() > MAX_SPEED:
            self.vel.scale_to_length(MAX_SPEED)
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