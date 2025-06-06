# -*- coding: utf-8 -*-
"""CSE423 LAb project_Zombies

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1pGwIwwwld9wRbSzIYpX6T3OHUfNSgq16
"""

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time
import math

window_width = 1000
window_height = 800

BUTTONS = {
    "reset": (340, 760, 380, 780),
    "pause": (420, 760, 460, 780),
    "quit":  (500, 760, 540, 780),
}

GRID_LENGTH = 600
CAMERA_MODE_THIRD_PERSON = 0
CAMERA_MODE_FIRST_PERSON = 1
FLOOR_COLOR = (0.9, 0.9, 0.9)
camera_mode = CAMERA_MODE_THIRD_PERSON
player_pos = [0, 0]
player_rotation = 0
player_jump_z = 0
is_jumping = False
jump_start_time = 0
JUMP_DURATION = 1.5
JUMP_HEIGHT = 100
camera_distance = 500
camera_height = 500
camera_angle = 45
camera_pitch = 30
fovY = 120
health = 100
score = 0
bullets = 0
game_paused = False
game_over = False
game_over_time = None
zombies = []
guns = []
hearts = []


game_start_time = time.time()
last_spawn_time = 0
spawn_interval = 5
pause_start_time = 0
paused_duration = 0
printed_running_state = False
zombie_speed = 0.15
zombie_speed_multiplier = 1.0
last_speed_increase_time = time.time()
SPEED_INCREASE_INTERVAL = 12


def update_jump():
    global player_jump_z, is_jumping, jump_start_time
    if is_jumping:
        elapsed = time.time() - jump_start_time
        if elapsed >= JUMP_DURATION:
            is_jumping = False
            player_jump_z = 0
        else:
            t = elapsed / JUMP_DURATION
            player_jump_z = 4 * JUMP_HEIGHT * t * (1 - t)

class GameObject:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.spawn_time = time.time()

    def draw(self):
        if self.kind == 'zombie':
            draw_zombie(self.x, self.y, 0)
        elif self.kind == 'gun':
            draw_gun(self.x, self.y)
        elif self.kind == 'heart':
            draw_heart(self.x, self.y)

def draw_gun(x, y):
    glPushMatrix()
    glTranslatef(x, y, 5)

    glPushMatrix()
    glTranslatef(0, 0, 0)
    glRotatef(-90, 1, 0, 0)
    glColor3f(0.2, 0.2, 0.2)
    gluCylinder(gluNewQuadric(), 2, 2, 8, 8, 1)
    glPopMatrix()

    # Gun barrel
    glPushMatrix()
    glTranslatef(0, 0, 8)
    glRotatef(0, 0, 0, 1)
    glColor3f(0.1, 0.1, 0.1)
    glScalef(1, 3, 1)
    glutSolidCube(4)
    glPopMatrix()

    # Gun muzzle
    glPushMatrix()
    glTranslatef(0, 6, 8)
    glColor3f(1, 0.2, 0.2)
    glutSolidSphere(1.5, 10, 10)
    glPopMatrix()

    glPopMatrix()


def draw_heart(x, y):
    glPushMatrix()

    jump_offset = 8 * abs(math.sin(time.time() * 3))
    glTranslatef(x, y, 10 + jump_offset)

    glColor3f(1, 0, 0)

    #heart top
    glPushMatrix()
    glTranslatef(-4, 0, 0)
    glutSolidSphere(10, 20, 20)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(4, 0, 0)
    glutSolidSphere(10, 20, 20)
    glPopMatrix()

    glBegin(GL_TRIANGLES)
    glVertex3f(-12, 3, 0)
    glVertex3f(12, 3, 0)
    glVertex3f(0, 0, -20)
    glEnd()

    glPopMatrix()



def draw_cartoon_human(x, y, z_base):
    glPushMatrix()
    glTranslatef(x, y, z_base)
    glRotatef(player_rotation - 90, 0, 0, 1)
    # Legs
    for offset in (-6, 6):
        glPushMatrix()
        glTranslatef(offset, 6, 0)
        glRotatef(-90, 1, 0, 0)
        glColor3f(0.3, 0.3, 0.3)
        gluCylinder(gluNewQuadric(), 2.5, 2.5, 12, 8, 1)
        glPopMatrix()

    # Body
    glPushMatrix()
    glTranslatef(0, 0, 35)
    glScalef(1.5, 1.2, 2.5)
    glColor3f(0,0,1)
    glutSolidCube(20)
    glPopMatrix()

    #  Head
    glPushMatrix()
    glTranslatef(0, 0, 72)
    glColor3f(0, 0, 0)
    glutSolidSphere(10, 12, 12)
    glPopMatrix()

    # Arms
    for offset in (-25, 15):
        glPushMatrix()
        glTranslatef(offset, 0, 36)
        glRotatef(90, 0, 1, 0)
        glColor3f(1, 0.8, 0.6)
        gluCylinder(gluNewQuadric(), 2, 2, 12, 8, 1)
        glPopMatrix()

    glPopMatrix()



def draw_zombie(x, y, z_base):
    global player_pos
    angle_to_player = math.degrees(math.atan2(player_pos[1] - y, player_pos[0] - x))

    glPushMatrix()
    glTranslatef(x, y, z_base)
    glRotatef(angle_to_player - 90, 0, 0, 1)

    # Legs
    for offset in (-3, 3):
        glPushMatrix()
        glTranslatef(offset, 10, 0)
        glRotatef(-90, 1, 0, 0)
        glColor3f(0, 0, 0)
        gluCylinder(gluNewQuadric(), 2, 0.5, 7, 6, 1)
        glPopMatrix()

    # Body
    glPushMatrix()
    glTranslatef(0, 0, 25)
    glColor3f(0.5, 0.1, 0.1)
    glScalef(1.0, 0.8, 2.0)
    glutSolidCube(20)
    glPopMatrix()

    # Arms
    for offset in (-6, 6):
        glPushMatrix()
        glTranslatef(offset, 10, 40)
        glRotatef(-90, 1, 0, 0)
        glColor3f(0.6, 0.9, 0.6)
        gluCylinder(gluNewQuadric(), 2.0, 2.0, 15, 6, 1)
        glPopMatrix()

    # Head
    glPushMatrix()
    glTranslatef(0, 0, 60)
    glColor3f(0.6, 0.9, 0.6)
    glutSolidSphere(9, 12, 12)
    glPopMatrix()

    glPopMatrix()


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(0, 0, 0)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)



def draw_grid():
    tile_size = 40
    glBegin(GL_QUADS)
    for x in range(-GRID_LENGTH, GRID_LENGTH, tile_size):
        for y in range(-GRID_LENGTH, GRID_LENGTH, tile_size):
            glColor3f(*FLOOR_COLOR)
            glVertex3f(x, y, 0)
            glVertex3f(x + tile_size, y, 0)
            glVertex3f(x + tile_size, y + tile_size, 0)
            glVertex3f(x, y + tile_size, 0)
    glEnd()




def draw_walls():
    wall_height = 80
    glBegin(GL_QUADS)
    glColor3f(0.48, 0.20, 0.10)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, wall_height)
    glEnd()

    glBegin(GL_QUADS)
    glColor3f(0.48, 0.20, 0.10)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, wall_height)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, wall_height)
    glEnd()

    glBegin(GL_QUADS)
    glColor3f(0.40, 0.16, 0.10)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, wall_height)
    glEnd()

    glBegin(GL_QUADS)
    glColor3f(0.40, 0.16, 0.10)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, wall_height)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, wall_height)
    glEnd()


def draw_pause_button(paused):
    x1, y1, x2, y2 = BUTTONS["pause"]
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    glColor3f(1, 0.75, 0)
    if paused:
        glBegin(GL_LINES)
        glVertex2f(center_x - 8, center_y + 15)
        glVertex2f(center_x - 8, center_y - 15)
        glVertex2f(center_x + 8, center_y + 15)
        glVertex2f(center_x + 8, center_y - 15)
        glEnd()
    else:
        glBegin(GL_TRIANGLES)
        glVertex2f(center_x - 6, center_y + 15)
        glVertex2f(center_x - 6, center_y - 15)
        glVertex2f(center_x + 12, center_y)
        glEnd()

def draw_reset_icon(x1, y1, x2, y2):
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    glColor3f(0, 1, 1)
    glBegin(GL_LINES)
    glVertex2f(center_x, center_y)
    glVertex2f(center_x - 20, center_y)
    glVertex2f(center_x - 10, center_y - 10)
    glVertex2f(center_x - 20, center_y)
    glVertex2f(center_x - 10, center_y + 10)
    glVertex2f(center_x - 20, center_y)
    glEnd()


def draw_quit_icon(x1, y1, x2, y2):
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    size = (x2 - x1) / 3

    glColor3f(1, 0.3, 0.3)
    glLineWidth(2)
    glBegin(GL_LINES)
    glVertex2f(center_x - size, center_y - size)
    glVertex2f(center_x + size, center_y + size)
    glVertex2f(center_x - size, center_y + size)
    glVertex2f(center_x + size, center_y - size)
    glEnd()



def draw_ui():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()


    draw_reset_icon(*BUTTONS["reset"])

    draw_pause_button(game_paused)

    draw_quit_icon(*BUTTONS["quit"])

    if game_paused:
        glColor3f(1, 0, 0)
        glRasterPos2f(window_width // 2 - 40, window_height // 2)
        for ch in "GAME PAUSED":
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)



def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if camera_mode == CAMERA_MODE_THIRD_PERSON:
        radius = 500
        cam_x = radius * math.cos(math.radians(camera_angle))
        cam_y = radius * math.sin(math.radians(camera_angle))
        cam_z = camera_height

        gluLookAt(cam_x, cam_y, cam_z, 0, 0, 0, 0, 0, 1)
    else:
        eye_x = player_pos[0]
        eye_y = player_pos[1]
        eye_z = 60 + player_jump_z

        look_x = eye_x + math.cos(math.radians(player_rotation))
        look_y = eye_y + math.sin(math.radians(player_rotation))
        look_z = eye_z

        gluLookAt(eye_x, eye_y, eye_z, look_x, look_y, look_z, 0, 0, 1)


def clamp_position(pos):
    return max(-GRID_LENGTH + 10, min(GRID_LENGTH - 10, pos))

def reset_game():
    global player_pos, player_rotation, health, score, bullets, zombies, guns, hearts
    global game_start_time, last_spawn_time, game_paused, paused_duration, pause_start_time
    global game_over, game_over_time, printed_running_state

    player_pos = [0, 0]
    player_rotation = 0
    health = 100
    bullets = 0
    zombies = []
    guns = []
    hearts = []
    game_start_time = time.time()
    last_spawn_time = 0
    game_paused = False
    paused_duration = 0
    pause_start_time = 0
    game_over = False
    game_over_time = None
    printed_running_state = False
    print("Game restarted.")

def update_game():
    global last_spawn_time, health, score, bullets, game_over, game_over_time, printed_running_state, zombie_speed, zombie_speed_multiplier, last_speed_increase_time, SPEED_INCREASE_INTERVAL


    if game_paused or game_over:
        return

    if not printed_running_state:
        print("Game is running...")
        printed_running_state = True

    now = time.time()

    if now - last_spawn_time > spawn_interval:
        spawn_x = random.randint(-GRID_LENGTH + 20, GRID_LENGTH - 20)
        spawn_y = random.randint(-GRID_LENGTH + 20, GRID_LENGTH - 20)
        zombies.append(GameObject(spawn_x, spawn_y, 'zombie'))

        bonus_x = random.randint(-GRID_LENGTH + 20, GRID_LENGTH - 20)
        bonus_y = random.randint(-GRID_LENGTH + 20, GRID_LENGTH - 20)

        if random.random() < 0.5:
            hearts.append(GameObject(bonus_x, bonus_y, 'heart'))
        else:
            guns.append(GameObject(bonus_x, bonus_y, 'gun'))

        last_spawn_time = now

    for lst in (guns, hearts):
        lst[:] = [o for o in lst if now - o.spawn_time < 10]

    if time.time() - last_speed_increase_time > SPEED_INCREASE_INTERVAL:
        zombie_speed_multiplier += 0.5
        last_speed_increase_time = time.time()

    speed = zombie_speed * zombie_speed_multiplier
    for z in zombies:
        dx = player_pos[0] - z.x
        dy = player_pos[1] - z.y
        dist = math.hypot(dx, dy)
        if dist > 1:
            z.x += speed * dx / dist
            z.y += speed * dy / dist
            z.x = clamp_position(z.x)
            z.y = clamp_position(z.y)

    for z in zombies[:]:
        distance = math.hypot(z.x - player_pos[0], z.y - player_pos[1])
        if distance < 20 and player_jump_z < 5:
            health = max(0, health - 25)
            zombies.remove(z)

    for gun in guns[:]:
        if abs(player_pos[0] - gun.x) < 20 and abs(player_pos[1] - gun.y) < 20:
            bullets += 5
            guns.remove(gun)
            print("Picked up bullets: +5")

    for heart in hearts[:]:
        if abs(player_pos[0] - heart.x) < 20 and abs(player_pos[1] - heart.y) < 20:
            health = min(100, health + 25)
            hearts.remove(heart)
            print("Picked up heart: +25 health")

    if health <= 0 and not game_over:
        game_over = True
        game_over_time = time.time()
        elapsed = game_over_time - game_start_time - paused_duration
        print(f"Game over! Final score (time survived): {int(elapsed)} seconds")

def keyboardListener(key, x, y):
    global player_pos, bullets, score, health, player_rotation
    global is_jumping, jump_start_time, camera_mode

    if game_paused or game_over:
        return

    move_step = 10
    if key == b'w':
        player_pos[0] += move_step * math.cos(math.radians(player_rotation))
        player_pos[1] += move_step * math.sin(math.radians(player_rotation))
    elif key == b's':
        player_pos[0] -= move_step * math.cos(math.radians(player_rotation))
        player_pos[1] -= move_step * math.sin(math.radians(player_rotation))
    elif key == b'a':
        player_rotation += 5
    elif key == b'd':
        player_rotation -= 5
    elif key == b'f' and bullets > 0:
        bullets -= 1
        for z in zombies[:]:
            if abs(z.x - player_pos[0]) < 30 and abs(z.y - player_pos[1]) < 30:
                zombies.remove(z)
                score += 1
                print("Zombie killed!")
                if score % 2 == 0:
                    health = min(100, health + 10)
                break
    elif key == b' ':
        if not is_jumping:
            is_jumping = True
            jump_start_time = time.time()
    elif key == b'c':
        camera_mode = CAMERA_MODE_FIRST_PERSON if camera_mode == CAMERA_MODE_THIRD_PERSON else CAMERA_MODE_THIRD_PERSON

    player_pos[0] = clamp_position(player_pos[0])
    player_pos[1] = clamp_position(player_pos[1])

def idle():
    update_game()
    glutPostRedisplay()
    update_jump()

def mouseListener(button, state, x, y):
    global game_paused, pause_start_time, paused_duration
    y = window_height - y
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if is_inside(x, y, BUTTONS["reset"]):
            reset_game()
        elif is_inside(x, y, BUTTONS["pause"]):
            if game_paused:
                paused_duration += time.time() - pause_start_time
                game_paused = False
                print("Game resumed.")
            else:
                pause_start_time = time.time()
                game_paused = True
                print("Game paused.")
        elif is_inside(x, y, BUTTONS["quit"]):
            print("Game quit.")
            glutLeaveMainLoop()

def showScreen():
    global game_over_time

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, window_width, window_height)
    setupCamera()
    draw_grid()
    draw_walls()

    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], 0)
    if camera_mode == CAMERA_MODE_THIRD_PERSON and not game_over:
        draw_cartoon_human(0, 0, player_jump_z)
    glPopMatrix()

    for o in zombies + guns + hearts:
        o.draw()

    draw_ui()

    if game_over and game_over_time:
        elapsed = game_over_time - game_start_time - paused_duration
    else:
        elapsed = (pause_start_time if game_paused else time.time()) - game_start_time - paused_duration

    draw_text(10, 770, f"Health: {health}%")
    draw_text(10, 740, f"Time Survived: {int(elapsed)}s")
    draw_text(10, 710, f"Bullets: {bullets}")
    draw_text(10, 680, f"Camera: {'First Person' if camera_mode == CAMERA_MODE_FIRST_PERSON else 'Third Person'}")

    if game_over:
        draw_text(window_width // 2 - 100, window_height // 2 + 20, "GAME OVER!", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(window_width // 2 - 140, window_height // 2 - 20, f"Your Score: {int(elapsed)} seconds", GLUT_BITMAP_TIMES_ROMAN_24)

    glutSwapBuffers()


def is_inside(x, y, region):
    x1, y1, x2, y2 = region
    return x1 <= x <= x2 and y1 <= y <= y2

def specialKeyListener(key, x, y):
    global camera_angle, camera_height
    if game_paused or game_over:
        return
    if camera_mode == CAMERA_MODE_THIRD_PERSON:
        if key == GLUT_KEY_LEFT:
            camera_angle += 5
        elif key == GLUT_KEY_RIGHT:
            camera_angle -= 5
        elif key == GLUT_KEY_UP:
            camera_height = min(1000, camera_height + 20)
        elif key == GLUT_KEY_DOWN:
            camera_height = max(100, camera_height - 20)
    camera_angle %= 360



glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(window_width, window_height)
glutInitWindowPosition(0, 0)
glutCreateWindow(b"Zombie Survival Arena - Fixed")
glEnable(GL_DEPTH_TEST)
glClearColor(0.25, 0.3, 0.35, 1.0)

glutDisplayFunc(showScreen)
glutIdleFunc(idle)
glutKeyboardFunc(keyboardListener)
glutMouseFunc(mouseListener)
glutSpecialFunc(specialKeyListener)
glutMainLoop()