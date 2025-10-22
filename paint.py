#region IMPORTS
import pygame
from os import path, makedirs
from glob import glob
from tkinter import Tk, filedialog, messagebox
from copy import deepcopy
from PIL import Image
#endregion

#region FUNCTIONS
# Opens a dialog to save
def select_save_file():
    """Opens a file explorer to select folder and enter file name."""
    root = Tk()
    root.withdraw()  # Nasconde la finestra principale
    file_path = filedialog.asksaveasfilename(
        title="Save as",
        defaultextension=".png",  # o altra estensione di default
        filetypes=[("Image files", "*.png"), ("All files", "*.*")]
    )
    root.destroy()
    return file_path

# makes you choose an image from the computer
def select_image():
    # Create a Tkinter root window (it will be hidden)
    root = Tk()
    root.withdraw()  # Hide the root window
        
    image_extensions = tuple(Image.registered_extensions().keys())

    # Open file dialog to select an image file
    file_path = filedialog.askopenfilename(
        title="Select an image file",
        filetypes=[("Image files", image_extensions)]
    )

    # Check if a file was selected
    if not file_path:
        root.iconify()
        root.destroy()
        return None

    # If the selected file is not a PNG, convert it to PNG
    if file_path.lower().endswith(image_extensions) and file_path.lower().endswith('.png'):
        # Open the image
        image = Image.open(file_path)
        # Change the file extension to .png
        png_file_path = file_path.rsplit('.', 1)[0] + '.png'
        # Save the image as a PNG
        image.save(png_file_path, 'PNG')
        # Return the path to the PNG file
        root.iconify()
        root.destroy()
        return png_file_path
    else:
        # If the selected file is already a PNG, return its path
        root.iconify()
        root.destroy()
        return file_path

# Asks if the user wants to quit
def ask_yes_no():
    answer = messagebox.askyesno(message="Do you want to quit?")
    if answer:
        return False
    else:
        return True

def display_image(screen, file_path):
    reset()

    img = pygame.image.load(file_path)

    # Dimensioni originali dell'immagine
    img_width, img_height = img.get_size()

    # Altezza target
    target_height = 720
    scale_ratio = target_height / img_height
    new_width = int(img_width * scale_ratio)
    new_height = target_height

    # Scala l'immagine
    img = pygame.transform.scale(img, (new_width, new_height))

    # Dimensioni della finestra
    win_width, win_height = screen.get_size()

    # Posizione per centrare l'immagine
    x = (win_width - new_width) // 2
    y = (win_height - new_height) // 2

    screen.blit(img, (x, y))

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
def drawRainbow(screen, rainbowFlag):
    """Draws rainbow icon."""
    if rainbowFlag:
        for i, color in enumerate([(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (238, 130, 238)]):
            pygame.draw.circle(screen, color, (100, 690), 80 - i * 10, width=10, draw_top_right=True, draw_top_left=True)
    else:
        pygame.draw.rect(screen, (150,150,150), (20,610, 160, 80))

# Function to draw fill tool icon
def drawBucket(screen, bucketFlag, selectedColor):
    """Draws fill tool icon."""
    if bucketFlag:
        pygame.draw.rect(screen, (50,50,50), (50, 610, 100, 80), border_radius=5)
        pygame.draw.polygon(screen, selectedColor, ((55,615), (145,615),(120, 635),(100, 640), (80, 635)))
    else:
        pygame.draw.rect(screen, (150,150,150), (20,610, 160, 80))

# Draws color palette
def drawPalette(screen, color, dict, selected):
    """Draws color palette."""
    global color_value
    pygame.draw.rect(screen, (150,150,150), (0,0, 200, SCREEN_Y-50))
    for x in range(2):
        for y in range(6):
            coord = (5+(100*x),5+(100*y), 90, 90)
            if (x*100,y*100) == selected:
                pygame.draw.rect(screen, (50,50,50), ((100*x),(100*y), 100, 100))
            pygame.draw.rect(screen, color[x][y], coord)
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
        pygame.draw.circle(screen, color, (x, y), radius)

# Draws the radius selection circles
def selectRadius(screen, selected):
    """Draws the radius selection circles."""
    pygame.draw.rect(screen, (50, 50, 50), (SCREEN_X-250, SCREEN_Y - 50, SCREEN_X, 50))
    colori = [(255,255,255),(255,255,255),(255,255,255)]
    colori.insert(selected, (0,0,0))
    colori_bordo = [(0,0,0),(0,0,0),(0,0,0)]
    colori_bordo.insert(selected, (255,255,255))
    centri = []
    for i in range(4):
        rad = (i+2)*2
        pygame.draw.circle(screen, colori[i], ((SCREEN_X-200)+50*i,(SCREEN_Y-25)), rad)
        pygame.draw.circle(screen, colori_bordo[i], ((SCREEN_X-200)+50*i,(SCREEN_Y-25)), rad+1, 2)
        centri.append(((SCREEN_X-200)+50*i,SCREEN_Y-25))
    return (selected+2)*2, centri

# Draws the toolbar on the bottom
def draw_toolbar(listaBlit):
    """Draws the toolbar on the bottom."""
    pygame.draw.rect(screen, (50, 50, 50), (0, SCREEN_Y - 50, SCREEN_X-250, 50))

    for i, text in enumerate(listaBlit):
        text_rect = text.get_rect()
        if i < 5:
            rect = pygame.Rect(5+i*100, SCREEN_Y - 50 + 5, 90, 40)
        else:
            rect = pygame.Rect(505 + (i-5)*50, SCREEN_Y - 50 + 5, 45, 40)
        text_rect.center = rect.center
        pygame.draw.rect(screen, (200, 200, 200), rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)
        screen.blit(text, text_rect)

# Resets the screen and tools to default state
def reset():
    """Resets the screen and tools to default state."""
    global colore, radius, rainbowStatus, bucketStatus, colorePrec, selectedPaletteCoord, listText, colori, new_colori
    palette = {}
    selectedPaletteCoord = (0,0)
    screen.fill(background)
    drawPalette(screen, colori, palette, selectedPaletteCoord)
    draw_toolbar(listText)
    colore = (0,0,0)
    radius = selectRadius(screen, 2)[0]
    rainbowStatus = False
    bucketStatus = False
    pygame.mouse.set_cursor(pygame.Cursor(0))
    colorePrec = None

# Flood fill algorithm to fill an area with a color
def floodFill(surface, position, fill_color):
    """Fast scanline flood fill algorithm for Pygame surfaces."""
    pygame.mouse.set_cursor(2)
    arr = pygame.surfarray.pixels2d(surface)
    x, y = position
    w, h = arr.shape
    orig_color = arr[x, y]
    fill_color_mapped = surface.map_rgb(fill_color)

    if orig_color == fill_color_mapped:
        pygame.mouse.set_cursor(pygame.Cursor(11))
        return

    stack = [(x, y)]
    while stack:
        nx, ny = stack.pop()
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if arr[nx, ny] != orig_color:
            continue

        west = nx
        east = nx

        # Move west as far as we can and fill
        while west > 0 and arr[west - 1, ny] == orig_color:
            west -= 1
        # Move east as far as we can and fill
        while east < w - 1 and arr[east + 1, ny] == orig_color:
            east += 1

        # Fill the scanline and queue north/south neighbors
        for i in range(west, east + 1):
            arr[i, ny] = fill_color_mapped
            if ny > 0 and arr[i, ny - 1] == orig_color:
                stack.append((i, ny - 1))
            if ny < h - 1 and arr[i, ny + 1] == orig_color:
                stack.append((i, ny + 1))

    pygame.surfarray.blit_array(surface, arr)
    pygame.mouse.set_cursor(pygame.Cursor(11))

# Toggles rainbow mode
def toggleRainbow(bucketFlag, rainbowFlag):
    """Toggles rainbow mode."""
    global color_value, colore, colorePrec
    if bucketFlag:
        pygame.mouse.set_cursor(pygame.Cursor(0))
        bucketFlag = False
        drawBucket(screen, bucketFlag, colore)
    if not rainbowFlag:
        rainbowFlag = True
    else:
        rainbowFlag = False
        color_value = 0
        if colorePrec:
            colore = colorePrec
            colorePrec = None
    drawRainbow(screen, rainbowFlag)
    return bucketFlag, rainbowFlag

# Toggles fill bucket mode
def toggleBucket(bucketFlag, rainbowFlag):
    """Toggles fill bucket mode."""
    global colore, colorePrec
    if rainbowFlag:
        rainbowFlag = False
        colore = colorePrec
        drawRainbow(screen, rainbowFlag)
    if not bucketFlag:
        bucketFlag = True
        pygame.mouse.set_cursor(pygame.Cursor(11))
    else:
        bucketFlag = False
        pygame.mouse.set_cursor(pygame.Cursor(0))
    drawBucket(screen, bucketFlag, colore)
    return bucketFlag, rainbowFlag

# Changes the size of the drawing tool
def changeSize(mp):
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
    global tastoUndo, tastoRedo, listText
    sshot = save_canvas(screen, pygame.Rect(200, 0, SCREEN_X-200, SCREEN_Y-50))
    list_append.append(sshot)
    pixArray = pygame.surfarray.pixels2d(list_pop[-1])
    list_pop.pop(-1)
    pygame.surfarray.blit_array(screen.subsurface(pygame.Rect(200, 0, SCREEN_X-200, SCREEN_Y-50)), pixArray)
    if UR: #undo
        tastoRedo = myfont.render('↪', True, (50,50,50))
        if not list_pop:
            tastoUndo = myfont.render('↩', True, (150,150,150))
    else:
        tastoUndo = myfont.render('↩', True, (50,50,50))
        if not list_pop:
            tastoRedo = myfont.render('↪', True, (150,150,150))
    listText = [salva,  apri,cancella, riempi, arcobaleno, tastoUndo, tastoRedo, tastoPicker]
    draw_toolbar(listText)

# Draw slider in the color picker
def draw_slider(screen, x, y, value, color):
    """Draw a slider bar with the given value and color."""
    pygame.draw.rect(screen, (255, 255, 255), (x, y, 258, 20))  # Background
    pygame.draw.rect(screen, (0, 0, 0), (x, y, 258, 20), 2)    # Border
    pygame.draw.rect(screen, color, (x + 1, y + 1, value, 18)) # Value fill

# Animates the slider
def get_slider_value(mouse_x, slider_x):
    """Calculate the slider value based on mouse position."""
    return max(0, min(255, mouse_x - slider_x))

# Builds the color picker
def buildColorPicker(window, colori:list, selected_color, selected):
    """Build the color picker interface."""
    myfont = pygame.font.SysFont("segoeuisymbol", 30)
    window.blit(colorPickerGrid, (0, 0))  # Display the color grid image

    pygame.draw.rect(window, (50, 50, 50), (720, 0, 360, 720))  # Sidebar background

    save = myfont.render('SAVE', True, (0, 0, 0))
    save_rect = save.get_rect()
    save_bg = pygame.Rect(725, 650, 90, 50)
    save_rect.center = save_bg.center
    pygame.draw.rect(window, (150, 150, 150), save_bg)  # Save button
    pygame.draw.rect(window, (0, 0, 0), save_bg, 2)
    window.blit(save, save_rect)

    cancel = myfont.render('CANCEL', True, (0, 0, 0))
    cancel_rect = cancel.get_rect()
    cancel_bg = pygame.Rect(950, 650, 125, 50)
    cancel_rect.center = cancel_bg.center
    pygame.draw.rect(window, (150, 150, 150), cancel_bg)  # Cancel button
    pygame.draw.rect(window, (0, 0, 0), cancel_bg, 2)
    window.blit(cancel, cancel_rect)

    pygame.draw.rect(window, (150, 150, 150), (725, 105, 350, 118))  # Color preview area
   
    def_pal = myfont.render('DEFAULT PALETTE', True, (0, 0, 0))
    def_pal_rect = def_pal.get_rect()
    def_pal_bg = pygame.Rect(750, 250, 300, 50)
    def_pal_rect.center = def_pal_bg.center
    pygame.draw.rect(window, (150, 150, 150), def_pal_bg)
    pygame.draw.rect(window, (0, 0, 0), def_pal_bg, 2)
    window.blit(def_pal, def_pal_rect)

    pygame.draw.rect(window, selected_color, (725, 5, 350, 90))  # Selected color display

    draw_slider(window, 760, 400, r, (255, 0, 0))  # Red slider
    draw_slider(window, 760, 450, g, (0, 255, 0))  # Green slider
    draw_slider(window, 760, 500, b, (0, 0, 255))  # Blue slider

    window.blit(myfont.render('R', True, (0, 0, 0)), (730, 385))
    window.blit(myfont.render('G', True, (0, 0, 0)), (730, 435))
    window.blit(myfont.render('B', True, (0, 0, 0)), (730, 485))

    text_r = (myfont.render(f'{r}', True, (0, 0, 0)))
    r_rect = text_r.get_rect()
    r_bg = pygame.Rect(1020, 390, 60, 40)
    r_rect.center = r_bg.center

    text_g = (myfont.render(f'{g}', True, (0, 0, 0)))
    g_rect = text_g.get_rect()
    g_bg = pygame.Rect(1020, 440, 60, 40)
    g_rect.center = g_bg.center

    text_b = (myfont.render(f'{b}', True, (0, 0, 0)))
    b_rect = text_b.get_rect()
    b_bg = pygame.Rect(1020, 490, 60, 40)
    b_rect.center = b_bg.center

    pygame.draw.rect(window, (150, 50, 50), r_bg, border_radius=15)  # Red value box
    pygame.draw.rect(window, (0,0,0), r_bg, border_radius=15, width=2)
    pygame.draw.rect(window, (50, 150, 50), g_bg, border_radius=15)  # Green value box
    pygame.draw.rect(window, (0,0,0), g_bg, border_radius=15, width=2)
    pygame.draw.rect(window, (50, 50, 150), b_bg, border_radius=15)  # Blue value box
    pygame.draw.rect(window, (0,0,0), b_bg, border_radius=15, width=2)

    window.blit(text_r, r_rect)
    window.blit(text_g, g_rect)
    window.blit(text_b, b_rect)

    for j in range(len(colori[0])):
        for i in range(len(colori)):
            color_rect = pygame.Rect(730 + 58 * j, 110 + 58 * i, 50, 50)
            if selected:
                if colori[i][j] == selected_color:
                    colori[selected_color_coord[0]][selected_color_coord[1]] = selected_color
                    pygame.draw.rect(window, selected_color, color_rect)
                    pygame.draw.rect(window, (50, 50, 50), color_rect, 3)
                else:
                    pygame.draw.rect(window, colori[i][j], color_rect)
            else:
                pygame.draw.rect(window, colori[i][j], color_rect)

    return colori, selected_color, selected_color_coord

# Handles the shortcut buttons
def shortcut(event):
    """Handles the shortcut buttons"""
    global picking, bucketStatus, rainbowStatus, screenshotsRedo, screenshotsUndo, radius, beforePick

    mods = pygame.key.get_mods()

    # rgb SPACE
    if event.key == pygame.K_SPACE and not picking:
        bucketStatus, rainbowStatus = toggleRainbow(bucketStatus, rainbowStatus)
        
    # fill B
    elif event.key == pygame.K_b and not picking:
        bucketStatus, rainbowStatus = toggleBucket(bucketStatus, rainbowStatus)

     # Undo (Ctrl+Z) / Redo (Ctrl+Shift+Z)
    elif event.key == pygame.K_z and (mods & pygame.KMOD_CTRL) and not picking:
        if mods & pygame.KMOD_SHIFT:
            if screenshotsRedo:
                undoRedo(screen, screenshotsRedo, screenshotsUndo, False)  # Redo
        elif screenshotsUndo:
            undoRedo(screen, screenshotsUndo, screenshotsRedo, True)       # Undo
            
    # picker P
    elif event.key == pygame.K_p:
        if bucketStatus:
            bucketStatus, rainbowStatus = toggleBucket(bucketStatus, rainbowStatus)
        elif rainbowStatus:
            bucketStatus, rainbowStatus = toggleRainbow(bucketStatus, rainbowStatus)
        if not picking:
            beforePick = save_canvas(screen, pygame.Rect(200, 0, SCREEN_X-200, SCREEN_Y-50))
            buildColorPicker(screen.subsurface(200,0,1080,720), colori, (255,255,255), selected)
            picking = True
        else:
            picking = False
            pygame.mouse.set_cursor(0)
            screen.blit(beforePick, pygame.Rect(200, 0, SCREEN_X-200, SCREEN_Y-50))

    # increase size +
    elif event.key == pygame.K_PLUS:
        if (radius//2)-2 < 3:
            radius = selectRadius(screen, (radius//2)-2 +1)[0]

    # decrease size -     
    elif event.key == pygame.K_MINUS:
        if (radius//2)-2 > 0:
            radius = selectRadius(screen, (radius//2)-2 -1)[0]

def mousePressed():
    global colore, colorePrec, selectedPaletteCoord, saving, bucketStatus, rainbowStatus, picking, screenshot 
    global drawings_folder, screenshotsUndo, screenshotsRedo, flagUndo, tastoUndo, tastoRedo, listText, selected_image
    global salva, apri, cancella, riempi, arcobaleno, tastoPicker, SCREEN_X, SCREEN_Y, coordPalette, colori, beforePick

    # click change color
    if 0 <= mp[0] <= 200 and 0 <= mp[1] <= SCREEN_Y-50 and not saving and not rainbowStatus and not picking:
        for k in coordPalette:
            if k[0] <= mp[0] <= k[1] and k[2] <= mp[1] <= k[3]:
                
                colore = coordPalette[k]
                colorePrec = colore
                selectedPaletteCoord = (k[0]-5,k[2]-5)
                drawPalette(screen, colori, coordPalette, selectedPaletteCoord)
                if bucketStatus:
                    drawBucket(screen, bucketStatus, colore)

    # click save
    elif 5 <= mp[0] <= 95 and SCREEN_Y-50+5 <= mp[1] <= SCREEN_Y-5 and not picking:
        saving = True
        screenshot = screen.subsurface(pygame.Rect(200, 0, SCREEN_X-200, SCREEN_Y-50))
        save_path = select_save_file()
        try:
            pygame.image.save(screenshot, save_path)
        except pygame.error:
            makedirs(drawings_folder)
            pygame.image.save(screenshot, save_path)
        saving = False
    
    # click open
    elif 105 <= mp[0] <= 195 and SCREEN_Y-50+5 <= mp[1] <= SCREEN_Y-5 and not saving and not picking:
        selected_image = select_image()
        if selected_image:
            if not flagUndo:
                screenshot = save_canvas(screen, pygame.Rect(200, 0, SCREEN_X-200, SCREEN_Y-50))
                screenshotsUndo.append(screenshot)
                screenshotsRedo = []
                flagUndo = True
                tastoUndo = myfont.render('↩', True, (50,50,50))
                tastoRedo = myfont.render('↪', True, (150,150,150))
                listText = [salva,  apri,cancella, riempi, arcobaleno, tastoUndo, tastoRedo, tastoPicker]
                draw_toolbar(listText)
                if len(screenshotsUndo) > 20:
                    screenshotsUndo.pop(0)
            display_image(screen.subsurface(pygame.Rect(200, 0, SCREEN_X-200, SCREEN_Y-50)),selected_image)

    # click canc 
    elif 205 <= mp[0] <= 295 and SCREEN_Y-50+5 <= mp[1] <= SCREEN_Y-5 and not saving and not picking:
        screenshot = save_canvas(screen, pygame.Rect(200, 0, SCREEN_X-200, SCREEN_Y-50))
        screenshotsUndo.append(screenshot)
        screenshotsRedo = []
        tastoUndo = myfont.render('↩', True, (50,50,50))
        tastoRedo = myfont.render('↪', True, (150,150,150))
        listText = [salva,  apri,cancella, riempi, arcobaleno, tastoUndo, tastoRedo, tastoPicker]
        reset()

    # click fill
    elif 305 <= mp[0] <= 395 and SCREEN_Y - 50 < mp[1] < SCREEN_Y - 10 and not saving and not picking:
        bucketStatus, rainbowStatus = toggleBucket(bucketStatus, rainbowStatus)

    # click rgb
    elif 405 <= mp[0] <= 495 and SCREEN_Y - 50 < mp[1] < SCREEN_Y - 10 and not saving and not picking:
        bucketStatus, rainbowStatus = toggleRainbow(bucketStatus, rainbowStatus)
    
    # click undo
    elif 505 <= mp[0] <= 550 and SCREEN_Y - 50 < mp[1] < SCREEN_Y - 10 and not saving and not picking:
        if screenshotsUndo:
            undoRedo(screen, screenshotsUndo, screenshotsRedo, True)

    # click redo
    elif 555 <= mp[0] <= 600 and SCREEN_Y - 50 < mp[1] < SCREEN_Y - 10 and not saving and not picking:
        if screenshotsRedo:
                undoRedo(screen, screenshotsRedo, screenshotsUndo, False)

    # click color picker
    elif 605 <= mp[0] <= 650 and SCREEN_Y - 50 < mp[1] < SCREEN_Y - 10 and not saving and not picking:
        if bucketStatus:
            bucketStatus, rainbowStatus = toggleBucket(bucketStatus, rainbowStatus)
        elif rainbowStatus:
            bucketStatus, rainbowStatus = toggleRainbow(bucketStatus, rainbowStatus)
        beforePick = save_canvas(screen, pygame.Rect(200, 0, SCREEN_X-200, SCREEN_Y-50))
        buildColorPicker(screen.subsurface(200,0,1080,720), colori, (255,255,255), selected)
        picking = True

    # click circles to change size
    elif mp[1] > SCREEN_Y-50 and not picking:
        changeSize(mp)
#endregion

#region VARIABLES
# Initialize Pygame
pygame.init()

# Initialize screen size and font
SCREEN_X, SCREEN_Y = 1280, 770 
myfont = pygame.font.SysFont("segoeuisymbol", 30)

# Initialize the text of the UI
salva = myfont.render('SAVE', True, (50,50,50))
apri = myfont.render('OPEN', True, (50,50,50))
cancella = myfont.render('CANC', True, (50,50,50))
riempi = myfont.render('FILL', True, (50,50,50))
arcobaleno = myfont.render('RGB', True, (50,50,50))
tastoUndo = myfont.render('↩', True, (150,150,150))
tastoRedo = myfont.render('↪', True, (150,150,150))
tastoPicker = myfont.render('🎨', True, (50,50,50))
listText = [salva, apri, cancella, riempi, arcobaleno, tastoUndo, tastoRedo, tastoPicker]

# Define color palette
colori = [[(0, 0, 0),(255, 0, 0),(0, 255, 0),(0, 0, 255),(165, 42, 42),(255, 165, 0)],
          [(255, 255, 255),(255, 0, 255),(255, 255, 0),(0, 255, 255),(128, 0, 128),(255, 192, 203)]]
new_colori = deepcopy(colori)
default_colori = deepcopy(colori)

# flags and starting conditions
coordPalette = {}
running = True
saving = False
colore = (0,0,0)
colorePrec = None
last_pos = None
color_value = 0
rainbowStatus = False
bucketStatus = False
selectedPaletteCoord = (0,0)
clock = pygame.time.Clock()
flagUndo = False
screenshotsUndo = []
screenshotsRedo = []
try:
    colorPickerGrid = pygame.image.load("picker/color_grid.png")
except FileNotFoundError:
    colorPickerGrid = pygame.image.load("Python Paint/picker/color_grid.png")
colorPickerGrid_rect = colorPickerGrid.get_rect(topleft=(200, 0))
selected_color = (255, 255, 255)
r, g, b = selected_color[0], selected_color[1], selected_color[2]
selected_color_coord = 0,0
picking = False
selected = False
onPicker = False
onSliders = False
defaultPalette = False
wait = 0

# Set up the display
pygame.display.set_caption("PAINT IN PYTHON")
screen = pygame.display.set_mode([SCREEN_X, SCREEN_Y], pygame.DOUBLEBUF)
background = (255, 255, 255)
screen.fill(background)
drawPalette(screen, colori, coordPalette, selectedPaletteCoord)
draw_toolbar(listText)

# Radius selection
radius, centri = selectRadius(screen, 2)
#endregion

#region MAIN LOOP
while running:
    # get mouse position
    mp = pygame.mouse.get_pos()
    if picking:
        if 200 < mp[0] < 920 and mp[1] < 720:
            pygame.mouse.set_cursor(3)
        else:
            pygame.mouse.set_cursor(0)
    #check events
    for e in pygame.event.get():

        # quit
        if e.type == pygame.QUIT:
            running = ask_yes_no()

        # press button on keyboard
        if e.type == pygame.KEYDOWN:
            shortcut(e)

        # draw + fill
        if pygame.mouse.get_pressed()[0] and not saving and not picking:
            if mp[0] > 200 - radius and mp[1] < SCREEN_Y-50 + radius and wait == 0:
                if not flagUndo:
                    screenshot = save_canvas(screen, pygame.Rect(200, 0, SCREEN_X-200, SCREEN_Y-50))
                    screenshotsUndo.append(screenshot)
                    screenshotsRedo = []
                    flagUndo = True
                    tastoUndo = myfont.render('↩', True, (50,50,50))
                    tastoRedo = myfont.render('↪', True, (150,150,150))
                    listText = [salva,  apri,cancella, riempi, arcobaleno, tastoUndo, tastoRedo, tastoPicker]
                    draw_toolbar(listText)
                    if len(screenshotsUndo) > 20:
                        screenshotsUndo.pop(0)

                if not bucketStatus:
                    if rainbowStatus:
                        if not colorePrec:
                            colorePrec = colore
                        color_value = (color_value + 8) % (256 * 6)
                        colore = rainbowColor(color_value)
                    else:
                        if colorePrec:
                            colore = colorePrec
                            colorePrec = None
                    pygame.draw.circle(screen, colore, mp, radius)
                    
                    draw_toolbar(listText)
                    selectRadius(screen, (radius//2)-2)
                    drawPalette(screen, colori, coordPalette, selectedPaletteCoord)

                    if rainbowStatus:
                        drawRainbow(screen, True)
                    elif bucketStatus:
                        drawBucket(screen, True, colore)
                    if last_pos:
                        roundLine(screen, colore, mp, last_pos, radius)


                    last_pos = mp
                else:
                    try:
                        if screen.get_at(mp)[:3] != colore and not rainbowStatus and mp[0] > 200 and mp[1] < SCREEN_Y-50:
                            floodFill(screen, mp, colore)
                    except:
                        pass
            else:
                # click outside canvas
                last_pos = None

        # release mouse
        if e.type == pygame.MOUSEBUTTONUP:
            last_pos = None
            color_value = 0
            flagUndo = False

        # click buttons
        if e.type == pygame.MOUSEBUTTONDOWN:
            mousePressed()

        if picking:      
            new_colori, nuovo_colore, coord_colore = buildColorPicker(screen.subsurface(200,0,1080,720), colori, selected_color, selected)  

            if e.type == pygame.MOUSEBUTTONDOWN:

                # Click Save or Quit
                if 650 <= mp[1] <= 700:

                    # Click Save Button
                    if 925 <= mp[0] <= 1015:
                        colori = deepcopy(new_colori)
                        coordPalette = {}
                        drawPalette(screen, colori, coordPalette, selectedPaletteCoord)
                        selected = False
                        selected_color = (255, 255, 255)
                        if colore not in colori[0] and colore not in colori[1]:
                            colore =  nuovo_colore
                        pygame.mouse.set_cursor(0)
                        screen.blit(beforePick, pygame.Rect(200, 0, SCREEN_X-200, SCREEN_Y-50))
                        picking = False
                        wait = 30

                    # Click Quit Button
                    elif 1150 <= mp[0] <=1275:
                        colori = deepcopy(default_colori)
                        selected = False
                        pygame.mouse.set_cursor(0)
                        if (defaultPalette):
                            colori = deepcopy(undo_default_colori)
                            colore = colori[coord_colore[0]][coord_colore[1]]
                            selected_color = (255, 255, 255)
                        drawPalette(screen, colori, coordPalette, selectedPaletteCoord)
                        screen.blit(beforePick, pygame.Rect(200, 0, SCREEN_X-200, SCREEN_Y-50))
                        picking = False
                        wait = 30

                # Click Default Palette
                elif 250 <= mp[1] <= 300 and 950 <= mp[0] <= 1250:

                    undo_default_colori = deepcopy(colori)
                    colori = deepcopy(default_colori)
                    new_colori = deepcopy(colori)
                    coordPalette = {}
                    drawPalette(screen, colori, coordPalette, selectedPaletteCoord)
                    colore = colori[coord_colore[0]][coord_colore[1]]
                    selected_color = colore
                    r, g, b = selected_color[0], selected_color[1], selected_color[2]
                    selected = False
                    defaultPalette = True

                # Check if mouse is clicked within color palette squares
                elif 110 <= mp[1] <= 220 and 930 <= mp[0] <= 1270:
                    for j in range(len(colori[0])):
                        for i in range(len(colori)):
                            color_rect = pygame.Rect(930 + 58 * j, 110 + 58 * i, 50, 50)
                            pygame.draw.rect(screen, colori[i][j], color_rect)
                            if color_rect.collidepoint(mp):
                                selected_square = pygame.draw.rect(screen, (50, 50, 50), color_rect, 3)
                                colored_square = color_rect
                                selected_color = colori[i][j]
                                colorePrec = None
                                r, g, b = selected_color[0], selected_color[1], selected_color[2]
                                selected = True
                                selected_color_coord = i, j
 
            # mouse + movement
            elif pygame.mouse.get_pressed()[0] and (e.type == pygame.MOUSEMOTION and e.buttons[0] == 1):
                # Check if mouse is dragged while clicked within the image rect
                if colorPickerGrid_rect.collidepoint(mp[0],mp[1]) and not onSliders:
                    onPicker = True
                    # Get the color of the pixel at the mouse position
                    selected_color = colorPickerGrid.get_at((mp[0] - colorPickerGrid_rect.x, mp[1] - colorPickerGrid_rect.y))
                    r, g, b = selected_color[0], selected_color[1], selected_color[2]
                    if selected:
                        colori[selected_color_coord[0]][selected_color_coord[1]] = selected_color
                        pygame.draw.rect(screen, selected_color, colored_square)
                        pygame.draw.rect(screen, (50, 50, 50), colored_square, 3)

                # Check if mouse is clicked on the sliders
                elif 960 <= mp[0] <= 1218 and not onPicker and not (250 <= mp[1] <= 300):
                    onSliders = True
                    if 400 <= mp[1] <= 420:
                        r = get_slider_value(mp[0], 960)
                    elif 450 <= mp[1] <= 470:
                        g = get_slider_value(mp[0], 960)
                    elif 500 <= mp[1] <= 520:
                        b = get_slider_value(mp[0], 960)
                    selected_color = (r, g, b)
                    if selected:
                        colori[selected_color_coord[0]][selected_color_coord[1]] = selected_color
                        pygame.draw.rect(screen, selected_color, colored_square)
                        pygame.draw.rect(screen, (50, 50, 50), colored_square, 3)

            if e.type == pygame.MOUSEBUTTONUP:
                onPicker = False
                onSliders = False

            

    # draw everything
    pygame.display.flip()
    clock.tick(144)
    if (wait > 0):
        wait -= 1

quit()
#endregion