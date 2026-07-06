import PySimpleGUI as gui
from PIL import Image

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