from src.input import build_input_state

class MenuScreen:
    def __init__(self, app):
        self.app = app

    def update(self, input_state):
        if input_state.fire_pressed:
            self.app.change_screen("play")

    def draw(self, screen):
        screen.fill((0,0,50))
        screen.draw.text("Bubble Bobble Clone", center=(400,200), fontsize=60, color="white")
        screen.draw.text("Press SPACE to start", center=(400,300), fontsize=40, color="yellow")
