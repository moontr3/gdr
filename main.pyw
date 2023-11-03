#--------------------------------#
#                                #
#    ######  ######    ######    #
#  ##        ##    ##  ##    ##  #
#  ##  ####  ##    ##  ######    #
#  ##    ##  ##    ##  ##  ##    #
#    ####    ######    ##    ##  #
#                                #
#           by moontr3           #
#   https://github.com/moontr3   #
#                                #
#--------------------------------#


############## INITIALIZATION ##############

import pygame as pg
import json
import easing_functions as easing
from mutagen.mp3 import MP3
import time
import random
import glob
import win32api
import win32con
import win32gui
import ctypes
from ctypes import wintypes
import pyautogui
import draw
from pypresence import Presence
import subtitle
import numpy as np
import os

pg.mixer.init()
pg.init()

mode = pg.display.list_modes()[0]
windowx = mode[0]
windowy = mode[1]
transparent = (0,0,0)
clock = pg.time.Clock()
fps = 60

screen = pg.display.set_mode((windowx,windowy), pg.NOFRAME)
running = True
pg.display.set_caption('Loading...')
draw.def_surface = screen

halfx = windowx//2
halfy = windowy//2

# invisible window
hwnd = pg.display.get_wm_info()["window"]
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*transparent), 0, win32con.LWA_COLORKEY)
user32 = ctypes.WinDLL("user32")
user32.SetWindowPos.restype = wintypes.HWND
user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, wintypes.INT, wintypes.INT, wintypes.INT, wintypes.INT, wintypes.UINT]
user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001)


# app functions

# save specified dictionary in json file
def dump(obj, filename='data.json'): 
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=4)

# load data from json file and return it
def load(filename='data.json'): 
    try:
        with open(filename, encoding='utf-8') as f:
            return json.load(f)
    except:
        dump({
            "folder": "songs\\",
            "client_id": "",
            "discord_presence": False,
            "presence_image": "",
            "presence_description": "",
            "fav_boost": 1,
            "remember_last_song": True,
            "song": 'No song',
            "next_song": 'No song',
            "boosted": [],
            "volume": 100
        })
        return load()
    
# loading save data
save_data = load()
volume = save_data['volume']
print(save_data)
print(volume)
pg.mixer.music.set_volume(volume/100)

# save data (just an easier way of dump(save_data))
def save():
    dump(save_data)
    
# convert path to song file into song name
def to_name(string):
    return string.removesuffix('.mp3').removeprefix(folder_path)
    
# convert path to subtitle file into subtitle name
def to_subtitle_name(string):
    return string.removesuffix('.json').removeprefix(folder_path+'subtitles\\')

# convert song name into song file path
def to_path(string):
    return f'{folder_path}{string}.mp3'

# convert subtitle file name into its path
def to_subtitle_path(string):
    return f'{folder_path}subtitles\\{string}.json'

# quit app
def quit():
    global running
    running = False

# hide/show song selector (menu)
def menu():
    global menu_opened
    menu_opened = not menu_opened

# pin bottom bar
def pin():
    global pinned, pin_state
    pinned = not pinned
    pin_state = f"Bar {'un' if not pinned else ''}pinned"
    popup('Bar:', f"{'Unp' if not pinned else 'P'}inned", 50)

# turn on/off remembering of the last song
def remember_last():
    global save_data, remember_last_song_state
    save_data['remember_last_song'] = not save_data['remember_last_song']
    save()
    remember_last_song_state = 'On' if save_data['remember_last_song'] else 'Off'
    popup('Remembering last song:', remember_last_song_state, 100)

# reload songs 
def reload_songs():
    global songs, vis_songs, subtitles

    # load songs
    songs = glob.glob(f"{folder_path}*.mp3")
    subtitles = glob.glob(f"{folder_path}subtitles\\*.json")
    subtitles = [to_subtitle_name(i) for i in subtitles]
    
    # converting songs to only names
    for i in range(len(songs)):
        songs[i] = to_name(songs[i])
    vis_songs = list(songs)

    # boosting fav songs
    for i in save_data['boosted']:
        if i in songs:
            for j in range(save_data['fav_boost']):
                songs.append(i)

# return random song from loaded songs
def generate_random_song():
    try:
        return random.choice(songs)
    except:
        reload_songs()
        try:
            return random.choice(songs)
        except:
            if not os.path.isdir('songs'): os.mkdir('songs')
            return 'We\'ve created a songs folder for you. Please put all your songs in there.'

# rewind
def rewind(timestamp):
    global time_started

    if timestamp < 0 or timestamp > length: return
    
    time_started = time.time()-timestamp
    pg.mixer.music.set_pos(timestamp)
    popup('Rewind', f'{int(timestamp//60)}:{round(timestamp%60,1):0>4}', 60)


# start playing new song
def play_song(path=None):
    global playing, prev, next, song_num, time_started, length, current_subtitle
    reload_songs() # just to be sure

    # choosing song
    prev = playing
    pre_next = generate_random_song()

    if path == None:
        if song_num == 0 and save_data['remember_last_song']:
            if save_data['song'] in songs:
                playing = save_data['song']
            if save_data['next_song'] in songs:
                pre_next = save_data['next_song']
        else:
            playing = next
    else:
        playing = path

    # subtitle
    if playing in subtitles:
        current_subtitle = subtitle.load_from_json(to_subtitle_path(playing))
    else:
        current_subtitle = None

    next = pre_next
    song_num += 1
    try:
        length = MP3(to_path(playing)).info.length
    except:
        length = 260

    # changing info
    pg.display.set_caption(f'#{song_num}: {playing}')
    popup(f'Now playing:', playing)
    save_data['song'] = playing
    save_data['next_song'] = next
    save()

    # discord rich presence
    try:
        RPC.update(
            large_image=save_data['presence_image'] if save_data['presence_image'] != "" else None,
            large_text=f"Song #{song_num} ({int(length//60)}:{int(length%60):0>2})",
            details=save_data['presence_description'] if save_data['presence_description'] != "" else None,
            state=f"{playing}"
        )
    except:
        pass

    # playing song
    pg.mixer.music.stop()

    try:
        pg.mixer.music.load(to_path(playing))
        pg.mixer.music.play()
    except:
        # smash or
        pass
    
    time_started = time.time()

# update volume
def update_vol(y):
    global volume, volume_timer
    print(volume)

    # changing volume
    volume -= -y*2
    if volume < 0: volume = 0
    if volume > 100: volume = 100
    volume_timer = 60

    # updating volume
    pg.mixer.music.set_volume(volume/100)
    popup('Volume:', f'{volume}%', 60)

    dump({
        "folder": "songs\\",
        "client_id": "",
        "discord_presence": False,
        "presence_image": "",
        "presence_description": "",
        "fav_boost": 1,
        "remember_last_song": True,
        "song": 'No song',
        "next_song": 'No song',
        "boosted": [],
        "volume": volume
    })

# display popup
def popup(text, val, time=500):
    global popup_timer, popup_text, popup_val
    popup_timer = time
    popup_text = text
    popup_val = val


# app classes

# quick action button 
class QAButton:
    def __init__(self, action, hover_color, strokes, tooltip, variable=None):
        self.action = action
        self.hover_color = hover_color
        self.strokes = strokes
        self.tooltip = tooltip
        self.variable = variable

    def click(self):
        self.action()


# app variables

folder_path = save_data['folder'].replace('/','\\')
volume = save_data['volume']
playing = None
next = generate_random_song()
song_num = 0
buttons = [
    QAButton(quit, (255,50,50), [(15,15), (35,35), (25,25), (35,15), (15,35)], "Quit app"),
    QAButton(play_song, (255,255,255), [(15,25), (35,25), (25,15), (35,25), (25,35)], "Play next song", 'next'),
    QAButton(menu, (255,255,255), [(23,15), (18,20), (18,35), (32,35), (32,15), (23,15), (23,20), (18,20)], "Open/close song selector"),
    QAButton(pin, (255,255,255), [(25,35), (25,27), (19,27), (21,23), (21,19), (19,15), (31,15), (29,19), (29,23), (31,27), (25,27)], "Pin/unpin bar", 'pin_state'),
    QAButton(remember_last, (255,255,255), [(30,15), (35,20), (35,35), (15,35), (15,15), (30,15), (29,15), (29,22), (19,22), (19,15)], "Remember last played song", 'remember_last_song_state'),
]

hovered = False
hover_key = 0

menu_opened = False
menu_key = 0
menu_size = windowy//3
menu_scroll = 0
menu_scroll_vel = 0
dragging = False

pinned = False
pin_state = "Bar unpinned"

remember_last_song_state = 'On' if save_data['remember_last_song'] else 'Off'

tooltip_visibility = 0

focus_surface = pg.Surface((len(buttons)*50,50))
focus_surface.set_alpha(128)
focus_surface.fill((1,1,1))

volume_key = 0
volume_timer = 0

popup_timer = 0
popup_key = 0

marker_key = 0
# other variables like songs, length, song_num or others define on the fly in functions above


# discord rich presence
if save_data['discord_presence']:
    pg.display.set_caption('Connecting to Discord...')
    try:
        RPC = Presence(save_data['client_id'])
        RPC.connect()
    except:
        pass


# main loop

while running:

############## INPUT ##############

    events = pg.event.get()
    mouse_pos = pyautogui.position()
    mouse_press = pg.mouse.get_pressed(5)
    mouse_moved = pg.mouse.get_rel()
    focused = pg.key.get_focused()
    lmb_up = False
    lmb_down = False
    mouse_wheel = 0

    subtitle_shift = 0
    screen.fill((0,0,0))



############## PROCESSING EVENTS ##############

    for event in events:
        if event.type == pg.QUIT:
            running = False

        if event.type == pg.MOUSEWHEEL:
            mouse_wheel = event.y

        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            lmb_up = True

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            lmb_down = True



############## SYSTEM STUFF ##############

    # playing music
    if not pg.mixer.music.get_busy():
        play_song()

    # spent time
    time_spent = time.time()-time_started
    percentage = time_spent/length

    # hovering
    hovered = (mouse_pos[1] > windowy-2-hover_key*2 and mouse_pos[0] > 0 and mouse_pos[0] < windowx) or menu_opened or pinned

    if hovered and hover_key < 20: 
        hover_key += 1
    if not hovered and hover_key > 0:
        hover_key -= 1

    # opening menu
    if menu_opened and menu_key < 21: 
        menu_key += 1
    if not menu_opened and menu_key > 0:
        menu_key -= 1



############## SONG INFO ##############

    if hover_key > 0:
        ease = easing.QuinticEaseOut(0,1,20).ease(hover_key)
        hover_ease = ease
        subtitle_shift += ease*50

        rect = pg.Rect(ease*20,windowy-ease*50,windowx-ease*40,100)
        pg.draw.rect(screen, (1,1,1), rect, border_radius=20)

        size = 15

        # rewinding
        if lmb_down and mouse_pos[1] > windowy-3:
            rewind((mouse_pos[0]-20)/(windowx-40)*length)

        # changing volume
        if mouse_wheel != 0 and rect.collidepoint(mouse_pos):
            update_vol(mouse_wheel)

        # marker
        if marker_key > 0 and mouse_pos[0] > 20 and mouse_pos[0] < windowx-20:
            color = min(20+abs(mouse_moved[0])*3,255)
            pg.draw.line(screen, (color,color,color), (mouse_pos[0], windowy), (mouse_pos[0], windowy-(ease+marker_key/10)*25), 2)

        if mouse_pos[1] > windowy-3 and marker_key < 10 and focused:
            marker_key += 1
        if mouse_pos[1] <= windowy-3 and marker_key > 0:
            marker_key -= 1

        # song num
        size += draw.text(f'#{song_num}', (size+ease*20,windowy+24-ease*50), size=28, style='bold', vertical_margin='m')[0]+22
        pg.draw.line(screen, (40,40,40), (size-12+ease*20, windowy+38-ease*50), (size-12+ease*20, windowy+11-ease*50), 2)

        # time
        size += draw.text(f'{int(time_spent)//60}:{int(time_spent)%60:0>2}', (size+ease*20,windowy+24-ease*50), size=28, style='bold', vertical_margin='m')[0]+1
        size += draw.text(f'{str(time_spent).split(".")[1][0]}', (size+ease*20,windowy+27-ease*50), size=20, style='bold', vertical_margin='m')[0]+7
        size += draw.text(f'/ {int(length)//60}:{int(length)%60:0>2}', (size+ease*20,windowy+27-ease*50), (150,150,150), size=20, style='bold', vertical_margin='m')[0]+22
        pg.draw.line(screen, (40,40,40), (size-12+ease*20, windowy+38-ease*50), (size-12+ease*20, windowy+11-ease*50), 2)

        # tooltip
        if tooltip_visibility > 10:
            color = (tooltip_visibility-10)*20
            size += draw.text(tooltip_text, (size+ease*20,windowy+24-ease*50), (color,color,color), size=26, style='bold', vertical_margin='m')[0]+10
            if tooltip_var != None:
                text_size = draw.get_text_size(tooltip_var, 18)[0]
                if text_size > windowx-10-ease*40-len(buttons)*50-size:
                    text_scale = windowx-10-ease*40-len(buttons)*50-size
                else:
                    text_scale = None
                draw.text(tooltip_var, (size+ease*20,windowy+27-ease*50), (color/3,color/3,color/3), size=18, vertical_margin='m', rect_size_x=text_scale)

        # song name
        else:
            text_size = draw.get_text_size(playing, 24)[0]
            if text_size > windowx-10-ease*40-len(buttons)*50-size:
                text_scale = windowx-10-ease*40-len(buttons)*50-size
            else:
                text_scale = None
            color = (10-tooltip_visibility)/10*254+1
            draw.text(playing, (size+ease*20,windowy+24-ease*50), (color,color,color), size=24, vertical_margin='m', rect_size_x=text_scale)

        # tooltip
        if tooltip_visibility > 0:
            percent_vis = tooltip_visibility/20

        # quick action buttons
        ongoing = windowx-50-ease*20
        did_hover = False

        for i in buttons:
            rect = pg.Rect(ongoing, windowy-ease*50, 50,70)
            hover_rect = pg.Rect(ongoing, windowy-ease*50, 50,48)
            strokes = [(j[0]+ongoing, j[1]+windowy+1-ease*50) for j in i.strokes]
            
            # drawing button
            if hover_rect.collidepoint(mouse_pos) and focused:
                pg.draw.rect(screen, i.hover_color, rect, border_radius=20)
                pg.draw.aalines(screen, (1,1,1), False, strokes)
                if lmb_up: i.click()

                if tooltip_visibility < 20:
                    tooltip_visibility += 1

                tooltip_text = i.tooltip
                if i.variable != None: tooltip_var = globals()[i.variable]
                else: tooltip_var = None

                did_hover = True
            else:
                pg.draw.aalines(screen, i.hover_color, False, strokes)
            
            ongoing -= 50

        if not did_hover and tooltip_visibility > 0:
            tooltip_visibility -= 1

        # dimming bar if window is not focused
        if not focused:
            screen.blit(focus_surface, (ongoing+50,windowy-ease*50))

    else:
        hover_ease = 0



############## SONG SELECTOR ##############

    if menu_key > 1:
        # drawing base box
        ease = easing.QuinticEaseOut(0,1,20).ease(menu_key-1)

        rect = pg.Rect(20,windowy-subtitle_shift-20-ease*menu_size, windowx-40,ease*menu_size)
        pg.draw.rect(screen, (1,1,1), rect, border_radius=20)

        subtitle_shift += ease*menu_size+20

        # closing
        if not focused:
            menu_opened = False

        # scrolling
        if mouse_wheel != 0 and rect.collidepoint(mouse_pos):
            menu_scroll_vel -= mouse_wheel*15

        if menu_scroll < 0: menu_scroll = 0
        if menu_scroll > len(vis_songs)*30-30: menu_scroll = len(vis_songs)*30-30

        menu_scroll += menu_scroll_vel
        menu_scroll_vel /= 1.3

        # songs
        ongoing = rect.centery-menu_scroll-20 # i did this shit at 3am plz fix somebody
        draw_ongoing = -menu_scroll+5-rect.height//2
        index = 0

        for i in vis_songs:
            # optimization
            if ongoing < rect.top:
                ongoing += 30; draw_ongoing += 30
                index += 1
                continue
            
            if ongoing > rect.bottom-30:
                break

            # offsets and positions
            raw_sine = -np.sin((draw_ongoing/(menu_size-30))*np.pi)
            sine = raw_sine*menu_size/10
            color = max(1,int(raw_sine*255))

            # fav button
            btn_rect = pg.Rect(20+sine,ongoing, 30,30)
            color_fav = int(color)

            if btn_rect.collidepoint(mouse_pos) and focused and not size_rect.collidepoint(mouse_pos) and not dragging:
                pg.draw.rect(screen, (color,color,color), btn_rect, border_radius=15)
                color_fav = 1

                # pressing
                if lmb_up:
                    if i in save_data['boosted']:
                        save_data['boosted'].remove(i)
                        popup('Unfavorited:', i, 200)
                    else:
                        save_data['boosted'].append(i)
                        popup('Favorited:', i, 200)
                    save()

            if i in save_data['boosted']:
                color_fav2 = color_fav//3
            else:
                color_fav2 = color_fav

            draw.text('♥' if i in save_data['boosted'] else '♡', btn_rect.center, (color_fav,color_fav2,color_fav2), vertical_margin='m', horizontal_margin='m')

            # set as next button
            btn_rect = pg.Rect(50+sine,ongoing, 30,30)
            color_next = int(color)

            if btn_rect.collidepoint(mouse_pos) and focused and not size_rect.collidepoint(mouse_pos) and not dragging:
                pg.draw.rect(screen, (color,color,color), btn_rect, border_radius=15)
                color_next = 1

                # pressing
                if lmb_up and next != i:
                    next = i
                    save_data['next_song'] = next
                    popup('Set as next song:', i, 200)
                    save()

            draw.text('→' , btn_rect.center, (color_next,color_next,color_next), vertical_margin='m', horizontal_margin='m')
            
            # song name
            size = draw.get_text_size(i)[0]
            song_rect = pg.Rect(80+sine,ongoing, min(size,windowx-120-sine)+20,30)

            if song_rect.collidepoint(mouse_pos) and focused and not size_rect.collidepoint(mouse_pos) and not dragging:
                pg.draw.rect(screen, (color,color,color), song_rect, border_radius=15)
                color = 1

                # pressing
                if lmb_up and playing != i:
                    play_song(i)
            
            if playing == i:
                color_g = color//3
            else:
                color_g = color

            draw.text(i, song_rect.center, (color_g,color,color_g), rect_size_x=min(size,windowx-120-sine), vertical_margin='m', horizontal_margin='m')

            ongoing += 30; draw_ongoing += 30
            index += 1

        # changing size
        size_rect = pg.Rect(40,rect.top,windowx-80,10)

        if size_rect.collidepoint(mouse_pos):
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_SIZENS)
            if lmb_down:
                dragging = True

        if lmb_up:
            dragging = False

        if dragging:
            menu_size = windowy-mouse_pos[1]-69
            if menu_size < 100:
                menu_size = 100

        if dragging or size_rect.collidepoint(mouse_pos):
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_SIZENS)
        else:
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)
            



############## BOTTOM BAR ##############

    pg.draw.line(screen, (255,255,255), (hover_ease*20,windowy-1), ((windowx-hover_ease*40)*percentage+20*hover_ease,windowy-1), 3)

    # volume
    if volume_key > 0:
        ease = easing.ExponentialEaseOut(0,1,20).ease(volume_key)
        pg.draw.line(screen, (1,1,1), (hover_ease*20,windowy-1), ((windowx-hover_ease*20)*ease,windowy-1), 3)
        pg.draw.line(screen, (65,180,255), (hover_ease*20,windowy-1), (((windowx-hover_ease*40)*volume/100+20*hover_ease)*ease,windowy-1), 3)

    if volume_timer > 0:
        volume_timer -= 1 
        if volume_key < 20: volume_key += 1
    elif volume_key > 0:
        volume_key -= 1



############## POPUP ##############

    # popup
    if popup_key > 0:
        ease = easing.ExponentialEaseOut(0,1,20).ease(popup_key)
        bsize = draw.get_text_size(popup_text, 20, 'bold')[0]
        vsize = draw.get_text_size(popup_val, 22)[0]
        size = bsize+vsize
        rect = pg.Rect(halfx-(size/2+15)*ease,70,(size+30)*ease,40)

        pg.draw.rect(screen, (1,1,1), rect, border_radius=20)
        draw.text(popup_text, (rect.left+10, rect.centery), (128,128,128), 20, 'bold', 'l', 'm', rect_size_x=bsize*ease)
        draw.text(popup_val, (rect.right-10, rect.centery), (255,255,255), 22, 'regular', 'r', 'm', rect_size_x=vsize*ease)

    if popup_timer > 0:
        popup_timer -= 1
        if popup_key < 20: popup_key += 1
    elif popup_key > 0:
        popup_key -= 1



############## SUBTITLES ##############

    if current_subtitle != None:
        line = current_subtitle.get_element(time_spent)
        if line != None:
            ease = easing.QuadEaseIn(0,1,0.3).ease(0.3-min(0.3, min(line.dist_from_end, line.dist_from_start)))
            offset = easing.QuadEaseIn(0,22,0.3).ease(0.3-min(0.3, line.dist_from_end))
            size_y = 22-ease*22

            draw.text(line.text, (windowx-10, windowy-10-subtitle_shift-offset), horizontal_margin='r', vertical_margin='b', rect_size_y=size_y)



############## UPDATING SCREEN ##############

    if menu_key == 0:
        update_rects = [(0,windowy-80,windowx,80), (0,70,windowx,40)]
    else:
        update_rects = [(0,0,windowx,windowy)]

    pg.display.update(update_rects)
    clock.tick(fps)