import arcade
import arcade.gui
from arcade.gui import UIManager
import numpy as np
import math

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
SCREEN_TITLE = "Acoustician 2.0"


# --- ABSORPTION & INPUT HANDLING FUNCTIONS ---

# Material choice : coefficient list
def set_absorb(absSelect):
    absDict = {
        0 : [0.01, 0.01, 0.03, 0.03, 0.04, 0.07], #smooth unpainted concrete
        1 : [0.30, 0.20, 0.15, 0.05, 0.05, 0.05], #plasterboard (18mm airspace w/ glass wool)
        2 : [0.15, 0.40, 0.65, 0.35, 0.35, 0.30], #muslin-covered cotton felt
        3 : [0.05, 0.04, 0.02, 0.04, 0.05, 0.05], #standard brickwork
        4 : [0.10, 0.20, 0.40, 0.60, 0.50, 0.60] #clinker concrete (no finish)
    }

    absList = absDict[absSelect]
    return absList

# Coefficient list + pulse frequency = current absorption
def current_abs(absList, ballFreq):
    frequencies = ["125", "250", "500", "1000", "2000", "4000"]
    fIndex = frequencies.index(str(ballFreq))
    return absList[fIndex]

# Set individual wall absorptions; returns list of floats
def vary_material():
    coeff = []
    entrOpt = check_quit(input("Enter absorption coefficients manually? "))

    if entrOpt == "yes" or entrOpt == "y":
        while True:
            try:
                coeff = [float(i) for i in input("Enter list for 125Hz, "
                                                 "250Hz, 500Hz, 1kHz, "
                                                 "2kHz, 4Hz: ").split()]
            except ValueError:
                print("Incorrect input format! [f f f f f f] required")
                continue
            else:
                if len(coeff) != 6:
                    print("Incorrect input format! All six coefficients "
                          "required")
                    continue
                else:
                    compareBools = []
                    for i in range(6):
                        compare = coeff[i] > 1.0
                        compareBools.append(compare)
                    if any(compareBools):
                        print("Absorption coefficients cannot be greater "
                              "than 1.0")
                        continue
                    else:
                        break

    # Choose from materials list
    else:
        while True:
            try:
                materials = ["Smooth concrete",
                             "Plasterboard",
                             "Muslin-covered Cotton Felt",
                             "Brick",
                             "Clinker concrete"]
                for index, material in enumerate(materials, start = 1):
                    print(str(index) + ". " + material)
                matChoice = get_int_input("Choose one: ")
                coeff = set_absorb(matChoice - 1)
            except KeyError:
                print("Incorrect index! 1-5 available only")
                continue
            else:
                break
    print("Absorption coefficients: ", coeff)
    return coeff

# Int input error handling
def get_int_input(text):
    while True:
        try:
            val = input(text)
            iVal = int(val)
        except ValueError:
            check_quit(val)
            print("Incorrect input format! Int required.")
            continue
        else:
            break
    return iVal

# Check for universal quit
def check_quit(text):
    text = text.lower()
    text = text.strip()
    if text == "quit":
        quit()
    else:
        return text


# --- CLASSES ---
class Ball:
    def __init__(self, freq):
        self.size = 5
        self.freq = freq
        self.color = self.set_color(self.freq)
        self.x = 0
        self.y = 0
        self.change_x = 0
        self.change_y = 0

    def draw(self):
        arcade.draw_circle_filled(self.x, self.y, self.size, self.color)

    # Frequency : color
    def set_color(self, f):
        colorDict = {
            125 : (255, 0, 0), #red
            250 : (255, 240, 0), #yellow
            500 : (0, 255, 0), #green
            1000 : (0, 255, 255), #cyan
            2000 : (0, 0, 255), #blue
            4000 : (255, 0, 255) #magenta
        }
        color = colorDict[f]
        return color

class Wall:
    def __init__(self, start_x, start_y, end_x, end_y, source, absInput):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.absorb = absInput
        self.type = "p"

        isVertical = False
        xDif = end_x - start_x
        yDif = end_y - start_y

        if xDif == 0:
            isVertical = True

        if isVertical:
            sourceVector = [source.x - start_x, 0.0]
            a = 1.0
            b = 0.0
            c = start_x
        else:
            m = yDif/xDif

            # Check for horizontal walls
            if yDif != 0:
                mNorm = xDif/yDif
            else:
                mNorm = 9999999999.0

            # Find shortest vector from wall to sound source
            denom = mNorm + m
            xIntersect = ((m * end_x) - end_y + source.y + (mNorm * source.x))/denom
            yIntersect = (m * (xIntersect - end_x)) + end_y
            sourceVector = np.subtract(source.pos, [xIntersect, yIntersect])
            a = -(yDif/xDif)
            b = 1.0
            c = (a * start_x) + start_y

        # Ensure vector points towards sound source
        if (sourceVector[1] < 0.0) or (isVertical and sourceVector[0] <= 0.0):
            a = -a
            b = -b
            c = -c
        self.c = c

        # Vector length
        d = np.sqrt(a**2 + b**2)
        self.d = d
        self.normal = [a, b]

        # Normalize vector
        if d != 1:
            a /= d
            b /= d
        self.unit = [a, b]

    def draw(self):
        arcade.draw_line(self.start_x,
                         self.start_y,
                         self.end_x,
                         self.end_y,
                         arcade.color.ASH_GREY)

class CircularWall:
    def __init__(self, center_x, center_y, radius, source, absInput):
        self.x = center_x
        self.y = center_y
        self.radius = radius
        self.absorb = absInput
        self.type = "c"

    def draw(self):
        arcade.draw_circle_filled(self.x,
                                  self.y,
                                  self.radius,
                                  arcade.color.ASH_GREY)

# Sound source class
class Source:
    def __init__(self, pos, angle):
        self.pos = pos
        self.x = pos[0]
        self.y = pos[1]
        self.range = 1800./(angle[1] - angle[0])
        self.min = angle[0] * np.pi/180.

# Button class
class MyFlatButton(arcade.gui.UIFlatButton):
    def on_click(self):
        global VIEW
        if self.text == 'Quit':
            quit()
        else:
            VIEW.isMakingWall = True

# Main window class
class MyView(arcade.View):
    def __init__(self):
        super().__init__()
        self.ball_list = []
        self.wall_list = []
        self.source = None
        self.isMakingWall = False
        self.wall_start_x = None
        self.wall_start_y = None
        self.edgeAbs = [0.01, 0.01, 0.03, 0.03, 0.04, 0.07]
        self.freq = 125
        self.ui_manager = UIManager()
        arcade.set_background_color(arcade.color.BLACK)

    # Initialize variables
    def setup(self):
        h = SCREEN_HEIGHT
        w = SCREEN_WIDTH

        quitButton = MyFlatButton(
            'Quit',
            center_x = 50,
            center_y = h - 18,
            width = 100,
            height = 25,
        )
        self.ui_manager.add_ui_element(quitButton)

        wallButton = MyFlatButton(
            'Make Wall',
            center_x = 200,
            center_y = h - 18,
            width = 150,
            height = 25,
        )
        self.ui_manager.add_ui_element(wallButton)

        # Set sound source
        while True:
            try:
                srcCoords = [int(i) for i in
                                input("Enter sound source "
                                      "coordinates (x y): ").split()]
            except ValueError:
                print("Incorrect input format! [Int Int] required.")
                continue
            else:
                try:
                    if (srcCoords[0] < 5
                            or srcCoords[1] < 5
                            or srcCoords[0] > w - 5
                            or srcCoords[1] > h - 5):
                        print("Out of bounds! Must be GTE to 5 "
                              "& within window boundaries.")
                        continue
                except IndexError:
                    print("Incorrect input format! [Int Int] required.")
                    continue
                else:
                    break
        while True:
            try:
                srcAngle = [int(i) for i in
                                input("Enter pulse angle, WRT positive "
                                      "vertical (x y): ").split()]
            except ValueError:
                print("Incorrect input format! [Int Int] required.")
                continue
            else:
                if (len(srcAngle) != 2) or (srcAngle[0] - srcAngle[1] == 0):
                    print("Incorrect input format! [Int Int] required "
                          "- difference must be non-zero.")
                    continue
                else:
                    break
        self.source = Source(srcCoords, srcAngle)

        # Set edge wall absorption coefficients
        self.wall_list.append(Wall(0, 0, w, 0, self.source, self.edgeAbs))
        self.wall_list.append(Wall(w, 0, w, h, self.source, self.edgeAbs))
        self.wall_list.append(Wall(w, h, 0, h, self.source, self.edgeAbs))
        self.wall_list.append(Wall(0, h, 0, 0, self.source, self.edgeAbs))
        print("Edge wall absorption coefficients: ", self.edgeAbs)

    # Render the screen
    def on_draw(self):
        arcade.start_render()

        for ball in self.ball_list:
            ball.draw()

        for wall in self.wall_list[4:]:
            wall.draw()

        arcade.draw_point(self.source.x,
                          self.source.y,
                          arcade.color.CAROLINA_BLUE,
                          10)

        output = "Pulse frequency: {}".format(str(self.freq) + " Hz")
        arcade.draw_text(output, 10, 20, arcade.color.WHITE, 14)

    # Send pulse according to source angle
    def make_balls(self, freq, source):
        for i in range(0, 11):
            ball = Ball(freq)
            ball.x = source.x
            ball.y = source.y
            ball.change_x = np.sin((i * np.pi / source.range) + source.min)
            ball.change_y = np.cos((i * np.pi / source.range) + source.min)
            self.ball_list.append(ball)

    # Decrease ball saturation
    def abs_color(self, absRate, ball):
        rgb = list(ball.color)
        # Check r, g, and b values individually
        for n in range(3):
            if rgb[n] != 0:
                rgb[n] -= int(absRate*255)
                if rgb[n] < 0:
                    rgb[n] = 0
        return rgb

    # Set edge wall absorptions
    def set_edge_abs(self):
        self.edgeAbs = vary_material()
        for wall in self.wall_list[:4]:
            wall.absorb = self.edgeAbs

    # Animation logic
    def on_update(self, delta_time):
        for ball in self.ball_list:
            ball.x += ball.change_x
            ball.y += ball.change_y

            # Collision with edge
            if ball.y < ball.size:
                ball.change_y *= -1
                ball.color = self.abs_color(
                                current_abs(self.wall_list[0].absorb, ball.freq),
                                ball)

            if ball.x > SCREEN_WIDTH - ball.size:
                ball.change_x *= -1
                ball.color = self.abs_color(
                                current_abs(self.wall_list[1].absorb, ball.freq),
                                ball)

            if ball.y > SCREEN_HEIGHT - ball.size:
                ball.change_y *= -1
                ball.color = self.abs_color(
                                current_abs(self.wall_list[2].absorb, ball.freq),
                                ball)

            if ball.x < ball.size:
                ball.change_x *= -1
                ball.color = self.abs_color(
                                current_abs(self.wall_list[3].absorb, ball.freq),
                                ball)

            # Collision with interior walls
            for wall in self.wall_list[4:]:
                ballVel = [ball.change_x, ball.change_y]
                future = [ball.x + ball.change_x, ball.y + ball.change_y]
                absorb = current_abs(wall.absorb, ball.freq)

                if wall.type == "p":
                    dist = (np.dot(wall.normal, future) - wall.c)/wall.d

                    if(dist < 0.0):
                        perp = 2 * np.multiply(
                                      (np.dot(wall.unit, ballVel)), wall.unit)
                        ball.change_x = np.subtract(ballVel, perp)[0]
                        ball.change_y = np.subtract(ballVel, perp)[1]
                        ball.color = self.abs_color(absorb, ball)
                else:
                    dist = np.sqrt((wall.x - ball.x)**2 + (wall.y - ball.y)**2)

                    if(dist < wall.radius):
                        theta = math.atan2(future[1] - wall.y,
                                           future[0] - wall.x)
                        r_hat = [np.cos(theta), np.sin(theta)]
                        v_r = -np.dot(ballVel, r_hat)
                        ball.change_x += 2 * v_r * np.cos(theta)
                        ball.change_y += 2 * v_r * np.sin(theta)
                        ball.color = self.abs_color(absorb, ball)

            # If ball has no more energy, delete from list
            if ball.color == [0,0,0]:
                self.ball_list.remove(ball)

    # Called whenever mouse button clicked
    def on_mouse_press(self, x, y, button, modifiers):
        if self.isMakingWall:
            self.wall_start_x = x
            self.wall_start_y = y

    # Called whenever mouse button released
    def on_mouse_release(self, x, y, button, modifiers):
        while self.isMakingWall:
            wallType = ""

            while True:
                wallType = check_quit(input("Enter wall type, "
                                           "planar or circular: "))
                if wallType == "planar" or wallType == "p":
                    wallType = "p"
                    break
                elif wallType == "circular" or wallType == "c":
                    wallType = "c"
                    break
                else:
                    print("Unknown wall type! "
                            "Please choose planar (p) or circular (c)")
                    continue

            if wallType == "p":
                planarWall = Wall(self.wall_start_x,
                                  self.wall_start_y,
                                  x,
                                  y,
                                  self.source,
                                  vary_material())
                self.wall_list.append(planarWall)
            else:
                radius = np.sqrt((self.wall_start_x - x)**2
                                 + (self.wall_start_y - y)**2)
                circleWall = CircularWall(self.wall_start_x,
                                          self.wall_start_y,
                                          radius,
                                          self.source,
                                          vary_material())
                self.wall_list.append(circleWall)
            self.isMakingWall = False

    # Respond to key input
    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.make_balls(self.freq, self.source)
        elif key == arcade.key.KEY_1:
            self.freq = 125
        elif key == arcade.key.KEY_2:
            self.freq = 250
        elif key == arcade.key.KEY_3:
            self.freq = 500
        elif key == arcade.key.KEY_4:
            self.freq = 1000
        elif key == arcade.key.KEY_5:
            self.freq = 2000
        elif key == arcade.key.KEY_6:
            self.freq = 4000
        elif key == arcade.key.E:
            print("Setting edge wall material...")
            self.set_edge_abs()
        else:
            print("Key input not mapped! Please try something else.")

def main():
    global VIEW
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    VIEW = MyView()
    window.show_view(VIEW)
    VIEW.setup()
    arcade.run()

if __name__ == "__main__":
    main()