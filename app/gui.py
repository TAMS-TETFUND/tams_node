import io
import json
import os
from PIL import Image, ImageDraw, ImageTk, ImageFont
import base64
import subprocess
import sys

import PySimpleGUI as sg

from icons import get_icon

ATTENDANCE_SESSION_DETAILS = {}
ICON_SIZE = {"h": 125, "w": 70}

with open("icons.json", "r") as data:
    icon_dict = json.loads(data.read())

def image_file_to_bytes(image64, size):
    image_file = io.BytesIO(base64.b64decode(image64))
    img = Image.open(image_file)
    img.thumbnail(size, Image.ANTIALIAS)
    bio = io.BytesIO()
    img.save(bio, format='PNG')
    imgbytes = bio.getvalue()
    return imgbytes


sg.theme('LightGreen6') #Dark, LightGreen6
wcolor = (sg.theme_background_color(), sg.theme_background_color())
# The home window
def make_window_home():

    fingerprint_icon = icon_dict['fingerprint']
    users_icon = icon_dict['users']
    column1 = [
                [
                    sg.Push(), 
                    sg.Button(image_data=image_file_to_bytes(fingerprint_icon, (ICON_SIZE['h'],ICON_SIZE['w'])), 
                                button_color=wcolor, 
                                font='Any 15', 
                                key='New'),
                    sg.Push()
                ],
                [sg.Push(), sg.Text('New'), sg.Push()]
                ]
    column2 = [
                [
                    sg.Push(), sg.Button(image_data=image_file_to_bytes(users_icon, (125,63)), 
                                        button_color=wcolor, font='Any 15', 
                                        pad=(0,0)), sg.Push()
                ],
                [sg.Push(), sg.Text('Continue Attendance'), sg.Push()]
                ]
    # column3 = [[sg.Text('A')]]
    
    layout = [
                [sg.VPush()],
                [sg.Push(), sg.Column(column1), sg.Column(column2), sg.Push()],
                [sg.VPush()]]
    home_window =  sg.Window('Home Window', 
                            layout,
                            size=(480,320),
                            no_titlebar=True,
                            keep_on_top=True,
                            grab_anywhere=True,
                            finalize=True)
    # home_window.maximize()
    return home_window

# The 'Choose Event' Window
def make_window_event_menu():
    exam_icon = icon_dict['graduation_cap']
    test_icon = icon_dict['test_script']
    lab_icon = icon_dict['lab']
    lecture_icon = icon_dict['lecture']

    column1 = [
                [
                sg.Push(), 
                sg.Button(image_data=image_file_to_bytes(lecture_icon, 
                                                        (ICON_SIZE['h'], ICON_SIZE['w'])
                                                        ),
                            button_color=wcolor, font='Any 15'),
                sg.Push()],
                [sg.Push(), sg.Text('Lecture'), sg.Push()]
                ]
    
    column2 = [
                [
                sg.Push(), 
                sg.Button(image_data=image_file_to_bytes(lab_icon, 
                                                        (ICON_SIZE['h'], ICON_SIZE['w'])
                                                        ),
                            button_color=wcolor, font='Any 15'),
                sg.Push()],
                [sg.Push(), sg.Text('Lab'), sg.Push()]
                ]
    
    column3 = [
                [
                sg.Push(), 
                sg.Button(image_data=image_file_to_bytes(test_icon, 
                                                        (ICON_SIZE['h'], ICON_SIZE['w'])
                                                        ),
                            button_color=wcolor, font='Any 15'),
                sg.Push()],
                [sg.Push(), sg.Text('Test'), sg.Push()]
                ]
    
    column4 = [
                [
                sg.Push(), 
                sg.Button(image_data=image_file_to_bytes(exam_icon, 
                                                        (ICON_SIZE['h'], ICON_SIZE['w'])
                                                        ),
                            button_color=wcolor, font='Any 15'),
                sg.Push()],
                [sg.Push(), sg.Text('Exam'), sg.Push()]
                ]

    layout = [
                [sg.Push(),sg.Text('Take Attendance for:', font='Any 20'), sg.Push()],
                [sg.Text('_' * 80)],
                [sg.VPush()],
                [sg.Push(), sg.Column(column1), sg.Column(column2), 
                sg.Column(column3), sg.Column(column4), sg.Push()],
                [sg.VPush()],
                [sg.Text('_' * 80)],
                [sg.Push(), sg.Button("Back"), sg.Push()]]

    event_menu_window =  sg.Window('Event Menu', 
                            layout,
                            size=(480,320),
                            no_titlebar=True,
                            keep_on_top=True,
                            grab_anywhere=True,
                            finalize=True)
    # event_menu_window.maximize()
    return event_menu_window

def main():
    home_window = make_window_home()
    event_menu_window = None


    while True:
        window, event, values = sg.read_all_windows()
        if event == sg.WIN_CLOSED:
            break

        if event == 'New' and not event_menu_window:
            home_window.hide()
            event_menu_window = make_window_event_menu()
            

        if window == event_menu_window and (event in (sg.WIN_CLOSED, 'Back')):
            event_menu_window.close()
            event_menu_window = None
            home_window.un_hide()

        if window == home_window:
            if event in ('Continue Existing Attendance-Taking Session'):
                break
    home_window.close()



if __name__ == '__main__':
    main()