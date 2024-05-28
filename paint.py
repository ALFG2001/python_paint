from pygame import *
from os import path, makedirs
from glob import glob
from tkinter import Tk, simpledialog, filedialog

# Opens a dialog to select a directory
def select_directory():
    """Opens a dialog to select a directory."""
    root = Tk()
    root.withdraw()  # Hide the root window
    folder_selected = filedialog.askdirectory()
    root.iconify()
    root.destroy()
    return folder_selected

# Prompts the user to enter a file name
def prompt_file_name():
    """Prompts the user to enter a file name."""
    root = Tk()
    root.withdraw()  # Hide the root window
    file_name = simpledialog.askstring("Input", f"Save as:")
    return file_name

# Counts files by their type in a given folder
def count_files_by_type(folder_path, file_extension):
    """Counts files by their type in a given folder."""
    search_pattern = path.join(folder_path, f"*.{file_extension}")
    files = glob(search_pattern)
    count = len(files) + 1
    return count

# Returns rainbow color based on a value
def rainbowColor(value):
    """Returns rainbow color based on a value."""
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

# Draws rainbow icon
def drawRainbow(screen, r):
    """Draws rainbow icon."""
    if r:
        for i, color in enumerate([(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (238, 130, 238)]):
            draw.circle(screen, color, (100, 690), 80 - i * 10, width=10, draw_top_right=True, draw_top_left=True)
    else:
        draw.rect(screen, (150,150,150), (20,610, 160, 80))

# Function to draw fill tool icon
def drawBucket(screen, b, c):
    """Draws fill tool icon."""
    if b:
        draw.rect(screen, (50,50,50), (50, 610, 100, 80), border_radius=5)
        draw.polygon(screen, c, ((55,615), (145,615),(120, 635),(100, 640), (80, 635)))
    else:
        draw.rect(screen, (150,150,150), (20,610, 160, 80))

# Draws color palette
def drawPalette(screen, color, dict, selected):
    """Draws color palette."""
    global color_value
    draw.rect(screen, (150,150,150), (0,0, 200, SCREEN_Y-50))
    for x in range(2):
        for y in range(6):
            coord = (5+(100*x),5+(100*y), 90, 90)
            if (x*100,y*100) == selected:
                draw.rect(screen, (50,50,50), ((100*x),(100*y), 100, 100))
            draw.rect(screen, color[x][y], coord)
            dict[(coord[0],coord[0]+90, coord[1], coord[1]+90)] = color[x][y]

# Smooths the drawn line
def roundLine(screen, color, start, end, radius=1):
    """Smooths the drawn line."""
    Xaxis = end[0]-start[0]
    Yaxis = end[1]-start[1]
    dist = max(abs(Xaxis), abs(Yaxis))
    for i in range(dist):
        x = int(start[0]+float(i)/dist*Xaxis)
        y = int(start[1]+float(i)/dist*Yaxis)
        draw.circle(screen, color, (x, y), radius)

# Draws the radius selection circles
def selectRadius(screen, selected):
    """Draws the radius selection circles."""
    colori = [(255,255,255),(255,255,255),(255,255,255)]
    colori.insert(selected, (0,0,0))
    centri = []
    for i in range(4):
        rad = (i+2)*2
        draw.circle(screen, colori[i], ((SCREEN_X-200)+50*i,(SCREEN_Y-25)), rad)
        centri.append(((SCREEN_X-200)+50*i,SCREEN_Y-25))
    return (selected+2)*2, centri

# Draws the toolbar on the bottom
def draw_toolbar(screen, salva, cancella, riempi, arcobaleno, tastoUndo, tastoRedo):
    """Draws the toolbar on the bottom."""
    draw.rect(screen, (50, 50, 50), (0, SCREEN_Y - 50, SCREEN_X, 50))
    draw.rect(screen, (200, 200, 200), (5, SCREEN_Y - 50 + 5, 90, 40))
    screen.blit(salva, (15, SCREEN_Y - 50))
    draw.rect(screen, (200, 200, 200), (105, SCREEN_Y - 50 + 5, 90, 40))
    screen.blit(cancella, (115, SCREEN_Y - 50))
    draw.rect(screen, (200, 200, 200), (205, SCREEN_Y - 50 + 5, 90, 40))
    screen.blit(riempi, (215, SCREEN_Y - 50))
    draw.rect(screen, (200, 200, 200), (305, SCREEN_Y - 50 + 5, 90, 40))
    screen.blit(arcobaleno, (315, SCREEN_Y - 50))
    draw.rect(screen, (200, 200, 200), (405, SCREEN_Y - 50 + 5, 45, 40))
    screen.blit(tastoUndo, (415, SCREEN_Y - 50))
    draw.rect(screen, (200, 200, 200), (455, SCREEN_Y - 50 + 5, 45, 40))
    screen.blit(tastoRedo, (465, SCREEN_Y - 50))

# Resets the screen and tools to default state
def reset():
    """Resets the screen and tools to default state."""
    global colore, r, rainbow, bucket, colorePrec, selezione, font
    selezione = (0,0)
    screen.fill(background)
    drawPalette(screen, colori, palette, selezione)
    draw_toolbar(screen, salva, cancella, riempi, arcobaleno, tastoUndo, tastoRedo)
    colore = (0,0,0)
    r = selectRadius(screen, 2)[0]
    rainbow = False
    bucket = False
    mouse.set_cursor(Cursor(0))
    colorePrec = None

# Flood fill algorithm to fill an area with a color
def floodFill(surface, position, fill_color):
    """Flood fill algorithm to fill an area with a color."""
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

# Toggles rainbow mode
def toggleRainbow(bucket, rainbow):
    """Toggles rainbow mode."""
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

# Toggles fill bucket mode
def toggleBucket(bucket, rainbow):
    """Toggles fill bucket mode."""
    global colore, colorePrec
    if rainbow:
        rainbow = False
        colore = colorePrec
        drawRainbow(screen, rainbow)
    if not bucket:
        bucket = True
        mouse.set_cursor(Cursor(11))
    else:
        bucket = False
        mouse.set_cursor(Cursor(0))
    drawBucket(screen, bucket, colore)
    return bucket, rainbow

# Changes the size of the drawing tool
def changeSize():
    """Changes the size of the drawing tool."""
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

# Takes a screenshot
def save_canvas(screen, rect):
    """Takes a screenshot."""
    return screen.subsurface(rect).copy()

# Undoes or redoes drawing actions
def undoRedo(screen, list_pop, list_append, UR):
    """Undoes or redoes drawing actions."""
    global tastoUndo, tastoRedo
    sshot = save_canvas(screen, Rect(200, 0, SCREEN_X-200, SCREEN_Y-50))
    list_append.append(sshot)
    pixArray = surfarray.pixels2d(list_pop[-1])
    list_pop.pop(-1)
    surfarray.blit_array(screen.subsurface(Rect(200, 0, SCREEN_X-200, SCREEN_Y-50)), pixArray)
    if UR: #undo
        tastoRedo = myfont.render('↪', True, (50,50,50))
        screen.blit(tastoRedo, (465,SCREEN_Y-50))
        if not list_pop:
            tastoUndo = myfont.render('↩', True, (150,150,150))
            screen.blit(tastoUndo, (415,SCREEN_Y-50))
    else:
        tastoUndo = myfont.render('↩', True, (50,50,50))
        screen.blit(tastoUndo, (415,SCREEN_Y-50))
        if not list_pop:
            tastoRedo = myfont.render('↪', True, (150,150,150))
            screen.blit(tastoRedo, (465,SCREEN_Y-50))

# Initialize Pygame
init()

# Initialize screen size and font
SCREEN_X, SCREEN_Y = 1280, 750 
myfont = font.SysFont("segoeuisymbol", 30)
salva = myfont.render('SAVE', True, (50,50,50))
cancella = myfont.render('CANC', True, (50,50,50))
riempi = myfont.render('FILL', True, (50,50,50))
arcobaleno = myfont.render('RGB', True, (50,50,50))
tastoUndo = myfont.render('↩', True, (150,150,150))
tastoRedo = myfont.render('↪', True, (150,150,150))

# Define color palette
colori = [[(0, 0, 0),(255, 0, 0),(0, 255, 0),(0, 0, 255),(165, 42, 42),(255, 165, 0)],
          [(255, 255, 255),(255, 0, 255),(255, 255, 0),(0, 255, 255),(128, 0, 128),(255, 192, 203)]]

# flags and starting conditions
palette = {}
running = True
saving = False
colore = (0,0,0)
colorePrec = None
last_pos = None
color_value = 0
rainbow = False
bucket = False
selezione = (0,0)
clock = time.Clock()
flagUndo = False
screenshotsUndo = []
screenshotsRedo = []

# Set up the display
display.set_caption("PAINT IN PYTHON")
screen = display.set_mode([SCREEN_X, SCREEN_Y], DOUBLEBUF)
background = (255, 255, 255)
screen.fill(background)
drawPalette(screen, colori, palette, selezione)
draw_toolbar(screen, salva, cancella, riempi, arcobaleno, tastoUndo, tastoRedo)

# Radius selection
r, centri = selectRadius(screen, 2)

# Main loop
while running:
    # get mouse position
    mp = mouse.get_pos()
    #check events
    for e in event.get():

        # quit
        if e.type == QUIT:
            running = False

        # press button on keyboard (space or b)
        if e.type == KEYDOWN:

            # rgb
            if e.key == K_SPACE:
                bucket, rainbow = toggleRainbow(bucket, rainbow)
                
            # fill
            if e.key == K_b:
                bucket, rainbow = toggleBucket(bucket, rainbow)

            # undo
            if e.key == K_z and (key.get_mods() & KMOD_CTRL):
                if (key.get_mods() & KMOD_CTRL) and (key.get_mods() & KMOD_SHIFT):
                    if screenshotsRedo:
                        undoRedo(screen, screenshotsRedo, screenshotsUndo, False)
                elif screenshotsUndo:
                    undoRedo(screen, screenshotsUndo, screenshotsRedo, True)


        # draw + fill
        if mouse.get_pressed()[0] and mp[0] > 200 - r and mp[1] < SCREEN_Y-50 + r and not saving:
            if not flagUndo:
                screenshot = save_canvas(screen, Rect(200, 0, SCREEN_X-200, SCREEN_Y-50))
                screenshotsUndo.append(screenshot)
                screenshotsRedo = []
                flagUndo = True
                tastoUndo = myfont.render('↩', True, (50,50,50))
                tastoRedo = myfont.render('↪', True, (150,150,150))
                if len(screenshotsUndo) > 20:
                    screenshotsUndo.pop(0)
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
                drawPalette(screen, colori, palette, selezione)
                draw_toolbar(screen, salva, cancella, riempi, arcobaleno, tastoUndo, tastoRedo)
                selectRadius(screen, (r//2)-2)
                if rainbow:
                    drawRainbow(screen, True)
                elif bucket:
                    drawBucket(screen, True, colore)
                if last_pos:
                    roundLine(screen, colore, mp, last_pos, r)
                last_pos = mp
            else:
                try:
                    if screen.get_at(mp)[:3] != colore and not rainbow and mp[0] > 200 and mp[1] < SCREEN_Y-50:
                        floodFill(screen, mp, colore)
                except:
                    pass

        # click outside canvas
        if mouse.get_pressed()[0] and not (mp[0] > 200 - r and mp[1] < SCREEN_Y-50 + r ) and not saving:
            last_pos = None

        # release mouse
        if e.type == MOUSEBUTTONUP:
            last_pos = None
            color_value = 0
            flagUndo = False

        if e.type == MOUSEBUTTONDOWN:
            # click change color
            if 0 <= mp[0] <= 200 and 0 <= mp[1] <= SCREEN_Y-50 and not saving and not rainbow:
                for k in palette:
                    if k[0] <= mp[0] <= k[1] and k[2] <= mp[1] <= k[3]:
                        
                        colore = palette[k]
                        colorePrec = colore
                        selezione = (k[0]-5,k[2]-5)
                        drawPalette(screen, colori, palette, selezione)
                        if bucket:
                            drawBucket(screen, bucket, colore)
            # click save
            elif 5 <= mp[0] <= 95 and SCREEN_Y-50+5 <= mp[1] <= SCREEN_Y-5:
                saving = True
                screenshot = screen.subsurface(Rect(200, 0, SCREEN_X-200, SCREEN_Y-50))
                drawings_folder = select_directory()
                if drawings_folder:
                    count = count_files_by_type(drawings_folder, "png")
                    default_name = f"{count}"
                    file_name = prompt_file_name()
                    if file_name != None:
                        if not file_name:
                            filename = f"{default_name}-drawing.png"
                        else:
                            filename = f"{default_name}-{file_name}.png"

                        save_path = path.join(drawings_folder, filename)
                        # print(save_path)
                        try:
                            image.save(screenshot, save_path)
                        except error:
                            makedirs(drawings_folder)
                            image.save(screenshot, save_path)
                        print(f"Saved as {filename}")
                saving = False
            
            # click canc
            
            elif 105 <= mp[0] <= 195 and SCREEN_Y-50+5 <= mp[1] <= SCREEN_Y-5 and not saving:
                screenshot = save_canvas(screen, Rect(200, 0, SCREEN_X-200, SCREEN_Y-50))
                screenshotsUndo.append(screenshot)
                screenshotsRedo = []
                tastoUndo = myfont.render('↩', True, (50,50,50))
                tastoRedo = myfont.render('↪', True, (150,150,150))
                reset()

            # click fill
            elif 205 <= mp[0] <= 295 and SCREEN_Y - 50 < mp[1] < SCREEN_Y - 10 and not saving:
                bucket, rainbow = toggleBucket(bucket, rainbow)

            # click rgb
            elif 305 <= mp[0] <= 395 and SCREEN_Y - 50 < mp[1] < SCREEN_Y - 10 and not saving:
                bucket, rainbow = toggleRainbow(bucket, rainbow)
            
            # click undo
            elif 405 <= mp[0] <= 450 and SCREEN_Y - 50 < mp[1] < SCREEN_Y - 10 and not saving:
                if screenshotsUndo:
                    undoRedo(screen, screenshotsUndo, screenshotsRedo, True)

            elif 455 <= mp[0] <= 500 and SCREEN_Y - 50 < mp[1] < SCREEN_Y - 10 and not saving:
                if screenshotsRedo:
                        undoRedo(screen, screenshotsRedo, screenshotsUndo, False)

            # click circles to change size
            elif mp[1] > SCREEN_Y-50:
                changeSize()

            
    # draw everything
    display.flip()
    clock.tick(144)

quit()
