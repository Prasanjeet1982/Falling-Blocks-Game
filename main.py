import pygame
import random
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import threading

app = FastAPI()

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CHAR_WIDTH = 50
CHAR_HEIGHT = 50
BLOCK_WIDTH = 50
BLOCK_HEIGHT = 50
BLOCK_SPEED = 5

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Initialize pygame
pygame.init()

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Falling Blocks Game")

class Character:
    """Class representing the player-controlled character."""
    def __init__(self):
        self.x = (SCREEN_WIDTH - CHAR_WIDTH) // 2
        self.y = SCREEN_HEIGHT - CHAR_HEIGHT

    def move_left(self):
        """Move the character to the left."""
        self.x -= 10

    def move_right(self):
        """Move the character to the right."""
        self.x += 10

class Block:
    """Class representing falling blocks."""
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH - BLOCK_WIDTH)
        self.y = 0

    def move(self):
        """Move the block downwards."""
        self.y += BLOCK_SPEED
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH - BLOCK_WIDTH)

class Game:
    """Class managing the game state and logic."""
    def __init__(self):
        self.character = Character()
        self.block = Block()
        self.game_running = False
        self.lock = threading.Lock()

    def start_game(self):
        """Start the game."""
        with self.lock:
            if not self.game_running:
                self.character = Character()
                self.block = Block()
                self.game_running = True

    def move_character_left(self):
        """Move the character to the left."""
        self.character.move_left()

    def move_character_right(self):
        """Move the character to the right."""
        self.character.move_right()

    def game_loop(self):
        """Main game loop."""
        while True:
            with self.lock:
                if self.game_running:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.game_running = False

                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LEFT]:
                        self.move_character_left()
                    if keys[pygame.K_RIGHT]:
                        self.move_character_right()

                    self.block.move()

                    if self.check_collision():
                        self.game_running = False

                    screen.fill(BLACK)
                    pygame.draw.rect(screen, WHITE, (self.character.x, self.character.y, CHAR_WIDTH, CHAR_HEIGHT))
                    pygame.draw.rect(screen, WHITE, (self.block.x, self.block.y, BLOCK_WIDTH, BLOCK_HEIGHT))
                    pygame.display.flip()

            pygame.time.Clock().tick(30)

    def check_collision(self):
        """Check for collision between character and block."""
        return (self.character.x < self.block.x + BLOCK_WIDTH and
                self.character.x + CHAR_WIDTH > self.block.x and
                self.character.y < self.block.y + BLOCK_HEIGHT and
                self.character.y + CHAR_HEIGHT > self.block.y)

game_instance = Game()
game_thread = threading.Thread(target=game_instance.game_loop)
game_thread.daemon = True
game_thread.start()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render the game interface."""
    return templates.TemplateResponse("index.html", {"request": request, "game_running": game_instance.game_running})

@app.post("/start-game")
async def start_game():
    """Start the game route."""
    game_instance.start_game()
    return {"message": "Game started"}

@app.post("/move-left")
async def move_left():
    """Move the character left route."""
    game_instance.move_character_left()
    return {"message": "Moved left"}

@app.post("/move-right")
async def move_right():
    """Move the character right route."""
    game_instance.move_character_right()
    return {"message": "Moved right"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
