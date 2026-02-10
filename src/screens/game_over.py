from src.input import build_input_state

class GameOverScreen:
    def __init__(self, app):
        self.app = app

    def update(self, keyboard):
        input_state = build_input_state(keyboard)
        if input_state.fire_pressed:
            self.app.change_screen("menu")

    def draw(self, screen):
        screen.clear()
        screen.blit("over", (0,0))
