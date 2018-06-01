from tkinter import *
from tkinter import messagebox
import subprocess
import sys
import os


# Main Settings
main_font = "Arial"
font_size = 10
h1_font_size = 36
h2_font_size = 24
h3_font_size = 16
# End Main Settings


# Window Settings
window = Tk()
window.title("Gertec TC506M Server Sync")
window.geometry('700x500')
window.iconbitmap('tc506.ico')
# End Window Settings


# GUI Actions
def find_between(s, first='', last=''):
    if first == '' and last == '':
        raise ValueError("There must be at least one character to find between the string")
    elif first != '' and last == '':
        last = first
    elif last != '' and first == '':
        first = last
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""


def popup_error(msg, title_msg='Erro!'):
    messagebox.showerror(
        title_msg,
        msg,
        parent=title
    )


def popup_success(msg, title_msg='Sucesso'):
    messagebox.showinfo(
        title_msg,
        msg,
        parent=title
    )


def translated_error_popup(error_msg):
    error_msg = str(error_msg)
    if (error_msg.find('FileNotFoundError') != -1):
        popup_error("O diretório deve existir e ser uma estrutura válida (contendo config.ini e a pasta tc506/)")
    else:
        error_msg = find_between(error_msg, '#').split('-')
        popup_error(error_msg[1], error_msg[0])


def translated_success_popup(success_msg):
    success_msg = str(success_msg)
    if (success_msg.find('Done.') != -1):
        popup_success(
            "Sincronização concluída",
            "Concluído!"
        )


def cmdline(command):
    try:
        CREATE_NO_WINDOW = 0x08000000
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=False, creationflags=CREATE_NO_WINDOW)
        translated_success_popup(output)
        return output
    except subprocess.CalledProcessError as e:
        translated_error_popup(e.output)
        return e.output


def write_on_console_textbox(text):
    console_textbox.configure(state='normal')
    console_textbox.delete('1.0', END)
    console_textbox.insert(END, text)
    console_textbox.insert(END, "\n")
    console_textbox.yview_moveto(1)
    console_textbox.configure(state='disabled')


def sync_btn_onclick():
    sync_btn.configure(cursor='wait')
    if place_input.get() == '':
        popup_error(
            "O campo Nome da pasta está vazio, preencha com o nome\n" +
            "de alguma pasta válida presente dentro do diretório server_images/"
        )
    else:
        write_on_console_textbox(cmdline(f"fab load_config:{place_input.get()} sync_servers"))
        sync_btn.configure(cursor='hand2')
# End GUI Actions


# GUI Structure
title = Label(window, text="Gertec TC506M Server Sync", font=(main_font, h2_font_size))
title.pack(fill='both')


place_frame = Frame(window)
place_frame.pack(pady=20)
place_label = Label(
    place_frame,
    text="Nome da pasta presente dentro do diretório server_images/" +
         "\n(geralmente associada ao nome do local, p. ex.: lab, loja001, armazem, etc)",
    font=(main_font, font_size)
)
place_label.pack(fill="both")
place_input = Entry(place_frame, width=40)
place_input.pack()


sync_btn = Button(
    window,
    text="Sincronizar",
    command=sync_btn_onclick,
    cursor="hand2",
    font=(main_font, h3_font_size),
    takefocus=True
)
sync_btn.pack()


console_label = Label(
    window,
    text="Console",
    font=(main_font, h3_font_size)
)
console_label.pack(fill="both", pady=10)
console_textbox = Text(
    window,
    background="black",
    foreground="white",
    font=(main_font, font_size),
    state=DISABLED
)
console_textbox.pack(fill="both", expand=True)
vscroll = Scrollbar(console_textbox, orient=VERTICAL, command=console_textbox.yview)
vscroll.pack(side="right", fill="y")
console_textbox.config(yscrollcommand=vscroll.set)
# End GUI Structure


window.mainloop()