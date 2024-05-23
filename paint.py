from pygame import *
import os
import glob

# Function to count files by type
def count_files_by_type(folder_path, file_extension):
    search_pattern = os.path.join(folder_path, f"*.{file_extension}")
    files = glob.glob(search_pattern)
    count = len(files) + 1
    return count

# Function to get rainbow color based on a value
def rainbowColor(value):
    step = (value // 256) % 6
    pos = value % 256
    if step == 0:
        return (255, pos, 0)
    if step == 1:
        return (255-pos, 255, 0)
    if step == 2:
        return (0, 255, pos)
    if step == 3:
        return (0, 255-pos, 255)
    if step == 4:
        return (pos, 0, 255)
    if step == 5:
        return (255, 0, 255-pos)

# Function to draw rainbow selector
def drawRainbow(screen, r):
    if r:
        draw.circle(screen, (255, 0, 0), (100,690), 80, width=10, draw_top_right=True, draw_top_left=True)
        draw.circle(screen, (255, 165, 0), (100,690), 70, width=10, draw_top_right=True, draw_top_left=True)
        draw.circle(screen, (255, 255, 0), (100,690), 60, width=10, draw_top_right=True, draw_top_left=True)
        draw.circle(screen, (0, 255, 0), (100,690), 50, width=10, draw_top_right=True, draw_top_left=True)
        draw.circle(screen, (0, 0, 255), (100,690), 40, width=10, draw_top_right=True, draw_top_left=True)
        draw.circle(screen, (75, 0, 130), (100,690), 30, width=10, draw_top_right=True, draw_top_left=True)
        draw.circle(screen, (238, 130, 238), (100,690), 20, width=10, draw_top_right=True, draw_top_left=True)
    else:
        draw.rect(screen, (150,150,150), (20,610, 160, 80))

# Function to draw fill tool selector
def drawBucket(screen, b, c):
    if b:
        draw.rect(screen, (50,50,50), (50, 610, 100, 80), border_radius=5)
        draw.polygon(screen, c, ((55,615), (145,615),(120, 635),(100, 640), (80, 635)))
    else:
        draw.rect(screen, (150,150,150), (20,610, 160, 80))

# Function to draw color palette
def drawPalette(screen, color, dict, selected):
    global color_value
    draw.rect(screen, (150,150,150), (0,0, 200, SCREEN_Y-50))
    for x in range(2):
        for y in range(6):
            coord = (5+(100*x),5+(100*y), 90, 90)
            if (x*100,y*100) == selected:
                draw.rect(screen, (50,50,50), ((100*x),(100*y), 100, 100))
            draw.rect(screen, color[x][y], coord)
            dict[(coord[0],coord[0]+90, coord[1], coord[1]+90)] = color[x][y]

# Function to smooth the drawn line
def roundLine(screen, color, start, end, radius=1):
    Xaxis = end[0]-start[0]
    Yaxis = end[1]-start[1]
    dist = max(abs(Xaxis), abs(Yaxis))
    for i in range(dist):
        x = int(start[0]+float(i)/dist*Xaxis)
        y = int(start[1]+float(i)/dist*Yaxis)
        draw.circle(screen, color, (x, y), radius)

# Function to draw the radius selection circles
def selectRadius(screen, selected):
    colori = [(255,255,255),(255,255,255),(255,255,255)]
    colori.insert(selected, (0,0,0))
    centri = []
    for i in range(4):
        rad = (i+2)*2
        draw.circle(screen, colori[i], ((SCREEN_X-200)+50*i,(SCREEN_Y-25)), rad)
        centri.append(((SCREEN_X-200)+50*i,SCREEN_Y-25))
    return (selected+2)*2, centri

# Function to reset the screen and tools to default state
def reset():
    global colore, r, rainbow, colorePrec
    screen.fill(background)
    drawPalette(screen, colori, palette, (0,0))
    draw.rect(screen, (50,50,50), (0, SCREEN_Y-50, SCREEN_X, 50))
    draw.rect(screen, (200,200,200), (5,SCREEN_Y-50+5, 90,40))
    screen.blit(salva, (15,SCREEN_Y-50+10))
    draw.rect(screen, (200,200,200), (105,SCREEN_Y-50+5, 90,40))
    screen.blit(cancella, (115,SCREEN_Y-50+10))
    draw.rect(screen, (200,200,200), (205,SCREEN_Y-50+5, 90,40))
    screen.blit(riempi, (215,SCREEN_Y-50+10))
    draw.rect(screen, (200,200,200), (305,SCREEN_Y-50+5, 90,40))
    screen.blit(arcobaleno, (315,SCREEN_Y-50+10))
    colore = (0,0,0)
    r = selectRadius(screen, 2)[0]
    rainbow = False
    colorePrec = None

# Flood fill algorithm to fill an area with a color
def fill(surface, position, fill_color):
    fill_color = surface.map_rgb(fill_color)
    surf_array = surfarray.pixels2d(surface)
    current_color = surf_array[position]

    frontier = [position]
    while len(frontier) > 0:
        x, y = frontier.pop()
        try:
            if surf_array[x, y] != current_color:
                continue
        except IndexError:
            continue
        surf_array[x, y] = fill_color
        frontier.append((x + 1, y))  # Right.
        frontier.append((x - 1, y))  # Left.
        frontier.append((x, y + 1))  # Down.
        frontier.append((x, y - 1))  # Up.

    surfarray.blit_array(surface, surf_array)

def toggleRainbow(bucket, rainbow):
    global color_value, colore, colorePrec
    if bucket:
        mouse.set_cursor(Cursor(0))
        bucket = False
        drawBucket(screen, bucket, colore)
    if not rainbow:
        rainbow = True
    else:
        rainbow = False
        color_value = 0
        if colorePrec:
            colore = colorePrec
            colorePrec = None
    drawRainbow(screen, rainbow)
    return bucket, rainbow

def toggleBucket(bucket, rainbow):
    global colore, colorePrec
    if rainbow:
        mouse.set_cursor(Cursor(0))
        rainbow = False
        colore = colorePrec
        drawRainbow(screen, rainbow)
    if not bucket:
        bucket = True
        mouse.set_cursor(Cursor(11))
    else:
        bucket = False
    drawBucket(screen, bucket, colore)
    return bucket, rainbow

def changeSize():
    global r
    click = screen.get_at(mp) == (255,255,255)
    selected = False
    i = 0
    while not selected and i < 4:
        if (mp[0]**2+mp[1]**2) <= (centri[i][0]+8)**2 + (centri[i][1]+8)**2 and click:
            selected = True
            indice = i
        i += 1
    if selected:
        r = selectRadius(screen, indice)[0]

# Initialize Pygame
init()

# Initialize screen size and font
SCREEN_X, SCREEN_Y = 1280, 750 
myfont = font.SysFont("monospace", 30)
salva = myfont.render('SAVE', True, (50,50,50))
cancella = myfont.render('CANC', True, (50,50,50))
riempi = myfont.render('FILL', True, (50,50,50))
arcobaleno = myfont.render('RGB', True, (50,50,50))

# Define color palette
colori = [[(0, 0, 0),(255, 0, 0),(0, 255, 0),(0, 0, 255),(165, 42, 42),(255, 165, 0)],
          [(255, 255, 255),(255, 0, 255),(255, 255, 0),(0, 255, 255),(128, 0, 128),(255, 192, 203)]]

palette = {}
running = True
saving = False
colore = (0,0,0)
colorePrec = None
last_pos = None
color_value = 0
rainbow = False
bucket = False
clock = time.Clock()

# Set up the display
display.set_caption("PAINT IN PYTHON")
screen = display.set_mode([SCREEN_X, SCREEN_Y], DOUBLEBUF)
background = (255, 255, 255)
screen.fill(background)
drawPalette(screen, colori, palette, (0,0))
draw.rect(screen, (50,50,50), (0, SCREEN_Y-50, SCREEN_X, 50))

draw.rect(screen, (200,200,200), (5,SCREEN_Y-50+5, 90,40))
screen.blit(salva, (15,SCREEN_Y-50+10))
draw.rect(screen, (200,200,200), (105,SCREEN_Y-50+5, 90,40))
screen.blit(cancella, (115,SCREEN_Y-50+10))
draw.rect(screen, (200,200,200), (205,SCREEN_Y-50+5, 90,40))
screen.blit(riempi, (215,SCREEN_Y-50+10))
draw.rect(screen, (200,200,200), (305,SCREEN_Y-50+5, 90,40))
screen.blit(arcobaleno, (315,SCREEN_Y-50+10))

# Radius selection
r, centri = selectRadius(screen, 2)

# Main loop
while running:
    mp = mouse.get_pos()
    for e in event.get():
        if e.type == QUIT:
            running = False

        if e.type == KEYDOWN:
            if e.key == K_SPACE:
                bucket, rainbow = toggleRainbow(bucket, rainbow)
                

            if e.key == K_b:
                bucket, rainbow = toggleBucket(bucket, rainbow)

        if mouse.get_pressed()[0] and mp[0] > 200 + r and mp[1] < SCREEN_Y-50 - r and not saving:
            if not bucket:
                if rainbow:
                    if not colorePrec:
                        colorePrec = colore
                    color_value = (color_value + 8) % (256 * 6)
                    colore = rainbowColor(color_value)
                else:
                    if colorePrec:
                        colore = colorePrec
                        colorePrec = None
                draw.circle(screen, colore, mp, r)
                if last_pos:
                    roundLine(screen, colore, mp, last_pos, r)
                last_pos = mp
            else:
                if screen.get_at(mp)[:3] != colore and not rainbow:
                    fill(screen, mp, colore)

        if mouse.get_pressed()[0] and not (mp[0] > 200 + r and mp[1] < SCREEN_Y-50 - r) and not saving:
            last_pos = None

        if e.type == MOUSEBUTTONUP:
            last_pos = None
            color_value = 0

        if e.type == MOUSEBUTTONDOWN:
            if 0 <= mp[0] <= 200 and not saving and not rainbow:
                if 0 <= mp[1] <= SCREEN_Y-50:
                    for k in palette:
                        if k[0] <= mp[0] <= k[1] and k[2] <= mp[1] <= k[3]:
                            colore = palette[k]
                            drawPalette(screen, colori, palette, (k[0]-5,k[2]-5))
                            if bucket:
                                drawBucket(screen, bucket, colore)
                elif 5 <= mp[0] <= 95 and SCREEN_Y-50+5 <= mp[1] <= SCREEN_Y-5:
                    saving = True
                    screenshot = screen.subsurface(Rect(200, 0, SCREEN_X-200, SCREEN_Y-50))
                    count = count_files_by_type("paint", "png")
                    nome = input(f"SALVA CON NOME: {count}-")

                    while not nome.isalnum() and nome != "":
                        print("INVALID NAME!!!")
                        nome = input(f"SALVA CON NOME: {count}-")

                    if not nome:
                        if count:
                            image.save(screenshot, f"python_paint\\{count}-screenshot.png")
                            print(f"Saved as {count}-screenshot")
                        else:
                            image.save(screenshot, f"python_paint\\{count}-screenshot.png")
                            print(f"Saved as {count}-screenshot")
                    else:
                        image.save(screenshot, f"python_paint\\{count}-{nome}.png")
                        print(f"Saved as {count}-{nome}")
                    saving = False
                elif 105 <= mp[0] <= 195 and SCREEN_Y-50+5 <= mp[1] <= SCREEN_Y-5 and not saving:
                    reset()

            elif 205 <= mp[0] <= 295 and SCREEN_Y - 50 < mp[1] < SCREEN_Y - 10 and not saving:
                bucket, rainbow = toggleBucket(bucket, rainbow)

            elif 305 <= mp[0] <= 395 and SCREEN_Y - 50 < mp[1] < SCREEN_Y - 10 and not saving:
                bucket, rainbow = toggleRainbow(bucket, rainbow)

            elif mp[1] > SCREEN_Y-50:
                changeSize()

    display.flip()
    clock.tick(60)

quit()
