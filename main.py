import time
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import messagebox
from pynput import keyboard
from pynput import mouse
from pynput.keyboard import Controller as KController
from pynput.mouse import Controller as MController
from datetime import datetime
import json


# Important stuff

is_listening = False
key_listener = None
mouse_listener = None
start_time = 0
global_dict = {}
keys_are_not_released = []
bind = None
config_dictionary = {}
is_config = False

# Saving and loading configs

def save_config():
    path = asksaveasfilename(initialdir='/', initialfile="Untitled.json", filetypes=[('Json Files', '*.json')])
    try:
        with open(path, "w") as f:
            json.dump(global_dict, f)
    except Exception as e:
        return

def load_config():
    global config_dictionary
    path = askopenfilename(filetypes=[("Json Files (configs are json-type)", "*.json")])
    lab_config.configure(text=path)
    if path == '':
        return
    with open(path, "r") as f:
        config_dictionary = json.load(f)
    print(config_dictionary)



# Recording stuff

def on_press(key):
    global is_listening, start_time
    if not is_listening:
        if key == keyboard.Key.insert:
            is_listening = True
            start_time = datetime.now().time()
    if key in keys_are_not_released or not is_listening or key == keyboard.Key.insert:
        return
    keys_are_not_released.append(key)
    t = datetime.combine(datetime.today(), datetime.now().time()) - datetime.combine(datetime.today(), start_time)
    global_dict[f"{t.total_seconds()}"] = f"key_press,{key}"
    if key == keyboard.Key.esc:
        is_listening = False
        key_listener.stop()
        if mouse_listener is not None:
            mouse_listener.stop()
        return False

def on_release(key):
    global is_listening
    if not is_listening:
        return
    if key == keyboard.Key.insert:
        return
    keys_are_not_released.remove(key)
    t = datetime.combine(datetime.today(), datetime.now().time()) - datetime.combine(datetime.today(), start_time)
    global_dict[f"{t.total_seconds()}"] = f"key_release,{key}"

def on_move(e1, e2):
    global is_listening
    if not is_listening:
        return
    t = datetime.combine(datetime.today(), datetime.now().time()) - datetime.combine(datetime.today(), start_time)
    global_dict[f"{t.total_seconds()}"] = f"move,{e1},{e2}"

def on_click(e1, e2, e3, e4):
    if not is_listening:
        return
    t = datetime.combine(datetime.today(), datetime.now().time()) - datetime.combine(datetime.today(), start_time)
    global_dict[f"{t.total_seconds()}"] = f"click,{e1},{e2},{e3},{e4}"


def record():
    global key_listener, mouse_listener, start_time
    messagebox.showinfo(title="Important information!", message="Press 'Insert' to start recording, press 'esc' to end recording.")
    key_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    key_listener.start()
    mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)
    mouse_listener.start()
    try:
        mouse_listener.join()
    except:
        pass
    try:
        key_listener.join()
    except:
        pass


# Playing stuff

slovar_button = {
    "Key.esc": keyboard.Key.esc,
    "Key.enter": keyboard.Key.enter,
    "Key.shift": keyboard.Key.shift,
    "Key.alt": keyboard.Key.alt,
    "Key.backspace": keyboard.Key.backspace,
    "'a'": "a", "'q'": "q", "'w'": "w", "'e'": "e", "'r'": "r", "'t'": "t", "'y'": "y", "'u'": "u",
    "'i'": "i", "'o'": "o", "'p'": "p", "'s'": "s", "'d'": "d", "'f'": "f", "'g'": "g", "'h'": "h",
    "'j'": "j", "'k'": "k", "'l'": "l", "'z'": "z", "'x'": "x", "'c'": "c", "'v'": "v", "'b'": "b",
    "'n'": "n", "'m'": "m", "'A'": "A", "'Q'": "Q", "'W'": "W", "'E'": "E", "'R'": "R", "'T'": "T",
    "'Y'": "Y", "'U'": "U", "'I'": "I", "'O'": "O", "'P'": "P", "'S'": "S", "'D'": "D", "'F'": "F",
    "'G'": "G", "'H'": "H", "'J'": "J", "'K'": "K", "'L'": "L", "'Z'": "Z", "'X'": "X", "'C'": "C",
    "'V'": "V", "'B'": "B", "'N'": "N", "'M'": "M", "'1'": "1", "'2'": "2", "'3'": "3", "'4'": "4",
    "'5'": "5", "'6'": "6", "'7'": "7", "'8'": "8", "'9'": "9", "'0'": "0", "'-'": "-", "'='": "=",
    "'['": "[", "']'": "]", "'\\'": "\\", "';'": ";", "'''": "'", "','": ",", "'.'": ".", "'/'": "/",
    "Key.space": keyboard.Key.space, "Key.tab": keyboard.Key.tab,
    "Key.caps_lock": keyboard.Key.caps_lock
}
slovar_click = {
    "Button.left":mouse.Button.left, "Button.right":mouse.Button.right
}






def run_script():
    global key_listener
    mc = MController()
    kb = KController()
    last_time = 0
    for timee, action in config_dictionary.items():
        if not is_config:
            break
        wait_time = float(timee) - last_time
        last_time = float(timee)
        act = action.split(",")
        time.sleep(wait_time)
        if act[0] == "key_press":
            key = slovar_button.get(act[1])
            # if not key:
            #     continue
            kb.press(key)
        elif act[0] == "release":
            key = slovar_button.get(act[1])
            # if not key:
            #     continue
            kb.press(key)
        elif act[0] == "move":
            mc.position = (int(act[1]), int(act[2]))
        elif act[0] == "click":
            if act[4] != "True":
                continue
            mc.position = (int(act[1]), int(act[2]))
            mc.click(slovar_click[act[3]])





def p_on_release(key):
    global is_config
    try:
        char = key.char
    except:
        return
    if char == bind:
        is_config = True
        run_script()
    if key == keyboard.Key.esc:
        is_config = False
        key_listener.stop()
        return False

def play():
    global bind, key_listener
    if lab_config.cget("text") == "":
        messagebox.showerror(title="Error!", message="Please choose config to start using it!")
        return
    bind = bind_input.get()
    alphabet = "qwertyuiopasdfghjklzxcvbnm"
    if type(bind) != str or bind not in alphabet or bind == '':
        messagebox.showerror("Error!", "You must write there english letter!")
        return
    bind = bind.lower()
    key_listener = keyboard.Listener(on_release=p_on_release)
    key_listener.start()
    try:
        key_listener.join()
    except:
        pass

app = tk.Tk()
app.title("Macro 1.0 sn3g0v1k")
app.geometry("300x500")
app.resizable(False, False)
rec_but = tk.Button(app, text='record', command=record)
rec_but.pack()
save_but = tk.Button(app, text="save", command=save_config)
save_but.pack()
choose_file_but_but = tk.Button(app, text="Choose config", command=load_config)
choose_file_but_but.pack()
lab_config = tk.Label(app)
lab_config.pack()
lab  = tk.Label(app, text="Enter your bind here:")
lab.pack()
bind_input = tk.Entry(app)
bind_input.pack()
start_but = tk.Button(app, text="Start", command=play)
start_but.pack()



app.mainloop()