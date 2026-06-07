import pgzrun

WIDTH = 800
HEIGHT = 600
# this function is called 60 times per second
def draw():
   screen.clear()
   screen.draw.circle((400, 300), 30, 'white')

pgzrun.go()