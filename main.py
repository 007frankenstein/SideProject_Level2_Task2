import os
from tkinter import *
import tkinter.messagebox
from tkinter import filedialog
from mutagen.mp3 import MP3
import time
import threading

import sqlite3

from tkinter import ttk
from ttkthemes import themed_tk as tk

from pygame import mixer


root = tk.ThemedTk()
root.get_themes()
root.set_theme('yaru')

statusbar = ttk.Label(root, text = 'Welcome to MusicMasti', relief = SUNKEN, anchor = W, font = 'Times 15 italic', foreground = 'Red')
statusbar.pack(side = BOTTOM, fill = X)

menubar = Menu(root)
root.config(menu = menubar)


play_list = []
def playList_init():

    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute('SELECT song_path FROM playlist')
        path_records = c.fetchall()


        for row in path_records:
            play_list.append(row[0])

        #print(play_list)

        l=0
        for list in play_list:
            play_list_box.insert(l, os.path.basename(list))
            l = l + 1

        conn.commit()

        c.close()

        return path_records

    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)

    finally:
        if (conn):
            conn.close()


def browse_file():
    global filename_path

    filename_path = filedialog.askopenfilename()

    add_to_playlist(filename_path)


index = 0
def add_to_playlist(filename_path):
    global  index

    filename = os.path.basename(filename_path)

    play_list_box.insert(index, filename)
    play_list.insert(index, filename_path)

    index = index + 1

    save_song(filename_path, filename)


# This Creates a database named database.db
# This also creates a table named playlist in the database database.db, if the table does not exist
# File Path is the Primary Key for the relational database playlist
"""
def create():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    c.execute("CREATE TABLE IF NOT EXISTS playlist(song_path text primary key, song_name text)")
    
    conn.commit()
    conn.close()

create()

"""

def save_song(filename_path, filename):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute('INSERT INTO playlist VALUES (:f_path, :f_name)',
                  {
                      'f_path': filename_path,
                      'f_name': filename
                  })

        c.execute('SELECT * FROM playlist')

        # print(c.fetchall())

        conn.commit()

        c.close()

    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)

    finally:
        if (conn):
            conn.close()



subMenu = Menu(menubar, tearoff = 0)
menubar.add_cascade(label = 'File', menu = subMenu)
subMenu.add_command(label = 'Open', command = browse_file)
subMenu.add_command(label = 'Exit', command = root.destroy)


def about_us():
    tkinter.messagebox.showinfo('About MusicMasti', 'This is a music player created by Rahul')


subMenu = Menu(menubar, tearoff = 0)
menubar.add_cascade(label = 'Help', menu = subMenu)
subMenu.add_command(label = 'About Us', command = about_us)


mixer.init()

root.geometry('840x540')
root.title('MusicMasti')
root.iconbitmap(r'images/MusicMasti.ico')

leftFrame = Frame(root)
leftFrame.pack(side = LEFT, padx = 30, pady = 30)

play_list_box = Listbox(leftFrame)
play_list_box.pack()

btnA = ttk.Button(leftFrame, text = '+ Add', command = browse_file)
btnA.pack(side = LEFT)


def remove_song():
    selected_song = play_list_box.curselection()
    selected_song = int(selected_song[0])
    play_list_box.delete(selected_song)

    delete_song(play_list[selected_song])

    play_list.pop(selected_song)


def delete_song(filename_path):

    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute('DELETE FROM playlist WHERE song_path = :f_path', {
            'f_path': filename_path
        })

        c.execute('SELECT * FROM playlist')

        #print(c.fetchall())

        conn.commit()

        c.close()

    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)

    finally:
        if (conn):
            conn.close()



btnD = ttk.Button(leftFrame, text = '- Delete', command = remove_song)
btnD.pack()


rightFrame = Frame(root)
rightFrame.pack(pady = 30)

topFrame = Frame(rightFrame)
topFrame.pack()


lengthLabel = ttk.Label(topFrame, text = 'Music Play Time :    --:--', foreground = 'Blue')
lengthLabel.pack(pady = 5)

timerLabel = ttk.Label(topFrame, text = 'Remaining Play Time :     --:--', relief = GROOVE, foreground = 'Green')
timerLabel.pack(pady = 10)

def show_details(play_song):

    file_data = os.path.splitext(play_song)

    if file_data[1] == '.mp3':
        temp = MP3(play_song)
        total_length = temp.info.length
    else:
        temp = mixer.Sound(play_song)
        total_length = temp.get_length()

    mins, secs = divmod(total_length, 60)
    mins = round(mins)
    secs = round(secs)

    timeFormat = '{:02d}:{:02d}'.format(mins, secs)
    lengthLabel['text'] = 'Total Length' + '-' + timeFormat


    th1 = threading.Thread(target = countdown_timer, args = (total_length,))
    th1.setDaemon(True)
    th1.start()


def countdown_timer(t):
    global paused

    while t and mixer.music.get_busy():
        if paused:
            continue
        else:
            mins, secs = divmod(t, 60)
            mins = round(mins)
            secs = round(secs)
            timeFormat = '{:02d}:{:02d}'.format(mins, secs)
            timerLabel['text'] = 'Timer' + ' - ' + timeFormat
            time.sleep(1)
            t = t - 1


def play_music(is_paused):
    global paused

    paused = is_paused
    try:
        if paused and play_list[(int)(play_list_box.curselection()[0])] == temp:
            mixer.music.unpause()
            paused = False
            statusbar['text'] = 'Playing Music' + '-' + os.path.basename(os.path.basename(temp))
        elif paused and play_list[(int)(play_list_box.curselection()[0])] != temp:

            selected_song = play_list_box.curselection()
            selected_song = int(selected_song[0])
            play_it = play_list[selected_song]

            stop_music()
            time.sleep(1)
            mixer.music.load(play_it)
            mixer.music.play()
            paused = False
            statusbar['text'] = 'Playing Music' + '-' + os.path.basename(play_it)
            show_details(play_it)

        else:
            selected_song = play_list_box.curselection()
            selected_song = int(selected_song[0])
            play_it = play_list[selected_song]

            stop_music()
            time.sleep(1)
            mixer.music.load(play_it)
            mixer.music.play()
            statusbar['text'] = 'Playing Music' + '-' + os.path.basename(play_it)
            show_details(play_it)


    except:
        tkinter.messagebox.showerror('File Not Found', 'MusicMasti could not find the file. Please check again!!!')



def stop_music():
    mixer.music.stop()
    statusbar['text'] = 'Music Stopped'


paused = FALSE
def pause_music():
    global paused
    global temp

    mixer.music.pause()
    temp = play_list[(int)(play_list_box.curselection()[0])]
    paused = True
    statusbar['text'] = 'Music Paused' + '-' + os.path.basename(play_list[(int)(play_list_box.curselection()[0])])

    return temp

muted = FALSE
def mute_music():
    global muted

    if muted:
        mixer.music.set_volume(0.7)
        volumebtn.configure(image = volumePhoto)
        volSlider.set(70)
        statusbar['text'] = 'Playing Music' + '-' + os.path.basename(play_list[(int)(play_list_box.curselection()[0])])
        muted = FALSE
    else:
        mixer.music.set_volume(0.0)
        volumebtn.configure(image=mutePhoto)
        volSlider.set(0)
        statusbar['text'] = 'Music Muted'
        muted = TRUE


def next_song():

    try:
        current_song = play_list_box.curselection()
        current_song = int(current_song[0])
        next_one = current_song + 1
        play_it = play_list[next_one]

        stop_music()
        time.sleep(1)
        mixer.music.load(play_it)
        mixer.music.play()
        statusbar['text'] = 'Playing Music' + '-' + os.path.basename(play_it)
        play_list_box.selection_clear(0, END)
        play_list_box.activate(next_one)
        play_list_box.selection_set(next_one, last = None)
        show_details(play_it)

    except:
        tkinter.messagebox.showerror('File Not Found', 'MusicMasti could not find the file. Please check again!!!')



def prev_song():

    try:
        current_song = play_list_box.curselection()
        current_song = int(current_song[0])
        prev_one = current_song - 1
        play_it = play_list[prev_one]

        stop_music()
        time.sleep(1)
        mixer.music.load(play_it)
        mixer.music.play()
        statusbar['text'] = 'Playing Music' + '-' + os.path.basename(play_it)
        play_list_box.selection_clear(0, END)
        play_list_box.activate(prev_one)
        play_list_box.selection_set(prev_one, last=None)
        show_details(play_it)

    except:
        tkinter.messagebox.showerror('File Not Found', 'MusicMasti could not find the file. Please check again!!!')


def set_vol(val):

    volume = float (val) / 100
    mixer.music.set_volume(volume)


middleFrame = Frame(rightFrame)
middleFrame.pack(padx = 30, pady = 30)


playPhoto = PhotoImage(file = 'images/play.png')
playbtn = ttk.Button(middleFrame, image = playPhoto, command =  lambda : play_music(paused))
playbtn.grid(row = 0, column = 0, padx = 10)

stopPhoto = PhotoImage(file = 'images/stop.png')
stopbtn = ttk.Button(middleFrame, image = stopPhoto, command = stop_music)
stopbtn.grid(row = 0, column = 1, padx = 10)

pausePhoto = PhotoImage(file = 'images/pause.png')
pausebtn = ttk.Button(middleFrame, image = pausePhoto, command = pause_music)
pausebtn.grid(row = 0, column = 2, padx = 10)

bottomFrame = Frame(rightFrame)
bottomFrame.pack()

mutePhoto = PhotoImage(file = 'images/mute.png')
volumePhoto = PhotoImage(file = 'images/volume.png')
volumebtn = ttk.Button(bottomFrame, image = volumePhoto, command = mute_music)
volumebtn.grid(row = 0, column = 3, padx = 10)

nextPhoto = PhotoImage(file = 'images/next.png')
nextbtn = ttk.Button(bottomFrame, image = nextPhoto, command = next_song)
nextbtn.grid(row = 0, column = 2, padx = 10)

prevPhoto = PhotoImage(file = 'images/prev.png')
prevbtn = ttk.Button(bottomFrame, image = prevPhoto, command = prev_song)
prevbtn.grid(row = 0, column = 1, padx = 10)


volSlider = ttk.Scale(bottomFrame, from_ = 0, to_ = 100, orient = VERTICAL, command = set_vol)
volSlider.set(70)
mixer.music.set_volume(0.7)
volSlider.grid(row = 0, column = 4, padx = 15, pady = 30)


def on_closing():
    stop_music()
    root.destroy()


root.protocol('WM_DELETE_WINDOW', on_closing)


path_records = playList_init()


root.mainloop()


