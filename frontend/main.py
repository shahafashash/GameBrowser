
import pygame
from pygame.math import Vector2
from pygame.font import Font
from pygame.surface import Surface

from pathlib import Path
import os
import sys
from typing import List, Tuple

pygame.init()
win = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
fps = 60

FRAME_SIZE = (200, 100)

class Colors:
    # white
    white = (255, 255, 255)
    # black
    black = (0, 0, 0)
    # red
    red = (255, 0, 0)
    # green
    green = (0, 255, 0)
    # blue
    blue = (0, 0, 255)
    # yellow
    yellow = (255, 255, 0)
    # orange
    orange = (255, 165, 0)

class GuiFonts:
    default = pygame.font.SysFont("comicsansms", 20)
    tahoma = pygame.font.SysFont("tahoma", 20)
    arial = pygame.font.SysFont("arial", 20)
    header1 = pygame.font.SysFont("tahoma", 40)
    header2 = pygame.font.SysFont("tahoma", 30)
    header3 = pygame.font.SysFont("tahoma", 20)
    header4 = pygame.font.SysFont("tahoma", 10)



class GuiElement:
    def __init__(self, pos: Vector2=None) -> None:
        self.pos: Vector2 = Vector2(0, 0) if pos is None else pos
    def step(self):
        raise NotImplementedError("step() not implemented")
    def draw(self):
        raise NotImplementedError("draw() not implemented")


class Frame(GuiElement):
    def __init__(self) -> None:
        super().__init__()
        self.width: int = FRAME_SIZE[0]
        self.height: int = FRAME_SIZE[1]

        self.surf: Surface = None
        self.path: Path = None

        self.selected: bool = False
        self.text_surf: Surface = None

    def set_text(self, text: str, font: Font, color: Tuple[int, int, int]=Colors.blue) -> None:
        self.text_surf = font.render(text, True, color)

    def step(self) -> None:
        mouse_pos = pygame.mouse.get_pos()
        # if mouse inside frame
        self.selected = self.pos.x < mouse_pos[0] < self.pos.x + self.width and self.pos.y < mouse_pos[1] < self.pos.y + self.height

    def draw(self) -> None:
        # draw rectangle
        pygame.draw.rect(win, Colors.white, (self.pos.x, self.pos.y, self.width, self.height), border_radius=3)

        # draw text
        if self.text_surf:
            win.blit(self.text_surf, (self.pos.x + self.width // 2 - self.text_surf.get_width() // 2, self.pos.y + self.height // 2 - self.text_surf.get_height() // 2))

        if self.selected:
            pygame.draw.rect(win, Colors.red, (self.pos.x, self.pos.y, self.width, self.height), 2, border_radius=3)

    def on_click(self) -> None:
        print("clicked", str(self.path))
        

class Slider(GuiElement):
    def __init__(self, title: str) -> None:
        super().__init__()
        self.frames: List[Frame] = []
        self.title_surf: Surface = GuiFonts.header2.render(title, True, Colors.white)
        self.height: int = self.title_surf.get_height() + 10 + FRAME_SIZE[1]
    
    def add_frame(self, frame: Frame) -> None:
        self.frames.append(frame)
        frame.pos = Vector2(self.pos.x + (len(self.frames) - 1) * (FRAME_SIZE[0] + 10), self.pos.y + self.title_surf.get_height() + 10)

    @property
    def selected(self) -> Frame:
        for frame in self.frames:
            if frame.selected:
                return frame
        return None

    def step(self) -> None:
        for frame in self.frames:
            frame.step()

    def draw(self) -> None:
        # draw title
        win.blit(self.title_surf, (self.pos.x + 10, self.pos.y))        
        for frame in self.frames:
            frame.draw()

class Gui:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Gui, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.elements: List[GuiElement] = []
    
    @property
    def selected(self):
        for element in self.elements:
            selected = element.selected
            if selected:
                return selected
        return None

    def add_slider(self, slider: Slider):
        self.elements.append(slider)
        slider.pos.y = (len(self.elements) - 1) * (slider.height + 10)

    def step(self):
        for element in self.elements:
            element.step()

    def draw(self):
        for element in self.elements:
            element.draw()

    def add_element(self, element: GuiElement):
        self.elements.append(element)

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        for event in events:
        # mouse click
            left_click = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
            if left_click:
                selected_element = self.selected
                if selected_element:
                    selected_element.on_click()

# create bold arial font
font = Font(None, 24)
font.set_bold(True)





def main():
    gui = Gui()

    slider = Slider("Categories")
    gui.add_slider(slider)

    for i in range(5):
        frame = Frame()
        frame.path = Path(f"{os.getcwd()}/images/{i}.png")
        slider.add_frame(frame)
        frame.set_text(f"Frame {i}", GuiFonts.header3)

    slider2 = Slider("Images")
    gui.add_slider(slider2)

    for i in range(5):
        frame = Frame()
        frame.path = Path(f"{os.getcwd()}/images/{i}.png")
        slider2.add_frame(frame)
        frame.set_text(f"Frame {i}", GuiFonts.header3)

    # slider = Slider("PCMR")
    # gui.add_slider(slider)

    # for i in range(3):
    #     frame = Frame()
    #     frame.path = Path(f"{os.getcwd()}/images/{i}.png")
    #     slider.add_frame(frame)
    #     frame.set_text(f"Frame {i}", GuiFonts.header3)

    # slider = Slider("VR")
    # gui.add_slider(slider)

    # for i in range(2):
    #     frame = Frame()
    #     frame.path = Path(f"{os.getcwd()}/images/{i}.png")
    #     slider.add_frame(frame)
    #     frame.set_text(f"Frame {i}", GuiFonts.header3)

    

    done = False
    while not done:
        # get events
        events = pygame.event.get()
        gui.handle_events(events)
        for event in events:
            if event.type == pygame.QUIT:
                done = True
            
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            done = True

        # step frame
        gui.step()

        # draw frame
        gui.draw()

        # update screen
        pygame.display.update()
        # set fps
        clock.tick(fps)

if __name__ == "__main__":
    main()