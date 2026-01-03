import os
import pygame
import sys
import asyncio
import json

from backend.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from backend.logger import log_state, log_event
from backend.player import Player
from backend.asteroidfield import AsteroidField
from backend.asteroid import Asteroid
from backend.shot import Shot

os.environ["SDL_VIDEODRIVER"] = "dummy"

pygame.init()
screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

updatable = pygame.sprite.Group()
drawable = pygame.sprite.Group()
asteroids = pygame.sprite.Group()
shots = pygame.sprite.Group()

Player.containers = (updatable, drawable)
Asteroid.containers = (asteroids, updatable, drawable)
Shot.containers = (shots, updatable, drawable)
AsteroidField.containers = (updatable,)

player_object = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
asteroidfield_object = AsteroidField()

def run_game_step(dt):
    updatable.update(dt)

    for asteroid in asteroids:
        for shot in shots:
            if asteroid.collides_with(shot):
                log_event("asteroid_shot")
                shot.kill()
                asteroid.split()

        if asteroid.collides_with(player_object):
            log_event("player_hit")
            print("Game Over!")
            return False  

    return True  


async def game_loop(connected_clients):
    dt = 0
    while True:
        clock.tick(60)
        cont = run_game_step(dt)
        if not cont:
            break

        state = {
            "player": [player_object.position.x, player_object.position.y],
            "asteroids": [
                [a.position.x, a.position.y, a.radius] for a in asteroids
            ],
            "shots": [
                [s.position.x, s.position.y] for s in shots
            ],
        }

        if connected_clients:
            msg = json.dumps({"type": "state", "data": state})
            await asyncio.gather(*(c.send(msg) for c in connected_clients))

        await asyncio.sleep(1 / 60)  
