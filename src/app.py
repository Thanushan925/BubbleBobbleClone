from src.screens.menu import MenuScreen
from src.screens.play import PlayScreen
from src.screens.game_over import GameOverScreen

class App:
    def __init__(self):
        from src.screens.play import PlayScreen
        self.screens = {}
        self.current_screen = None
        self.change_screen("menu")

    def change_screen(self, screen_name):
        if screen_name not in self.screens:
            if screen_name == "menu":
                from src.screens.menu import MenuScreen
                self.screens["menu"] = MenuScreen(self)
            elif screen_name == "play":
                from src.screens.play import PlayScreen
                self.screens["play"] = PlayScreen()
            elif screen_name == "game_over":
                from src.screens.game_over import GameOverScreen
                self.screens["game_over"] = GameOverScreen(self)
        self.current_screen = self.screens[screen_name]

    def update(self, input_state):
        self.current_screen.update(input_state)

    def draw(self, screen):
        self.current_screen.draw(screen)