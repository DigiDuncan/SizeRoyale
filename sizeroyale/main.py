import importlib.resources as pkg_resources
import logging
from pathlib import Path
from typing import Optional
from tkinter import Tk
from tkinter.filedialog import askopenfilename

from digiformatter import logger as digilogger

import sizeroyale.data
from sizeroyale.lib.classes.game import Game
from sizeroyale.lib.loglevels import ROYALE

import arcade
from arcade import Sprite, SpriteList, Window
from arcade.key import RETURN

logger = logging.getLogger()

with pkg_resources.path(sizeroyale.data, "Roobert-Medium.otf") as p:
    arcade.text.load_font(str(p))

def setup_logging():
    global logger
    # Logging stuff.
    logging.basicConfig(level=logging.INFO)
    dfhandler = digilogger.DigiFormatterHandler()
    phandler = PygletHandler()
    logger.handlers = []
    logger.propagate = False
    logger.addHandler(dfhandler)
    
    logger2 = logging.getLogger("sizeroyale")
    logger2.handlers = []
    logger2.propagate = False
    logger2.addHandler(phandler)


def console_main():
    p = input("Input a Royale Spec file path, or hit [ENTER] for the default path.")
    if not p:
        p = Path(__file__).parent.parent / "royale-spec.txt"
    else:
        p = Path(p)
    game = Game(p)
    # logger.info(game)
    logger.log(ROYALE, f"seed = {game.seed}")
    print(game.royale.current_players)
    game.royale.stats_screen.show()

    while game.game_over is None:
        game.next()
        input()


class DebugLog:
    def __init__(self) -> None:
        self.messages: list[str] = []
        self.label = arcade.Text("", 0, 0)

    def render(self) -> str:
        renderstr = "\n".join([m for m in self.messages[-10:]])
        return renderstr

    def _log(self, message: str):
        self.messages.append(message)
        self.label.text = self.render()


class PygletHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def emit(self, record):
        debug_log = arcade.get_window().debug_log
        message = record.getMessage()
        debug_log._log(message)


class RoyaleWindow(Window):
    def __init__(self, path: str):
        super().__init__(1280, 720, "Royale")
        self.game: Optional[Game] = None
        self.next_flag = True
        self.stats_screen: Optional[Sprite] = None
        self.debug_log = DebugLog()

        self.path = path

        self.setup()

    def setup(self):
        self.game = Game(self.path)
        logger.info("Royale loaded.")

        self.sprite_list = SpriteList()

        _tex = arcade.Texture(self.game.royale.stats_screen)
        self.stats_screen = arcade.Sprite(_tex)
        self.stats_screen.top = 720
        self.stats_screen.left = 0
        self.sprite_list.append(self.stats_screen)

        self.text = arcade.Text("[TEXT]", self.stats_screen.right + 10, self.height - 10, arcade.color.BLACK, 24, self.width / 2,
                                anchor_y = "top", multiline = True, font_name = "Roobert")
        self.debug_log.label = self.text

        self.go_text = arcade.Text("[ENTER] to continue...", 5, 5, arcade.color.GREEN, 24,
                                anchor_y = "bottom", font_name = "Roobert", bold = True)

    def on_update(self, delta_time: float):
        if self.game and self.next_flag:
            self.game.next()
            _tex = arcade.Texture(self.game.royale.stats_screen)
            self.stats_screen.texture = _tex
            self.next_flag = False

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == RETURN:
            self.next_flag = True
            self.debug_log.messages = []

    def on_draw(self):
        self.clear(arcade.color.WHITE)
        self.sprite_list.draw()
        self.text.draw()
        self.go_text.draw()

def main():
    setup_logging()
    Tk().withdraw()
    with pkg_resources.path(sizeroyale.data, "royale-spec.txt") as path:
        dp = str(path)
    p = askopenfilename(initialfile = dp)
    RoyaleWindow(p).run()


if __name__ == "__main__":
    main()
