from src.game import Game
from src.input import InputState

class PlayScreen:
    def __init__(self):
        self.game = Game()
        self.paused = False

    def update(self, input_state: InputState):
        if input_state.pause_pressed:
            self.paused = not self.paused
            self.game.paused = self.paused

        if not self.paused:
            self.game.update(input_state)

    def draw(self, screen):
        self.game.draw(screen)