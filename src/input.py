from dataclasses import dataclass

@dataclass
class InputState:
    left: bool = False
    right: bool = False
    up: bool = False       # <-- add this
    fire: bool = False     # <-- add this
    jump_pressed: bool = False
    fire_pressed: bool = False
    fire_held: bool = False
    pause_pressed: bool = False

_prev_space = False
_prev_up = False
_prev_p = False

def build_input_state(keyboard):
    global _prev_space, _prev_up, _prev_p
    is_ = InputState()
    is_.left = keyboard.left
    is_.right = keyboard.right
    is_.up = keyboard.up            # <-- add this
    is_.fire = keyboard.space       # <-- add this

    is_.jump_pressed = keyboard.up and not _prev_up
    _prev_up = keyboard.up

    is_.fire_pressed = keyboard.space and not _prev_space
    is_.fire_held = keyboard.space
    _prev_space = keyboard.space

    is_.pause_pressed = keyboard.p and not _prev_p
    _prev_p = keyboard.p

    return is_
