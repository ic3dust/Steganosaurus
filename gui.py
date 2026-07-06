import PySimpleGUI as gui
from PIL import Image
import io
import os

user = os.path.expanduser('~')
script_dir = os.path.dirname(__file__)
icon = os.path.join(script_dir, 'icons', 'logo.ico')
gui.theme('DarkGrey12')
#gui.theme_previewer()
COLOR = "#313641"

def LSBcrypt(image_path, secret_msg, output_path):
    try:
        img = Image.open(image_path).convert('RGB')
        pixels = img.load()
        secret_msg+='#####'
        binary_msg = ''.join(format(ord(char), '08b') for char in secret_msg)
        i = 0
        width, height = img.size

        for y in range(height):
            for x in range(width):
                if i < len(binary_msg):
                    r, g, b = pixels[x, y]
                    if i < len(binary_msg):
                        r = (r & ~1) | int(binary_msg[i]);i+=1
                    if i < len(binary_msg):
                       g = (g & ~1) | int(binary_msg[i]);i+=1
                    if i < len(binary_msg):
                       b = (b & ~1) | int(binary_msg[i]);i+=1
                    pixels[x, y]=(r,g,b)
                else: break
                if i >= len(binary_msg): break
        img.save(output_path, format="PNG")        
        return True
    except Exception as ex:
        gui.popup_error(f"Encryption failed: {ex}")
        return False

def LSBdecrypt(image_path):
    try:
        img = Image.open(image_path).convert('RGB')
        pixels=img.load()
        binary_msg = ""
        width,height = img.size
        for y in range (height):
            for x in range (width):
                r,g,b=pixels[x, y]  
                binary_msg += str(r & 1)
                binary_msg += str(g & 1)
                binary_msg += str(b & 1)
        full_bin = "".join(binary_msg)
        data = [full_bin[i: i+8] for i in range(0, len(full_bin), 8)]
        decoded = ""
        for byte in data:
            if len(byte)<8:
                break
            decoded += chr(int(byte,2))
            if decoded.endswith('#####'):
                return decoded[:-5]
        return "No hidden message was found."
    
    except Exception as ex:
        gui.popup_error(f"Failed to decrypt: {ex}")
        return False
    
def load_orig(filename=None, max_size=(400, 400), color=COLOR):
    try:
        canvas = Image.new("RGB", max_size, color)
        if filename:
            image = Image.open(filename)
            image.thumbnail(max_size)
            x_offset = (max_size[0] - image.width) // 2
            y_offset = (max_size[1] - image.height) // 2
            canvas.paste(image, (x_offset, y_offset))
        bio = io.BytesIO()
        canvas.save(bio, format='PNG')
        return bio.getvalue()
        
    except Exception as e:
        gui.popup_error(f"Error processing image asset: {e}")
        return load_orig(filename=None, max_size=max_size, color=color) if filename else None

image_row = [
    gui.Column([
        [gui.Text("Original Image:")],
        [gui.Image(key='-CONT-', size=(400, 400),background_color=COLOR)]
    ], size=(410, 430), pad=(10,10),element_justification='center', vertical_alignment='center'),
    
    gui.Column([
        [gui.Text("Encrypted Image Preview:")],
        [gui.Image(key='-ENCRYPTED_PREVIEW-', size=(400, 400), background_color=COLOR)] 
    ], size=(410, 430), pad=(10,10),element_justification='center', vertical_alignment='center')
]

layout = [
    [gui.Frame("Image Setup", [
        [
            gui.Text("Load container (image):"), 
            gui.Input(key='-FILE_PATH-', enable_events=True, size=(25, 1)), 
            gui.FileBrowse('Choose file', initial_folder=user, file_types=(("PNG Image", "*.png"),)),
            gui.Text("(Or select the image to decrypt)", font=('Helvetica', 9, 'italic'))
        ]
    ], element_justification='left', expand_x=True, pad=(10, 10))],
    
    image_row,
    
    [
        gui.Column([[gui.Button('Encrypt', key="-E-", visible=False, size=(15,2), pad=(10,30))]]), 
        gui.Column([[]], expand_x=True),
        gui.Column([[gui.Button('Decrypt', key="-D-", visible=False, size=(15,2), pad=(10,30))]])
    ]
]

window = gui.Window("app by cryptor", layout, icon=icon)

def msg_window():
    global embedded
    msg_window_layout=[
        [gui.Text("Enter the message to embed:")],
        [gui.InputText(key='-SECRET-', size=(40,1))],
        [gui.Button('Embed', key='-EMBED-'),gui.Button('Cancel', key='-C-')]
    ]

    msg_window_gui = gui.Window("Input to embed",msg_window_layout, modal=True, finalize=True)
    msg_window_gui['-SECRET-'].set_focus()

    while True:
        event, values = msg_window_gui.read()
        if event in (gui.WIN_CLOSED, '-C-'):
            embedded = False
            message = None
            break
        if event == '-EMBED-':
            message = values['-SECRET-'].strip()
            if not message:
                gui.popup_error("Message not specified!")
                embedded = False
                continue
            embedded =True
            break
    msg_window_gui.close()
    return message

def decrypt_window(window, initial_path=""):
    decrypt_window_layout = [
        [gui.Text("Select the image to decrypt...")],
        [gui.Input(default_text=initial_path,key='-DEC_FILE_PATH-', enable_events=True),
         gui.FileBrowse('Choose file', file_types=(("PNG Image", "*.png"),))], 
        [gui.Text('Decoded Output:')],
        [gui.Multiline(size=(45, 4), key='-OUT-', disabled=True)],
        [gui.Button("Decrypt", key="-D_SUBMIT-"), gui.Button('Close', key='-CD-')]
    ]
    decrypt_window_gui = gui.Window("LSB decryption",decrypt_window_layout, modal=True, finalize=True)

    if initial_path:
        img_bytes = load_orig(initial_path)
        window['-ENCRYPTED_PREVIEW-'].update(data=img_bytes)
    while True:
        event, values = decrypt_window_gui.read()
        if event in (gui.WIN_CLOSED, '-CD-'):
            break
        if event == '-DEC_FILE_PATH-':
            filename = values['-DEC_FILE_PATH-']
            if filename and not filename.lower().endswith('.png'):
                gui.popup_error("app accepts only .PNG format so far.")
                decrypt_window_gui['-DEC_FILE_PATH-'].update('')
        if event == "-D_SUBMIT-":
            if values['-DEC_FILE_PATH-']:
                output = LSBdecrypt(values['-DEC_FILE_PATH-'])
                
                decrypt_window_gui['-OUT-'].update(disabled=False)
                decrypt_window_gui['-OUT-'].update(output)
                decrypt_window_gui['-OUT-'].update(disabled=True)
            else:
                gui.popup_error("Please choose a file first!")
                
    decrypt_window_gui.close()


# WORK, IF IMAGE #
while True:
    event, values = window.read()

    if event == gui.WINDOW_CLOSED:
        break
    
    if event == '-FILE_PATH-' or event == 'Choose file':
        filename=values['-FILE_PATH-']
        if filename:
            if not filename.lower().endswith('.png'):
                gui.popup_error("app accepts only .PNG format so far.")
                window['-FILE_PATH-'].update('')
                continue

            img_data=load_orig(filename)
            if img_data is not None:

                window['-CONT-'].update(data=img_data)
                window['-E-'].update(visible=True)
                window['-D-'].update(visible=True)
    if event == '-E-':
        while True:

            secret_msg = msg_window()
            if not secret_msg or not embedded:
                break
            
            save_layout = [
                [gui.Text("Choose where to save your encrypted image:")],
                [gui.Input(key='-SAVE_FOLDER-'), gui.FileSaveAs('Browse', file_types=(("PNG Image", "*.png"),), initial_folder=user)],
                [gui.Button('Save', key='-SAVE_BTN-'), gui.Button('Back', key='-BACK_BTN-')]
            ]

            save_gui = gui.Window("Save encrypted image as...", save_layout, modal=True, finalize=True)
            save_gui['-SAVE_FOLDER-'].set_focus()

            back= False
            save_path = None

            while True:

                save_event, save_values = save_gui.read()
                if save_event == gui.WIN_CLOSED:
                    break
                    
                if save_event == '-BACK_BTN-':
                    back = True
                    break
                    
                if save_event == '-SAVE_BTN-':
                    save_path = save_values['-SAVE_FOLDER-'].strip()
                    if not save_path:
                        gui.popup_error("Please select a file path!")
                        continue
                    break
            
            save_gui.close() 

            if back:
                continue  
            
            if not save_path:
                continue

            if not save_path.lower().endswith('.png'):
                save_path+='.png'
            success = LSBcrypt(values['-FILE_PATH-'], secret_msg,save_path)
            if success:
                encrypted_bytes = load_orig(save_path)
                window['-ENCRYPTED_PREVIEW-'].update(data=encrypted_bytes, visible=True)
                break
    if event == '-D-':
        current_path = values['-FILE_PATH-']
        decrypt_window(window, initial_path=current_path)
    if event == "-D_SUBMIT-":
            file_to_decode = values['-DEC_FILE_PATH-']
            if file_to_decode:
                output = LSBdecrypt(file_to_decode)
                
                decrypt_window['-OUT-'].update(disabled=False)
                decrypt_window['-OUT-'].update(output)
                decrypt_window['-OUT-'].update(disabled=True)
            else:
                gui.popup_error("Please choose a file first!")

window.close()