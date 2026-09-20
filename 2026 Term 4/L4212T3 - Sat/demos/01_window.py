import arcade

# Constants: settings you might want to change
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Arcade Window"

class MyGame(arcade.Window):
    def __init__(self):
        # Run arcade.Window's own setup first. This is what opens a window.
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Now our own setup.
        self.background_color = arcade.color.DARK_BLUE_GRAY

    def on_draw(self):
        # Arcade calls this ~60 times a second
        self.clear()

        # A dot at the origin, to show where (0, 0) is
        arcade.draw_circle_filled(0, 0, 25, arcade.color.RED)
        arcade.draw_text("(0, 0) is here", 35, 20, arcade.color.WHITE, 14)

        # A dot at the top-right corner.
        arcade.draw_circle_filled(SCREEN_WIDTH, SCREEN_HEIGHT, 25, arcade.color.YELLOW)
        arcade.draw_text(
            f"({SCREEN_WIDTH}, {SCREEN_HEIGHT})",
            SCREEN_WIDTH - 130, SCREEN_HEIGHT - 45,
            arcade.color.WHITE, 14,
        )

# Outside the class. This creates one object and starts the looop.
window = MyGame()
arcade.run()
