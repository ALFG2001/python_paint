from pygame import *
from os import path, makedirs
from glob import glob
from tkinter import Tk, simpledialog, filedialog
from copy import deepcopy

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
def draw_toolbar(screen, salva, cancella, riempi, arcobaleno, tastoUndo, tastoRedo, tastoPicker):
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
    draw.rect(screen, (200, 200, 200), (505, SCREEN_Y - 50 + 5, 45, 40))
    screen.blit(tastoPicker, (515, SCREEN_Y - 50))

# Resets the screen and tools to default state
def reset():
    """Resets the screen and tools to default state."""
    global colore, radius, rainbow, bucket, colorePrec, selezione, font
    colori = deepcopy(default_colori)
    palette = {}
    selezione = (0,0)
    screen.fill(background)
    drawPalette(screen, colori, palette, selezione)
    draw_toolbar(screen, salva, cancella, riempi, arcobaleno, tastoUndo, tastoRedo, tastoPicker)
    colore = (0,0,0)
    radius = selectRadius(screen, 2)[0]
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
    global radius
    click = screen.get_at(mp) == (255,255,255)
    selected = False
    i = 0
    while not selected and i < 4:
        if (mp[0]**2+mp[1]**2) <= (centri[i][0]+8)**2 + (centri[i][1]+8)**2 and click:
            selected = True
            indice = i
        i += 1
    if selected:
        radius = selectRadius(screen, indice)[0]

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

def draw_slider(screen, x, y, value, color):
    """Draw a slider bar with the given value and color."""
    draw.rect(screen, (255, 255, 255), (x, y, 258, 20))  # Background
    draw.rect(screen, (0, 0, 0), (x, y, 258, 20), 2)    # Border
    draw.rect(screen, color, (x + 1, y + 1, value, 18)) # Value fill

def get_slider_value(mouse_x, slider_x):
    """Calculate the slider value based on mouse position."""
    return max(0, min(255, mouse_x - slider_x))

def buildColorPicker(window, colori:list, selected_color, selected):
    """Build the color picker interface."""
    myfont = font.SysFont("segoeuisymbol", 30)
    save = myfont.render('SAVE', True, (0, 0, 0))
    cancel = myfont.render('CANCEL', True, (0, 0, 0))
    
    window.blit(img, (0, 0))  # Display the color grid image

    draw.rect(window, (50, 50, 50), (720, 0, 360, 720))  # Sidebar background

    draw.rect(window, (150, 150, 150), (725, 650, 90, 50))  # Save button
    window.blit(save, (735, 650))

    draw.rect(window, (150, 150, 150), (950, 650, 125, 50))  # Cancel button
    window.blit(cancel, (960, 650))

    draw.rect(window, (150, 150, 150), (725, 105, 350, 118))  # Color preview area
   
    draw.rect(window, (150, 150, 150), (750, 250, 300, 50))
    window.blit(myfont.render('DEFAULT PALETTE', True, (0, 0, 0)), (760, 250))

    draw.rect(window, selected_color, (725, 5, 350, 90))  # Selected color display

    draw_slider(window, 760, 400, r, (255, 0, 0))  # Red slider
    draw_slider(window, 760, 450, g, (0, 255, 0))  # Green slider
    draw_slider(window, 760, 500, b, (0, 0, 255))  # Blue slider

    window.blit(myfont.render('R', True, (0, 0, 0)), (730, 385))
    window.blit(myfont.render('G', True, (0, 0, 0)), (730, 435))
    window.blit(myfont.render('B', True, (0, 0, 0)), (730, 485))

    draw.rect(window, (150, 50, 50), (1020, 390, 50, 40), border_radius=15)  # Red value box
    draw.rect(window, (50, 150, 50), (1020, 440, 50, 40), border_radius=15)  # Green value box
    draw.rect(window, (50, 50, 150), (1020, 490, 50, 40), border_radius=15)  # Blue value box

    window.blit(myfont.render(f'{r}', True, (0, 0, 0)), (1020, 385))
    window.blit(myfont.render(f'{g}', True, (0, 0, 0)), (1020, 435))
    window.blit(myfont.render(f'{b}', True, (0, 0, 0)), (1020, 485))

    for j in range(len(colori[0])):
        for i in range(len(colori)):
            color_rect = Rect(730 + 58 * j, 110 + 58 * i, 50, 50)
            if selected:
                if colori[i][j] == selected_color:
                    colori[selected_color_coord[0]][selected_color_coord[1]] = selected_color
                    draw.rect(window, selected_color, color_rect)
                    draw.rect(window, (50, 50, 50), color_rect, 3)
                else:
                    draw.rect(window, colori[i][j], color_rect)
            else:
                draw.rect(window, colori[i][j], color_rect)

    return colori, selected_color

# Initialize Pygame
init()

# Initialize screen size and font
SCREEN_X, SCREEN_Y = 1280, 770 
myfont = font.SysFont("segoeuisymbol", 30)
salva = myfont.render('SAVE', True, (50,50,50))
cancella = myfont.render('CANC', True, (50,50,50))
riempi = myfont.render('FILL', True, (50,50,50))
arcobaleno = myfont.render('RGB', True, (50,50,50))
tastoUndo = myfont.render('↩', True, (150,150,150))
tastoRedo = myfont.render('↪', True, (150,150,150))
tastoPicker = myfont.render('🎨', True, (50,50,50))

# Define color palette
colori = [[(0, 0, 0),(255, 0, 0),(0, 255, 0),(0, 0, 255),(165, 42, 42),(255, 165, 0)],
          [(255, 255, 255),(255, 0, 255),(255, 255, 0),(0, 255, 255),(128, 0, 128),(255, 192, 203)]]

new_colori = deepcopy(colori)
default_colori = deepcopy(colori)

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
img = image.load("picker/color_grid.png")
#img = image.load("python_paint/picker/color_grid.png")
image_rect = img.get_rect(topleft=(200, 0))
selected_color = (255, 255, 255)
r, g, b = selected_color[0], selected_color[1], selected_color[2]
selected_color_coord = 0,0
picking = False
selected = False

# Set up the display
display.set_caption("PAINT IN PYTHON")
screen = display.set_mode([SCREEN_X, SCREEN_Y], DOUBLEBUF)
background = (255, 255, 255)
screen.fill(background)
drawPalette(screen, colori, palette, selezione)
draw_toolbar(screen, salva, cancella, riempi, arcobaleno, tastoUndo, tastoRedo, tastoPicker)

# Radius selection
radius, centri = selectRadius(screen, 2)

# Main loop
while running:
    # get mouse position
    mp = mouse.get_pos()
    if picking:
        if 200 < mp[0] < 920 and mp[1] < 720:
            mouse.set_cursor(3)
        else:
            mouse.set_cursor(0)
    #check events
    for e in event.get():

        # quit
        if e.type == QUIT:
            running = False

        # press button on keyboard (space or b)
        if e.type == KEYDOWN:

            # rgb
            if e.key == K_SPACE and not picking:
                bucket, rainbow = toggleRainbow(bucket, rainbow)
                
            # fill
            if e.key == K_b and not picking:
                bucket, rainbow = toggleBucket(bucket, rainbow)

            # undo
            if e.key == K_z and (key.get_mods() & KMOD_CTRL) and not picking:
                if (key.get_mods() & KMOD_CTRL) and (key.get_mods() & KMOD_SHIFT):
                    if screenshotsRedo:
                        undoRedo(screen, screenshotsRedo, screenshotsUndo, False)
                elif screenshotsUndo:
                    undoRedo(screen, screenshotsUndo, screenshotsRedo, True)

            if e.key == K_p:
                if not picking:
                    beforePick = save_canvas(screen, Rect(200, 0, SCREEN_X-200, SCREEN_Y-50))
                    buildColorPicker(screen.subsurface(200,0,1080,720), colori, (255,255,255), selected)
                    picking = True
                else:
                    picking = False
                    mouse.set_cursor(0)
                    screen.blit(beforePick, Rect(200, 0, SCREEN_X-200, SCREEN_Y-50))

        # draw + fill
        if mouse.get_pressed()[0] and mp[0] > 200 - radius and mp[1] < SCREEN_Y-50 + radius and not saving and not picking:
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
                draw.circle(screen, colore, mp, radius)
                drawPalette(screen, colori, palette, selezione)
                draw_toolbar(screen, salva, cancella, riempi, arcobaleno, tastoUndo, tastoRedo, tastoPicker)
                selectRadius(screen, (radius//2)-2)
                if rainbow:
                    drawRainbow(screen, True)
                elif bucket:
                    drawBucket(screen, True, colore)
                if last_pos:
                    roundLine(screen, colore, mp, last_pos, radius)
                last_pos = mp
            else:
                try:
                    if screen.get_at(mp)[:3] != colore and not rainbow and mp[0] > 200 and mp[1] < SCREEN_Y-50:
                        floodFill(screen, mp, colore)
                except:
                    pass

        # click outside canvas
        if mouse.get_pressed()[0] and not (mp[0] > 200 - radius and mp[1] < SCREEN_Y-50 + radius ) and not saving and not picking:
            last_pos = None

        # release mouse
        if e.type == MOUSEBUTTONUP:
            last_pos = None
            color_value = 0
            flagUndo = False

        if e.type == MOUSEBUTTONDOWN:
            # click change color
            if 0 <= mp[0] <= 200 and 0 <= mp[1] <= SCREEN_Y-50 and not saving and not rainbow and not picking:
                for k in palette:
                    if k[0] <= mp[0] <= k[1] and k[2] <= mp[1] <= k[3]:
                        
                        colore = palette[k]
                        colorePrec = colore
                        selezione = (k[0]-5,k[2]-5)
                        drawPalette(screen, colori, palette, selezione)
                        if bucket:
                            drawBucket(screen, bucket, colore)
            # click save
            elif 5 <= mp[0] <= 95 and SCREEN_Y-50+5 <= mp[1] <= SCREEN_Y-5 and not picking:
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
            
            elif 105 <= mp[0] <= 195 and SCREEN_Y-50+5 <= mp[1] <= SCREEN_Y-5 and not saving and not picking:
                screenshot = save_canvas(screen, Rect(200, 0, SCREEN_X-200, SCREEN_Y-50))
                screenshotsUndo.append(screenshot)
                screenshotsRedo = []
                tastoUndo = myfont.render('↩', True, (50,50,50))
                tastoRedo = myfont.render('↪', True, (150,150,150))
                reset()

            # click fill
            elif 205 <= mp[0] <= 295 and SCREEN_Y - 50 < mp[1] < SCREEN_Y - 10 and not saving and not picking:
                bucket, rainbow = toggleBucket(bucket, rainbow)

            # click rgb
            elif 305 <= mp[0] <= 395 and SCREEN_Y - 50 < mp[1] < SCREEN_Y - 10 and not saving and not picking:
                bucket, rainbow = toggleRainbow(bucket, rainbow)
            
            # click undo
            elif 405 <= mp[0] <= 450 and SCREEN_Y - 50 < mp[1] < SCREEN_Y - 10 and not saving and not picking:
                if screenshotsUndo:
                    undoRedo(screen, screenshotsUndo, screenshotsRedo, True)

            elif 455 <= mp[0] <= 500 and SCREEN_Y - 50 < mp[1] < SCREEN_Y - 10 and not saving and not picking:
                if screenshotsRedo:
                        undoRedo(screen, screenshotsRedo, screenshotsUndo, False)

            elif 505 <= mp[0] <= 550 and SCREEN_Y - 50 < mp[1] < SCREEN_Y - 10 and not saving and not picking:
                beforePick = save_canvas(screen, Rect(200, 0, SCREEN_X-200, SCREEN_Y-50))
                buildColorPicker(screen.subsurface(200,0,1080,720), colori, (255,255,255), selected)
                picking = True

            # click circles to change size
            elif mp[1] > SCREEN_Y-50 and not picking:
                changeSize()

        if picking:      
            new_colori, nuovo_colore = buildColorPicker(screen.subsurface(200,0,1080,720), colori, selected_color, selected)  

            if e.type == MOUSEBUTTONDOWN:
                if 650 <= mp[1] <= 700:
                    if 925 <= mp[0] <= 1015:
                        colori = deepcopy(new_colori)
                        palette = {}
                        drawPalette(screen, colori, palette, selezione)
                        selected = False
                        if colore not in colori[0] and colore not in colori[1]:
                            colore =  nuovo_colore
                        picking = False
                        mouse.set_cursor(0)
                        screen.blit(beforePick, Rect(200, 0, SCREEN_X-200, SCREEN_Y-50))

                    elif 1150 <= mp[0] <=1275:
                        colori = deepcopy(default_colori)
                        picking = False
                        selected = False
                        mouse.set_cursor(0)
                        drawPalette(screen, colori, palette, selezione)
                        screen.blit(beforePick, Rect(200, 0, SCREEN_X-200, SCREEN_Y-50))

                elif 250 <= mp[1] <= 300:
                    if 950 <= mp[0] <= 1250:
                        colori = deepcopy(default_colori)
                        new_colori = deepcopy(colori)
                        palette = {}
                        drawPalette(screen, colori, palette, selezione)
                        selected = False

            
            elif mouse.get_pressed()[0] or (e.type == MOUSEMOTION and e.buttons[0] == 1):
                # Check if mouse is dragged while clicked within the image rect
                if image_rect.collidepoint(mp[0],mp[1]):
                    # Get the color of the pixel at the mouse position
                    selected_color = img.get_at((mp[0] - image_rect.x, mp[1] - image_rect.y))
                    r, g, b = selected_color[0], selected_color[1], selected_color[2]
                    if selected:
                        colori[selected_color_coord[0]][selected_color_coord[1]] = selected_color
                        draw.rect(screen, selected_color, colored_square)
                        draw.rect(screen, (50, 50, 50), colored_square, 3)

                # Check if mouse is clicked within color palette squares
                elif 110 <= mp[1] <= 220 and 930 <= mp[0] <= 1270:
                    for j in range(len(colori[0])):
                        for i in range(len(colori)):
                            color_rect = Rect(930 + 58 * j, 110 + 58 * i, 50, 50)
                            draw.rect(screen, colori[i][j], color_rect)
                            if color_rect.collidepoint(mp):
                                selected_square = draw.rect(screen, (50, 50, 50), color_rect, 3)
                                colored_square = color_rect
                                selected_color = colori[i][j]
                                r, g, b = selected_color[0], selected_color[1], selected_color[2]
                                selected = True
                                selected_color_coord = i, j

                # Check if mouse is clicked on the sliders
                elif 960 <= mp[0] <= 1218:
                    if 400 <= mp[1] <= 420:
                        r = get_slider_value(mp[0], 960)
                    elif 450 <= mp[1] <= 470:
                        g = get_slider_value(mp[0], 960)
                    elif 500 <= mp[1] <= 520:
                        b = get_slider_value(mp[0], 960)
                    selected_color = (r, g, b)
                    if selected:
                        colori[selected_color_coord[0]][selected_color_coord[1]] = selected_color
                        draw.rect(screen, selected_color, colored_square)
                        draw.rect(screen, (50, 50, 50), colored_square, 3)

            

    # draw everything
    display.flip()
    clock.tick(144)

quit()
