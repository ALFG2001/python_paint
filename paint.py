from pygame import * 
import os
import glob

def count_files_by_type(folder_path, file_extension):
    # Construct the search pattern
    search_pattern = os.path.join(folder_path, f"*.{file_extension}")

    # Use glob to find files matching the pattern
    files = glob.glob(search_pattern)

    # Count the number of files found
    count = len(files)+1

    return count

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

def drawRainbow(schermo, r):
    if r:
        draw.circle(schermo, (255, 0, 0), (100,690), 80, width=10 , draw_top_right=True, draw_top_left=True)
        draw.circle(schermo, (255, 165, 0), (100,690), 70, width=10 , draw_top_right=True, draw_top_left=True)
        draw.circle(schermo, (255, 255, 0), (100,690), 60, width=10 , draw_top_right=True, draw_top_left=True)
        draw.circle(schermo, (0, 255, 0), (100,690), 50, width=10 , draw_top_right=True, draw_top_left=True)
        draw.circle(schermo, (0, 0, 255), (100,690), 40, width=10 , draw_top_right=True, draw_top_left=True)
        draw.circle(schermo, (75, 0, 130), (100,690), 30, width=10 , draw_top_right=True, draw_top_left=True)
        draw.circle(schermo, (238, 130, 238),(100,690), 20, width=10 , draw_top_right=True, draw_top_left=True)
    else:
        draw.rect(schermo, (150,150,150), (20,610, 160, 80))

def drawBucket(schermo, b, c):
    if b:
        draw.rect(schermo, (50,50,50), (50, 610, 100, 80), border_radius=5)
        draw.polygon(schermo, c, ((55,615), (145,615),(120, 635),(100, 640), (80, 635)))
    else:
        draw.rect(schermo, (150,150,150), (20,610, 160, 80))

def drawPalette(schermo, color, dict, selected):
    global color_value
    draw.rect(schermo, (150,150,150), (0,0, 200, SCREEN_Y-50))
    for x in range(2):
        for y in range(6):
            coord = (5+(100*x),5+(100*y), 90, 90)
            if (x*100,y*100) == selected:
                draw.rect(schermo, (50,50,50), ((100*x),(100*y), 100, 100))
            draw.rect(schermo, color[x][y], coord)
            dict[(coord[0],coord[0]+90, coord[1], coord[1]+90)] = color[x][y]
    
def roundLine(schermo, color, start, end, radius=1):
    Xaxis = end[0]-start[0]
    Yaxis = end[1]-start[1]
    dist = max(abs(Xaxis), abs(Yaxis))
    for i in range(dist):
        x = int(start[0]+float(i)/dist*Xaxis)
        y = int(start[1]+float(i)/dist*Yaxis)
        draw.circle(schermo, color, (x, y), radius)

def selectRadius(schermo, selected):
    colori = [(255,255,255),(255,255,255),(255,255,255)]
    colori.insert(selected, (0,0,0))
    centri = []
    for i in range(4):
        rad = (i+2)*2
        draw.circle(schermo, colori[i], ((SCREEN_X-200)+50*i,(SCREEN_Y-25)), rad)
        centri.append(((SCREEN_X-200)+50*i,SCREEN_Y-25))
    return (selected+2)*2, centri

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

def fill(surface, position, fill_color):
    fill_color = surface.map_rgb(fill_color)  # Convert the color to mapped integer value.
    surf_array = surfarray.pixels2d(surface)  # Create an array from the surface.
    current_color = surf_array[position]  # Get the mapped integer color value.

    # 'frontier' is a list where we put the pixels that's we haven't checked. Imagine that we first check one pixel and 
    # then expand like rings on the water. 'frontier' are the pixels on the edge of the pool of pixels we have checked.
    #
    # During each loop we get the position of a pixel. If that pixel contains the same color as the ones we've checked
    # we paint it with our 'fill_color' and put all its neighbours into the 'frontier' list. If not, we check the next
    # one in our list, until it's empty.

    frontier = [position]
    while len(frontier) > 0:
        x, y = frontier.pop()
        try:  # Add a try-except block in case the position is outside the surface.
            if surf_array[x, y] != current_color:
                continue
        except IndexError:
            continue
        surf_array[x, y] = fill_color
        # Then we append the neighbours of the pixel in the current position to our 'frontier' list.
        frontier.append((x + 1, y))  # Right.
        frontier.append((x - 1, y))  # Left.
        frontier.append((x, y + 1))  # Down.
        frontier.append((x, y - 1))  # Up.

    surfarray.blit_array(surface, surf_array)

init()

SCREEN_X, SCREEN_Y = 1280, 750 
myfont = font.SysFont("monospace", 30)
salva = myfont.render('SAVE', True, (50,50,50))
cancella = myfont.render('CANC', True, (50,50,50))
riempi = myfont.render('FILL', True, (50,50,50))
arcobaleno = myfont.render('RGB', True, (50,50,50))

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

r, centri = selectRadius(screen, 2)
while running:
    
    mp = mouse.get_pos()
    for e in event.get():
        if e.type == QUIT:
            running = False

        if e.type == KEYDOWN:
            if e.key == K_SPACE:
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

            if e.key == K_b:
                if rainbow:
                    rainbow = False
                    drawRainbow(screen, rainbow)
                if bucket:
                    bucket = False
                    mouse.set_cursor(Cursor(0))   
                else:
                    bucket = True
                    mouse.set_cursor(Cursor(11))
                drawBucket(screen, bucket, colore)              

        if mouse.get_pressed()[0]:# and 305 >= mp[0] > 395 + r and SCREEN_Y-50 < mp[1] < SCREEN_Y-10 and not saving:
            pass

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
                    fill(screen,mp,colore)

  
        if mouse.get_pressed()[0] and not (mp[0] > 200 + r and mp[1]) < SCREEN_Y-50 - r and not saving:
            last_pos = None
            
        if e.type == MOUSEBUTTONUP:
            last_pos = None
            color_value = 0

        if e.type == MOUSEBUTTONDOWN:
            if  0 <= mp[0] <= 200 and not saving and not rainbow:
                
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
                            image.save(screenshot, f"paint\{count}-screenshot.png")
                            print(f"Saved as {count}-screenshot")
                        else:
                            image.save(screenshot, f"paint\{count}-screenshot.png")
                            print(f"Saved as {count}-screenshot")

                    else:
                        image.save(screenshot, f"paint\{count}-{nome}.png")
                        print(f"Saved as {count}-{nome}")
                    
                    saving = False
                        
                elif 105 <= mp[0] <= 195 and SCREEN_Y-50+5 <= mp[1] <= SCREEN_Y-5 and not saving:
                    reset()

            elif 205 <= mp[0] <= 295 and SCREEN_Y - 50 < mp[1] < SCREEN_Y - 10 and not saving:
                if rainbow:
                    mouse.set_cursor(Cursor(0))
                    rainbow = False
                    drawRainbow(screen, rainbow)
                if not bucket:
                    bucket = True
                else:
                    bucket = False

                drawBucket(screen, bucket, colore)
                

            elif 305 <= mp[0] <= 395 and SCREEN_Y - 50 < mp[1] < SCREEN_Y - 10 and not saving:
                if bucket:
                    mouse.set_cursor(Cursor(0))
                    bucket = False
                    drawBucket(screen, bucket, colore)
                if not rainbow:
                    rainbow = True
                else:
                    rainbow = False
                    color_value = 0
                    colorePrec = None  # Reset colorePrec when exiting rainbow mode

                drawRainbow(screen, rainbow)

            elif mp[1] > SCREEN_Y-50:
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
    display.flip()
    clock.tick(144)
    
quit()