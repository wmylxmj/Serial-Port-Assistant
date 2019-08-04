# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 17:06:02 2019

@author: wmy
"""

import serial
import serial.tools.list_ports
import time
import threading
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
from tkinter import messagebox
from tkinter import ttk

class SerialPortAssistant(object):
    
    def __init__(self):
        self.serial = serial.Serial()
        self.device = None
        self.baudrate = 9600
        self.encoding = "gb2312"
        self.recthread = None
        self.connecting = False
        self.comports = []
        self.devices = []
        self.search()
        self.interface()
        self.updatethread = threading.Thread(target=self.update)
        self.updatethread.start()
        pass
    
    def interface(self):
        self.root = tk.Tk()
        self.root.title('大咸鱼串口助手 V0.0.1')
        self.root.geometry('960x640')
        self.face = tk.Frame(self.root)
        self.face.config(height=640, width=960)
        self.face.propagate(False)
        self.face.pack(anchor='nw')
        # operate frame
        operateframe = tk.Frame(self.face)
        operateframe.config(height=220, width=960)
        operateframe.propagate(False)
        operateframe.pack(anchor='nw', side='bottom')
        operatespaceframe = tk.Frame(operateframe)
        operatespaceframe.config(height=220, width=10)
        operatespaceframe.propagate(False)
        operatespaceframe.pack(anchor='nw', side='left')
        # send text
        operatetextframe = tk.Frame(operateframe)
        operatetextframe.config(height=220, width=725)
        operatetextframe.propagate(False)
        operatetextframe.pack(anchor='nw', side='left')
        operatespaceframe = tk.Frame(operatetextframe)
        operatespaceframe.config(height=10, width=725)
        operatespaceframe.propagate(False)
        operatespaceframe.pack(anchor='nw', side='top')
        operatespaceframe = tk.Frame(operatetextframe)
        operatespaceframe.config(height=10, width=725)
        operatespaceframe.propagate(False)
        operatespaceframe.pack(anchor='sw', side='bottom')
        # operate right
        operateframeright = tk.Frame(operateframe)
        operateframeright.config(height=240, width=210)
        operateframeright.propagate(False)
        operateframeright.pack(anchor='nw', side='left')
        # send mode
        spacelabel = tk.Label(operateframeright, width=5, height=3)
        spacelabel.pack()
        self.hexsend = tk.BooleanVar()
        self.hexsendcheck = tk.Checkbutton(operateframeright, text='十六进制发送', \
                                              onvalue=True, offvalue=False, variable=self.hexsend)
        self.hexsendcheck.pack(side='top')
        # send botton
        spacelabel = tk.Label(operateframeright, width=5, height=1)
        spacelabel.pack()
        self.sendbutton = tk.Button(operateframeright, text='发送数据', \
                                    width=20, height=1, command=self.sendbuttoncmd)
        self.sendbutton.pack(side='top')
        # text
        self.sendtext = tk.Text(operatetextframe ,height=15, width=99, bg='white', fg="black") 
        self.sendscrollbar = tk.Scrollbar(operatetextframe)
        self.sendtext['yscrollcommand']=self.sendscrollbar.set
        self.sendscrollbar['command']=self.sendtext.yview
        self.sendtext.pack(side=tk.LEFT)
        self.sendscrollbar.pack(side='left', fill=tk.Y)
        # space frame
        spaceframe = tk.Frame(self.face)
        spaceframe.config(height=420, width=10)
        spaceframe.propagate(False)
        spaceframe.pack(anchor='nw', side='left')
        # text frame
        textframe = tk.Frame(self.face)
        textframe.config(height=420, width=725)
        textframe.propagate(False)
        textframe.pack(anchor='nw', side='left')
        # option frame
        optionframe = tk.Frame(self.face)
        optionframe.config(height=420., width=225)
        optionframe.propagate(False)
        optionframe.pack(anchor='ne', side='right')
        # text
        self.rectext = tk.Text(textframe ,height=35, width=99, bg='black', fg="#00FF00") 
        self.recscrollbar = tk.Scrollbar(textframe)
        self.rectext['yscrollcommand']=self.recscrollbar.set
        self.rectext.config(state=tk.DISABLED)
        self.recscrollbar['command']=self.rectext.yview
        self.rectext.pack(side=tk.LEFT, fill=tk.BOTH)
        self.recscrollbar.pack(side='left', fill=tk.Y)
        # option
        optionframebottom = tk.Frame(optionframe)
        optionframebottom.config(height=150., width=210)
        optionframebottom.propagate(False)
        optionframebottom.pack(anchor='sw', side='bottom')
        #left
        optionframeleft = tk.Frame(optionframe)
        optionframeleft.config(height=420., width=60)
        optionframeleft.propagate(False)
        optionframeleft.pack(anchor='nw', side='left')
        # right
        optionframeright = tk.Frame(optionframe)
        optionframeright.config(height=420., width=150)
        optionframeright.propagate(False)
        optionframeright.pack(anchor='nw', side='left')
        # serial
        spacelabel = tk.Label(optionframeleft, width=5, height=1)
        spacelabel.pack()
        label1 = tk.Label(optionframeleft, text="端口号", width=5, height=1)
        label1.pack()
        spacelabel = tk.Label(optionframeright, width=5, height=1)
        spacelabel.pack()
        self.serialselect = ttk.Combobox(optionframeright, width=15, height=5)
        self.serialselect.bind("<<ComboboxSelected>>", self.serialselectcmd)
        self.serialselect.pack()
        # baudrate
        spacelabel = tk.Label(optionframeleft, width=5, height=1)
        spacelabel.pack()
        label2 = tk.Label(optionframeleft, text="波特率", width=5, height=1)
        label2.pack()
        spacelabel = tk.Label(optionframeright, width=5, height=1)
        spacelabel.pack()
        self.baudrateselect = ttk.Combobox(optionframeright, width=15, height=8)
        self.baudrateselect.bind("<<ComboboxSelected>>", self.baudrateselectcmd)
        self.baudrateselect['value'] = [1382400, 921600, 460800, 256000, 230400, \
                           128000, 115200, 76800, 57600, 43000, 38400, 19200, 14400, \
                           9600, 4800, 2400, 1200]
        self.baudrateselect.current(13)
        self.baudrateselect.pack()
        # cal bit
        spacelabel = tk.Label(optionframeleft, width=5, height=1)
        spacelabel.pack()
        label3 = tk.Label(optionframeleft, text="校验位", width=5, height=1)
        label3.pack()
        spacelabel = tk.Label(optionframeright, width=5, height=1)
        spacelabel.pack()
        self.calbitselect = ttk.Combobox(optionframeright, width=15, height=8)
        self.calbitselect['value'] = ["无校验", "奇校验", "偶校验"]
        self.calbitselect.current(0)
        self.calbitselect.pack()
        # data bit
        spacelabel = tk.Label(optionframeleft, width=5, height=1)
        spacelabel.pack()
        label4 = tk.Label(optionframeleft, text="数据位", width=5, height=1)
        label4.pack()
        spacelabel = tk.Label(optionframeright, width=5, height=1)
        spacelabel.pack()
        self.databitselect = ttk.Combobox(optionframeright, width=15, height=8)
        self.databitselect['value'] = [8, 7, 6, 5]
        self.databitselect.current(0)
        self.databitselect.pack()
        # stop bit
        spacelabel = tk.Label(optionframeleft, width=5, height=1)
        spacelabel.pack()
        label5 = tk.Label(optionframeleft, text="停止位", width=5, height=1)
        label5.pack()
        spacelabel = tk.Label(optionframeright, width=5, height=1)
        spacelabel.pack()
        self.stopbitselect = ttk.Combobox(optionframeright, width=15, height=8)
        self.stopbitselect['value'] = [1]
        self.stopbitselect.current(0)
        self.stopbitselect.pack()
        # check
        self.hexdisplay = tk.BooleanVar()
        self.hexdisplaycheck = tk.Checkbutton(optionframebottom, text='十六进制显示', \
                                              onvalue=True, offvalue=False, variable=self.hexdisplay)
        self.hexdisplaycheck.pack()
        # open
        spacelabel = tk.Label(optionframebottom, width=5, height=1)
        spacelabel.pack()
        self.openbutton = tk.Button(optionframebottom, text='打开串口', \
                                    width=20, height=1, command=self.openbuttoncmd)
        self.openbutton.pack()
        #clear
        spacelabel = tk.Label(optionframebottom, width=5, height=1)
        spacelabel.pack()
        self.clearbutton = tk.Button(optionframebottom, text='清除接收', \
                                    width=20, height=1, command=self.clearbuttoncmd)
        self.clearbutton.pack()
        pass
    
    def clearbuttoncmd(self):
        self.rectext.config(state=tk.NORMAL)
        self.rectext.delete(1.0, tk.END)
        self.rectext.config(state=tk.DISABLED)
        self.rectext.update()
        pass
    
    def sendbuttoncmd(self):
        if self.connecting:
            data = self.sendtext.get(1.0, tk.END)
            if self.hexsend.get() == False:
                self.serial.write(data[0:-1].encode(self.encoding))
                pass
            else:
                hex_dict = {'0':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, \
                            '8':8, '9':9, 'A':10, 'a':10, 'B':11, 'b':11, 'C':12, \
                            'c':12, 'D':13, 'd':13, 'E':14, 'e':14, 'F':15, 'f':15}
                data = data.replace(' ', '')
                data = data.replace('\n', '')
                char = 0
                count = 0
                byte = b''
                for num in data:
                    try:
                        num = hex_dict[num]
                        pass
                    except:
                        tk.messagebox.showinfo(title='无法发送', message='输入错误')
                        return None
                    else:
                        count += 1
                        if count % 2 == 1:
                            char = num * 16
                            if count == len(data):
                                char = num
                                byte += bytes([char])
                                pass
                            pass
                        else:
                            char += num
                            byte += bytes([char])
                            pass
                        pass
                    pass
                self.serial.write(byte)
                pass
            pass
        else:
             tk.messagebox.showinfo(title='无法发送', message='请先打开串口')
             pass
        pass
    
    def baudrateselectcmd(self, *args):
        self.baudrate = int(self.baudrateselect.get())
        self.serial.baudrate = self.baudrate
        print(self.baudrate)
        pass
    
    def serialselectcmd(self, *args):
        self.device = self.serialselect.get().split()[0]
        self.serial.port = self.device
        print(self.device)
        pass
    
    def openbuttoncmd(self):
        if self.openbutton['text'] == '打开串口':
            is_open = self.serialopen()
            if is_open:
                self.openbutton['text'] = '关闭串口'
                pass
            pass
        else:
            self.serialclose()
            self.openbutton['text'] = '打开串口'
            pass
        pass
    
    def search(self):
        self.devices = []
        self.comports = list(serial.tools.list_ports.comports())
        for comport in self.comports:
            self.devices.append(comport.device)
            pass
        pass
    
    def update(self):
        while True:
            if self.connecting == False:         
                self.search()
                self.serialselect['value'] = self.comports
                if len(list(self.serialselect['value'])) == 0:
                    self.serialselect['value'] = [""]
                    self.serialselect.current(0)
                    self.device = None
                    pass
                elif self.device == None or self.device not in self.devices:        
                    self.serialselect.current(0)
                    self.device = self.devices[0]
                    pass
                self.serialselect.update()
                self.face.update_idletasks()
                pass
            pass
        pass
    
    def serialopen(self):
        self.serial.port = self.device
        self.serial.baudrate = self.baudrate
        self.serial.timeout = 2
        try:
            self.serialclose()
            time.sleep(0.1)
            self.serial.open()
        except Exception as error:
            tk.messagebox.showinfo(title='无法连接到串口', message=error)
            return False
        else:
            if self.serial.isOpen():
                self.connecting = True
                self.recthread = threading.Thread(target=self.receive)
                self.recthread.start()
                return True
            else:
                return False
            pass
        pass
    
    def serialclose(self):
        self.connecting = False
        time.sleep(0.1)
        self.serial.close()
        pass
    
    def receive(self):
        while self.connecting:
            try:
                nchar = self.serial.inWaiting()
                pass
            except:
                self.connecting = False
                self.serialclose()
                self.openbutton['text'] = '打开串口'
                pass
            if nchar:
                if self.hexdisplay.get() == False:
                    data = ''.encode('utf-8')
                    data = data + self.serial.read(nchar)
                    try:
                        self.rectext.config(state=tk.NORMAL)
                        self.rectext.insert(tk.END, data.decode(self.encoding))
                        self.rectext.config(state=tk.DISABLED)
                        self.rectext.yview_moveto(1)
                        self.rectext.update()
                        pass
                    except:
                        pass
                    pass
                else:
                    data = self.serial.read(nchar)
                    convert = '0123456789ABCDEF'
                    string = ''
                    for char in data:
                        string += convert[char//16] + convert[char%16] + ' '
                        pass
                    self.rectext.config(state=tk.NORMAL)
                    self.rectext.insert(tk.END, string)
                    self.rectext.config(state=tk.DISABLED)
                    self.rectext.yview_moveto(1)
                    self.rectext.update()
                    pass
                pass
            pass
        pass
    
    def run(self):
        self.root.mainloop()
        self.exit()
        pass
    
    def exit(self):
        self.serialclose()
        pass
    
    pass
    

if __name__ == '__main__':
    assistant = SerialPortAssistant()
    assistant.run()