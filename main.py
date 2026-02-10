from src.app import App
from src.input import build_input_state
from pgzero.builtins import keyboard
import pgzrun

app = App()

def update():
    input_state = build_input_state(keyboard)
    app.update(input_state)

def draw():
    app.draw(screen)

pgzrun.go()
