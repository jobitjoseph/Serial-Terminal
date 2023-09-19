import PySimpleGUI as sg
import serial
import serial.tools.list_ports
import threading
import base64
import os
import tempfile

def serial_thread(port, baud, console, line_ending, running_event, ser_instance):
    with serial.Serial(port, baud, timeout=0.1) as ser:
        ser_instance.append(ser)
        while running_event.is_set():
            try:
                line = ser.readline().decode('utf-8')
                if line:
                    console.update(value=line, append=True)
            except Exception as e:
                print("Error:", e)
                break

sg.LOOK_AND_FEEL_TABLE['MaterialTheme'] = {
    'BACKGROUND': '#FFFFFF',
    'TEXT': '#FFFFFF',
    'INPUT': '#000000',
    'TEXT_INPUT': '#FFFFFF',
    'SCROLL': '#F0F0F0',
    'BUTTON': ('#FFFFFF', '#018786'),
    'PROGRESS': ('#01826B', '#D0D0D0'),
    'BORDER': 1,
    'SLIDER_DEPTH': 0,
    'PROGRESS_DEPTH': 0,
}

sg.theme('MaterialTheme')

baud_rates = [300, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200, 230400, 460800, 921600, 2000000]
line_endings = {
    "New Line": "\n",
    "Carriage Return": "\r",
    "Both NL+CR": "\r\n",
    "No Line Ending": ""
}

layout = [
    [sg.Text("Serial Port:"), 
     sg.Combo([port.device for port in serial.tools.list_ports.comports()], size=(20, 1), key="PORT"), 
     sg.Button("Refresh", key="REFRESH"), 
     sg.Text("Baud:"), 
     sg.Combo(baud_rates, default_value=9600, size=(10, 1), key="BAUD"), 
     sg.Button("Connect", size=(20, 1), key="CONN_DISCONN"),
     sg.Button("Clear", key="CLEAR_CONSOLE")
    ],
    [sg.Output(size=(100, 20), font=("Any", 12), key="CONSOLE", expand_x=True, expand_y=True)],
    [sg.InputText(size=(70, 1), font=("Any", 12), key="SEND_TXT", expand_x=True), 
     sg.Button("Send", key="SEND", font=("Any", 12)), 
     sg.Combo(list(line_endings.keys()), default_value="New Line", size=(15, 1), font=("Any", 12), key="LINE_END")
    ],
]

# Base64 Decoded Image
BASE64_ICON = "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"
decoded_icon = base64.b64decode(BASE64_ICON)

# Save the decoded image to a temporary .ico file
icon_filename = os.path.join(tempfile.gettempdir(), "temp_icon.ico")
with open(icon_filename, "wb") as icon_file:
    icon_file.write(decoded_icon)

window = sg.Window("Serial Monitor", layout, finalize=True, resizable=True, icon=icon_filename)

ser_thread = None
running_event = threading.Event()
ser_instance = []

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        running_event.clear()
        if ser_instance:
            ser_instance[0].close()
        break

    elif event == "CONN_DISCONN":
        if window["CONN_DISCONN"].GetText() == "Connect":
            running_event.set()
            ser_thread = threading.Thread(target=serial_thread, args=(values["PORT"], values["BAUD"], window["CONSOLE"], line_endings[values["LINE_END"]], running_event, ser_instance))
            ser_thread.start()
            window["CONN_DISCONN"].update("Disconnect")
            window["PORT"].update(disabled=True)
            window["BAUD"].update(disabled=True)
        else:
            running_event.clear()
            ser_thread.join()
            if ser_instance:
                ser_instance[0].close()
            window["CONN_DISCONN"].update("Connect")
            window["PORT"].update(disabled=False)
            window["BAUD"].update(disabled=False)

    elif event == "SEND":
        try:
            with serial.Serial(values["PORT"], values["BAUD"], timeout=1) as ser:
                ser.write((values["SEND_TXT"] + line_endings[values["LINE_END"]]).encode('utf-8'))
        except Exception as e:
            print("Error:", e)

    elif event == "REFRESH":
        window["PORT"].update(values=[port.device for port in serial.tools.list_ports.comports()])

    elif event == "CLEAR_CONSOLE":
        window["CONSOLE"].update(value="")

window.close()

# Optional: Remove the temporary .ico file after closing the window
os.remove(icon_filename)