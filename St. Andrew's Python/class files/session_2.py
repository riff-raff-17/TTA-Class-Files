import cv2                 # camera vision
import numpy as np    # for camera data transformation
import pygame           # for keyboard calls and driving
from ugot import ugot # for robot commands

got = ugot.UGOT()

# UGOT API stubs
def forward():
  got.mecanum_move_speed(0, 45)
  print("Robot -> Forward")

def backward():
  got.mecanum_move_speed(1, 45)
  print("Robot -> Backward")

def left():
  got.mecanum_turn_speed(2, 45)
  print("Robot -> Left")

def right():
  got.mecanum_turn_speed(3, 45)
  print("Robot -> Right")

#--------------------------------------------------------

def main():
  # Initialize UGOT camera
  got.initialize('192.168.88.1')
  got.open_camera()

  # Initialize pygame 
  pygame.init()
  screen = None
  clock = pygame.time.Clock()
  running = True

  while running:
    #1. Grab frame from ugot
    frame = got.read_camera_data()
    if not frame:
      break
    nparr = np.frombuffer(frame, np.uint8)
    data = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    flipped = cv2.flip(data, 1)
    frame_rgb = cv2.cvtColor(flipped, cv2.COLOR_BGR2RGB)

    # 2. On first frame, create a pygame window of matching size
    h, w = frame_rgb.shape[:2]
    if screen is None:
      screen = pygame.display.set_mode((w, h))
      pygame.display.set_caption("UGOT Camera")

    # 3. Convert to pygame surface
    surface = pygame.image.frombuffer(frame_rgb.tobytes(), (w, h), "RGB")
    screen.blit(surface, (0, 0))
    pygame.display.flip()

    # 4. Handle pygame events
    for evt in pygame.event.get():
      if evt.type == pygame.QUIT:
        running = False
      
      elif evt.type == pygame.KEYDOWN:
        if evt.key == pygame.K_w:
          forward()
        elif evt.key == pygame.K_s:
          backward()
        elif evt.key == pygame.K_a:
          left()
        elif evt.key == pygame.K_d:
          right()

      elif evt.type == pygame.KEYUP:
        if evt.key in (pygame.K_w, pygame.K_s, pygame.K_a,  pygame.K_d):
          got.mecanum_stop()
    
    # cap the frame rate
    clock.tick(30)

  pygame.quit()
  cv2.destroyAllWindows()

if __name__ == "__main__":
  main()
