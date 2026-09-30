import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TITLE = "Basic Shapes"

class BasicShapes(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
        self.background_color = arcade.color.ASH_GREY

    def on_draw(self):
        self.clear()

        # --- Circles: x, y, radius ---
        arcade.draw_circle_filled(100, 480, 40, arcade.color.RED)
        arcade.draw_circle_outline(100, 480, 40, arcade.color.BLACK, border_width=3)

        # --- Rectangle: build a Rect, then draw it ---
        box = arcade.XYWH(260, 480, 90, 70)
        arcade.draw_rect_filled(box, arcade.color.BLUE)
        arcade.draw_rect_outline(box, arcade.color.BLACK, border_width=2)

        same_box = arcade.LBWH(440, 445, 90, 70) # left, bottom, width, height
        arcade.draw_rect_filled(same_box, arcade.color.DARK_GREEN)

        # --- Line: note line_width, not border_width ---
        arcade.draw_line(550, 445, 650, 515, arcade.color.DARK_GREEN, line_width=5)

        # --- Polygon: a list of (x, y) points ---
        diamond = [(720, 445), (760, 480), (720, 515), (680, 480)]
        arcade.draw_polygon_filled(diamond, arcade.color.YELLOW)
        arcade.draw_polygon_outline(diamond, arcade.color.BLACK, line_width=3)

        # --- Alpha: a translucent panel over everything above ---
        panel = arcade.LRBT(60, 780, 300, 400)
        arcade.draw_rect_filled(panel, (0, 0, 0, 120)) # 4th number = see-through
        arcade.draw_text(
            "translucent panel (alpha = 120)", 80, 340, arcade.color.WHITE, 18
        )
        arcade.draw_text("Basic Shapes", 60, 550, arcade.color.BLACK, 22)

window = BasicShapes()
arcade.run()
