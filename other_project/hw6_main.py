import sqlite3
import rsa_homework as rsa
import base64
import hashlib
import json
import tkinter as tk
import numpy as np
from tkinter import messagebox
import tkinter.filedialog as tkf
import threading
'''
This script use the last rsa assignment code, this script create a GUI for the user to log in and use the encryption
and decryption function. The user can either encrypt/decrypt a file or just encrypt/decrypt a message using the text
widgets provided
'''


def login():
    '''
    this is the function for the login. provide the user with login GUI and register function
    :return: no return
    '''
    # this create the entry box and necessary label for the login GUI
    root = tk.Tk()
    root.title("LOGIN GUI")
    tk.Label(root, text="username: ").grid(row=1)
    tk.Label(root, text="password: ").grid(row=2)
    e1 = tk.Entry(root)
    e1.grid(row=1, column=1, padx=5, pady=5)
    e2 = tk.Entry(root, show='*')
    e2.grid(row=2, column=1, padx=5, pady=5)
    e3 = tk.Entry(root, show='*')
    label = tk.Label(text="reenter password: ")
    database = "userinfo.db"

    def sign_in():
        '''
        this is the sub function to deal with the user sign in, it will compare the user input is correct or not
        :return: no return
        '''
        # connect to the user info database
        db = sqlite3.connect(database)
        # hash the user input and compare the hash is the same or not
        user = hashlib.sha256()
        passw = hashlib.sha256()
        user.update((('sdfja54sadgwe32D' + e1.get()).encode('utf-8')))
        passw.update((('sdfja54sadgwe32D' + e2.get()).encode('utf-8')))
        username = user.hexdigest()
        password = passw.hexdigest()
        confirm = list(db.execute("select * from users where username = ?", (username,)))
        if not confirm:
            messagebox.showerror('error', "Wrong username password combination!!!")
        else:
            if password == confirm[0][1]:
                root.destroy()
                rsa_gui(username, password)
            else:
                messagebox.showerror('error', 'Wrong username password combination!!!')
        pass

    def sign_up():
        '''
        pre process the user sign up request, show another password confirmation entry box
        :return: no return
        '''
        label.grid(row=3, column=0)
        e3.grid(row=3, column=1)
        bt2.config(text="register", command=reg)

    def reg():
        '''
        this the main function deal with the user register.
        :return:
        '''
        # connect to the database
        db = sqlite3.connect(database)
        # to make sure the user didn't input a password he/she doesn't want
        if e2.get() == e3.get():
            # if the two time entry are the same then can move on to the register process
            user = hashlib.sha256()
            passw = hashlib.sha256()
            user.update((('sdfja54sadgwe32D' + e1.get()).encode('utf-8')))
            passw.update((('sdfja54sadgwe32D' + e2.get()).encode('utf-8')))
            username = user.hexdigest()
            password = passw.hexdigest()
            # to make sure the username is unique
            only = list(db.execute("select * from users where username = ?", (username,)))
            if only:
                messagebox.showerror('error', 'This username has already been taken, please try another username')
            else:
                # insert the hashed username and password into the database
                db.execute('insert into users values (?, ?)', (username, password))
                db.commit()
                db.close()
                messagebox.showinfo('Done', "register Done!")
            e1.delete(0, tk.END)
            e2.delete(0, tk.END)
            e3.delete(0, tk.END)
            e3.grid_remove()
            label.grid_remove()
            bt2.config(text='sign up', command=sign_up)
        else:
            messagebox.showerror('error!!', "Inconsistent password")

    bt1 = tk.Button(root, text='login', command=sign_in)
    bt2 = tk.Button(root, text="signup", command=sign_up)
    bt3 = tk.Button(root, text="exit", command=root.destroy)
    bt1.grid(row=4, column=2)
    bt2.grid(row=4, column=0)
    bt3.grid(row=4, column=1)
    root.mainloop()


def rsa_gui(username, password):
    '''
    this is the main function to deal with rsa encryption and decryption
    :param username: the hashed username
    :param password: the hashed password
    :return: no return
    '''
    database = 'userinfo.db'
    db = sqlite3.connect(database)
    confirm = list(db.execute("select * from users where username = ?", (username, )))
    # to make sure is authorized user to use this function
    if confirm[0][1] == password:
        # create the necessary component for the GUI
        root22 = tk.Tk()
        var1 = tk.IntVar()
        tk.Checkbutton(root22, text='use default key', variable=var1).pack()
        var2 = tk.IntVar()
        tk.Checkbutton(root22, text='encrypt/decrypt a file or not', variable=var2).pack()
        lb4 = tk.Label(text="Please enter a number you want the key generate from: ")
        lb4.pack()
        e3 = tk.Entry(root22)
        e3.pack()
        lb = tk.Label(root22, text='Please input message in the following box:')
        lb.pack()
        e1 = tk.Text(root22, height=10)
        e1.pack()
        lb2 = tk.Label(root22, text='''The encrypted / decrypted message is in the following box:\n
        (If you decrypt a message just copy paste all the result from encryption)''')
        lb2.pack()
        e2 = tk.Text(root22, height=10)
        e2.pack()
        lb3 = tk.Label(root22, text='')
        lb3.pack()

        def encrypt():
            '''
            this is the function will triggered after click the encrypt button
            :return: no return
            '''
            try:
                e2.delete('1.0', 'end')
                # according to the user's choice to deal the user's demand
                if var1.get() == 1:
                    n, d, e = rsa.generate_key(1, int(base64.b64decode(b'MTIzNA==')))
                else:
                    n, d, e = rsa.generate_key(1, int(e3.get()))
                if var2.get() == 1:
                    file_name = tkf.askopenfilename()
                    try:
                        # use threading to overcome the GUI not response problem
                        a = file_name[0]
                        thread = threading.Thread(target=rsa.encrypt, args=(file_name, e, n, lb3))
                        thread.setDaemon(True)
                        thread.start()
                    except IndexError:
                        lb3.config(text="Please choose a file")
                else:
                    # use threading to overcome the GUI not response problem
                    thread = threading.Thread(target=sub_process_en, args=(e, n))
                    thread.setDaemon(True)
                    thread.start()
            except ValueError:
                lb3.config(text="Please enter a number you want the key generate from!!!")

        def log_out():
            '''
            This is the log out function to back to login GUI
            :return: no return
            '''
            root22.destroy()
            login()

        def decrypt():
            '''
            this is the function will triggered after click the decrypt button
            :return:
            '''
            try:
                e2.delete('1.0', 'end')
                if var1.get() == 1:
                    n, d, e = rsa.generate_key(1, int(base64.b64decode(b'MTIzNA==')))
                else:
                    n, d, e = rsa.generate_key(1, int(e3.get()))
                if var2.get() == 1:
                    file_name = tkf.askopenfilename()
                    try:
                        # use threading to overcome the GUI not response problem
                        a = file_name[0]
                        file_type = 'txt'
                        thread = threading.Thread(target=rsa.decrypt, args=(file_name, file_type, d, n, lb3))
                        thread.setDaemon(True)
                        thread.start()
                    except IndexError:
                        lb3.config(text="Please choose a file")
                else:
                    # use threading to overcome the GUI not response problem
                    thread = threading.Thread(target=sub_process_de, args=(d, n))
                    thread.setDaemon(True)
                    thread.start()
            except ValueError:
                lb3.config(text="Please enter a number you want the key generate from!!!")

        def sub_process_de(d, n):
            '''
            this is the sub process for the threading when just decrypt text form text box
            :param d: rsa key
            :param n: rsa key
            :return: no return
            '''
            lb3.config(text="Decryption in progress.....")
            result = []
            for i in json.loads(e1.get("1.0", tk.END)):
                dct = i ** d
                dtc = int(np.mod(dct, n))
                data = chr(dtc)
                result.append(data)
            e2.insert(tk.END, ''.join(result))
            lb3.config(text="Decryption Done!!")

        def sub_process_en(e, n):
            '''
            This is the sub process for the encryption process when just encrypt the text form text box
            :param e: rsa key
            :param n: rsa key
            :return: no return
            '''
            lb3.config(text="Encryption in progress.....")
            result = []
            for i in e1.get("1.0", tk.END):
                etc = ord(i)
                etc = etc ** e
                etc = int(np.mod(etc, n))
                result.append(etc)
            e2.insert(tk.END, json.dumps(result))
            lb3.config(text="Encryption Done!!")

        bt1 = tk.Button(root22, text='encrypt', command=encrypt)
        bt1.pack(padx=5, pady=10, side=tk.LEFT)
        bt2 = tk.Button(root22, text='decrypt', command=decrypt)
        bt2.pack(padx=5, pady=20, side=tk.LEFT)
        bt3 = tk.Button(root22, text='log out', command=log_out)
        bt3.pack(padx=5, pady=20, side=tk.LEFT)
        root22.mainloop()
    else:
        quit(0)


if __name__ == "__main__":
    login()
