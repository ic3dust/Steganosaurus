import PySimpleGUI as gui
from PIL import Image
import io
import os

user = os.path.expanduser('~')
script_dir = os.path.dirname(__file__)
icon = os.path.join(script_dir, 'icons', 'logo.ico')
gui.theme('DarkGrey12')
#gui.theme_previewer()

def load_orig(filename, max_size=(500,500)):
    try:
        image = Image.open(filename)
        image.thumbnail(max_size)
        bio = io.BytesIO()
        image.save(bio, format='PNG')
        return bio.getvalue()
    except Exception as e:
        gui.popup_error(f"Error loading image: {e}")
        return None

layout = [
    [gui.Text("Load container (image):"), gui.Input(key='-FILE_PATH-', enable_events=True), 
     gui.FileBrowse('Choose file', initial_folder=user, file_types=(("Image Files", "*.png;*.jpg;*.jpeg"),))], # <-- Fixed here
    [gui.Image(key='-CONT-')],
    [
        gui.Column([[gui.Button('Encrypt', key="-E-", visible=False, size=(15,2), pad=(10,30))]]), 
        gui.Column([[]], expand_x=True),
        gui.Column([[gui.Button('Decrypt', key="-D-", visible=False, size=(15,2), pad=(10,30))]])
    ]
]

window = gui.Window("Steganosaurus by ic3dust", layout, icon=icon)

# WORK, IF IMAGE #
while True:
    event, values = window.read()

    if event == gui.WINDOW_CLOSED:
        break
    
    if event == '-FILE_PATH-' or event == 'Choose file':
        filename=values['-FILE_PATH-']
        if filename:
            img_data=load_orig(filename)
            if(img_data is not None):

                window['-CONT-'].update(data=img_data)
                window['-E-'].update(visible=True)
                window['-D-'].update(visible=True)

window.close()