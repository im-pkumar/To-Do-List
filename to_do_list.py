from tkinter import *
from tkinter import messagebox, Text, Checkbutton
from tkinter.ttk import Scrollbar
import threading
from PIL import Image, ImageTk
from datetime import datetime as dt
import os
import sqlite3 as slite


colors = {'main_bg': "#048283", 'white': "#FFFFFF", 'light':"#AAF6F7", 'dark_light':"#55D9DB"}
main_f = None
task_f = None
slno = []

win = Tk()
win.title("To-Do List")
icon = PhotoImage(file = f"{os.getcwd()}/images/icon.png")
win.iconphoto(False, icon)
win.configure(bg = colors["main_bg"])
win.geometry("750x650")
win.resizable(False, False)

w = Label(win, text = "Welcome to your To-Do List Dairy!! ", font = ("Sans Serif", 24, "bold"), fg = colors['white'], bg = colors['main_bg'])
w.place(relx = 0.15, rely = 0.1)

welcome_image = PhotoImage(file = f"{os.getcwd()}/images/welcome.png")
w_image = Label(win, image = welcome_image, bg = colors['main_bg'])
w_image.image = welcome_image
w_image.place(relx = 0.05, rely = 0.25)

#   ******************************************** Database Creation to store to-do list ******************************************************

try:
    con = slite.Connection(database = "todolist.sqlite3")
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE todotask (
            slno INTEGER PRIMARY KEY,
            date DATETIME NOT NULL,
            to_dotask TEXT NOT NULL,
            completed VARCHAR(3)
        )
    """)
    con.commit()
except Exception as e:
    print("Something went wrong! Might be table already created.")
finally: 
    con.close()

#   *********************************************** This is to Delete Task of To-Do List ********************************************************

def delete_task():
    global task_f, main_f
    if task_f != None: task_f.destroy()

    global vars_list, slno
    to_del = []
    for var, value in zip(vars_list, slno):
        print("Sl No.", var, value) 
        if var.get() == 1:  
            to_del.append(value)
    print(to_del)

    if len(to_del) >= 1:
        task_f = Frame(main_f)
        task_f.configure(bg = colors['light'], highlightthickness = 1, highlightbackground = colors['main_bg'])
        task_f.place(relx = 0.275, rely = 0.15, relheight = 0.825, relwidth = 0.7)

        res = messagebox.askokcancel(title="Deletion Warning", message="Do you really want to delete the records in To-Do List")
    
        if res:
            placeholders = ', '.join('?' for _ in to_del)
            query = f"DELETE FROM todotask WHERE slno IN ({placeholders})"
            
            # Deleting the selected Tasks from Record - DataBase Updation
            con = slite.Connection(database = "todolist.sqlite3")
            cur = con.cursor()
            cur.execute(query, (tuple(to_del)))
            con.commit()
            con.close()
            print("Deleted")
            messagebox.showinfo(title = 'Message', message = "Successfully deleted the selected records!")
            task_f.destroy()
            to_del = []
            viewtask()

        else:
            print("Not Deleted!")
            messagebox.showinfo(title = 'Message', message = "Deletion of records Cancelled!")
            task_f.destroy()
            to_del = []
            viewtask()
    else:
        messagebox.showinfo(title = "Message", message = "No Task in To-Do List is Selected to Delete.")
        to_del = []
        viewtask()
        

#   *********************************************** This is to View All Task of To-Do List ********************************************************

def viewtask():
    global task_f, main_f, slno, vars_list
    if task_f != None: 
        task_f.destroy()
    slno = []
    vars_list = []

    task_f = Frame(main_f)
    task_f.configure(bg = colors['light'], highlightthickness = 1, highlightbackground = colors['main_bg'])
    task_f.place(relx = 0.275, rely = 0.15, relheight = 0.825, relwidth = 0.7)
    
    canvas = Canvas(task_f, bg = colors['light'], highlightthickness = 1, highlightbackground = colors['main_bg'])
    canvas.configure(bg = colors['light'], bd = 0)
    canvas.pack(side = LEFT, fill = 'both', expand = True)

    scrollbar_y = Scrollbar(task_f, orient = "vertical", command = canvas.yview)
    scrollbar_y.pack(side = "right", fill = "y")
    
    canvas.configure(yscrollcommand = scrollbar_y.set)    
    
    scrollable_f = Frame(canvas, bg = colors['light'])
    canvas.create_window((0, 0), window = scrollable_f, anchor="nw")
    
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    # Bind the configure event to update scroll region
    scrollable_f.bind("<Configure>", on_frame_configure)
    
    # get all task-data from database
    con = slite.Connection(database = "todolist.sqlite3")
    cur = con.cursor()
    cur.execute("select * from todotask")
    data = cur.fetchall()
    con.close()
    
    for i in range(len(data)):
        slno.append(data[i][0])
    
    # List to hold IntVar objects
    vars_list = [IntVar() for _ in slno]
    print(vars_list)
    print(slno)

    i = 0
    for var, n in zip(vars_list, slno):
        d = data[i]
        view_f = Frame(scrollable_f, bg = colors['light'], width = 700, height = 5)
        #view_f.grid_propagate(False)
        view_f.grid(row = i, column = 0, padx = 2, pady = 5)
        
        showdate = Label(view_f, text = d[1], font = ("Verdana", 12, "bold"), fg = colors['main_bg'], bg = colors['light'], width = 42)
        showdate.grid(row = 0, column = 1, pady = 5)
               
        chk_b = Checkbutton(view_f, text = "", variable = var, bg = colors['light'])
        chk_b.grid(row = 1, column = 0)
        
        msg_l = Label(view_f, text = d[2], wraplength = 475, font = ("Comic Sans MS", 14, "normal"), fg = colors['main_bg'], bg = colors['light'])
        msg_l.grid(row = 1, column = 1)
        
        complt_l= Label(view_f, text = f"Completed : {d[3]}" , font = ("Comic Sans MS", 12, "normal"), bg = colors['light'], fg = colors['main_bg'], width = 42)
        complt_l.grid(row = 2, column = 1)
        i+=1

#   *********************************************** End of View All Task of To-Do List ***********************************************************




#   *********************************************** This is to Update Task of To-Do List ********************************************************

#   Database updation function
def update_db(to_upd, msg, chk_var):
    s = msg.get("1.0", "end-1c")
    ck = "Yes" if chk_var.get() else "No"        
    
    # Getting data of selected SlNo from Database
    con = slite.Connection(database = "todolist.sqlite3")
    cur = con.cursor()
    cur.execute(f"UPDATE todotask SET to_dotask = ?, completed = ? WHERE slno = ?", (s, ck, to_upd[0]))
    con.commit()
    con.close()

    print("Updated Task")
    messagebox.showinfo("Message", message="Task Updated Successfully!!")
    global slno, vars_list
    task_f.destroy()
    to_upd = []
    viewtask()

def update():
    global task_f, vars_list, slno
    if task_f != None: task_f.destroy()

    # to get which data to update
    to_upd = []
    for var, value in zip(vars_list, slno):
        print("Upd Sl No.", var, value) 
        if var.get() == 1:  
            to_upd.append(value)
    print(to_upd)
    
    # Checking whether any data is selected for updation or not, and then proceed.
    if len(to_upd) == 0: 
        messagebox.showinfo(title="Message", message = "No Task Selected to Update. Please select the Task in To-Do List & then Update!")
        task_f.destroy()
        slno = []
        viewtask()
    elif len(to_upd) > 1: 
        messagebox.showinfo(title="Message", message = "Please Select only One Task to Update.")
        task_f.destroy()
        to_upd = []
        viewtask()
    else:        
        task_f = Canvas(main_f)
        task_f.configure(bg = colors['dark_light'], highlightthickness = 1, highlightbackground = colors['main_bg'])
        task_f.place(relx = 0.275, rely = 0.295, relheight = 0.5, relwidth = 0.7)    
        
        # Getting data of selected SlNo from Database
        con = slite.Connection(database = "todolist.sqlite3")
        cur = con.cursor()
        cur.execute(f"SELECT * FROM todotask WHERE slno = {to_upd[0]}")
        data = cur.fetchone()
        con.close()

        showdate = Label(task_f, text = data[1], font = ("Verdana", 12, "bold"), fg = colors['main_bg'], bg = colors['dark_light'])
        showdate.grid(row = 0, column = 0, padx = 30, pady = 5)

        msg = Text(task_f, font = ("Comic Sans MS", 12, "normal"), fg = colors['main_bg'], bg = colors['white'], width = 45, height = 8)
        msg.insert(END, data[2])
        msg.grid(row = 1, column = 0, padx = 30)

        if data[3] == 'No':
            chk_var = IntVar(value = 0)
        else: chk_var = IntVar(value = 1)
        chk_b = Checkbutton(task_f, text = "Completed", variable = chk_var, font = ("Comic Sans MS", 12, "normal"), bg = colors['dark_light'], 
                            fg = colors['main_bg'] )
        chk_b.grid(row = 2, column = 0, padx = 30)

        save_b = Button(task_f, text = "Save", command = lambda: update_db(to_upd, msg, chk_var), font = ("Comic Sans MS", 14, "normal"), bg = colors['main_bg'], 
                        fg = colors['white'], bd = 1, width = 14)
        save_b.grid(row = 3, column = 0, pady = 5)

#   *********************************************** End Of Update Task of To-Do List ********************************************************



#   *********************************************** This is to FAQs of To-Do List ********************************************************

def faqs():
    faq_title = "FAQ for To-Do List App"
    
    global task_f, main_f
    if task_f != None: task_f.destroy()

    task_f = Frame(main_f)
    task_f.configure(bg = colors['light'], highlightthickness = 1, highlightbackground = colors['main_bg'])
    task_f.place(relx = 0.275, rely = 0.15, relheight = 0.825, relwidth = 0.7)
    
    canvas = Canvas(task_f, bg = colors['light'], highlightthickness = 1, highlightbackground = colors['main_bg'])
    canvas.configure(bg = colors['light'], bd = 0)
    canvas.pack(side = LEFT, fill = 'both', expand = True)

    scrollbar_y = Scrollbar(task_f, orient = "vertical", command = canvas.yview)
    scrollbar_y.pack(side = "right", fill = "y")
    
    canvas.configure(yscrollcommand = scrollbar_y.set)    
    
    scrollable_f = Frame(canvas, bg = colors['light'])
    canvas.create_window((0, 0), window = scrollable_f, anchor="nw")
    
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    # Bind the configure event to update scroll region
    scrollable_f.bind("<Configure>", on_frame_configure)

    faq_l = Label(scrollable_f, text = faq_title, wraplength = 450, font = ("Comic Sans MS", 14, "bold"), fg = colors['main_bg'], bg = colors['light'])
    faq_l.grid(row = 0, column = 0, pady = 10)

    with open(f"{os.getcwd()}/faq.txt", "r") as file:
        for i in range(1, 9, 2):
            q = file.readline()
            a = file.readline()

            q_l = Label(scrollable_f, text = q, wraplength = 500, font = ("Comic Sans MS", 12, "bold"), fg = colors['main_bg'], bg = colors['light'], anchor='w')
            q_l.grid(row = i, column = 0, padx = 4, pady = (10, 0), sticky='w')

            a_l = Label(scrollable_f, text = a, wraplength = 500, font = ("Comic Sans MS", 12, "normal"), fg = colors['main_bg'], bg = colors['light'], anchor='w')
            a_l.grid(row = i+1, column = 0, padx = 4, pady = (0, 0), sticky='w')

#   *********************************************** End of FAQs for To-Do List ********************************************************




#   *********************************************** This is to Add New Task to To-Do List ********************************************************

def newtask():
    global task_f
    if task_f != None: task_f.destroy()

    task_f = Canvas(main_f)
    task_f.configure(bg = colors['dark_light'], highlightthickness = 1, highlightbackground = colors['main_bg'])
    task_f.place(relx = 0.275, rely = 0.295, relheight = 0.5, relwidth = 0.7)
    
    def cancel():
        print("New task add is cancelled. Not saved!!")
        task_f.destroy()
        viewtask()

    def save_record():
        tarikh = dt.now().strftime("%B %d, %Y, %I:%M %p")
        global msg_e
        print(msg_e.get("1.0", "end-1c"))
        
        # database updation for new to-do list
        con = slite.Connection(database = "todolist.sqlite3")
        cur = con.cursor()
        cur.execute("INSERT INTO todotask (date, to_dotask, completed) VALUES (?, ?, ?)", (tarikh, msg_e.get("1.0", "end-1c"), "No"))
        con.commit()
        con.close()
        messagebox.showinfo("Message: Add Task", message = "New To-Do List successfully recorded!!")
        task_f.destroy()
        viewtask()

    def task():
        tarikh = dt.now().strftime("%B %d, %Y, %I:%M %p")
        showdate = Label(task_f, text = tarikh, font = ("Verdana", 12, "bold"), fg = colors['main_bg'], bg = colors['dark_light'])
        showdate.grid(row = 0, column = 1)
        
        global msg_e
        msg_e = Text(task_f, font = ("Comic Sans MS", 12, "normal"), fg = colors['main_bg'], bg = colors['white'], width = 45, height = 9)
        msg_e.grid(row = 1, column = 1)

        btn_f = Frame(task_f, bg = colors['dark_light'])
        btn_f.place(relx = 0.15, rely = 0.775, relheight = 0.2, relwidth = 0.7)

        save_b = Button(btn_f, text = "Save", command = save_record, font = ("Comic Sans MS", 14, "normal"), bg = colors['main_bg'], fg = colors['white'], bd = 1, width = 14)
        save_b.grid(row = 1, column = 0, pady = 10, padx = (5, 10))
        cancel_b = Button(btn_f, text = "Cancel", command = cancel, font = ("Comic Sans MS", 14, "normal"), bg = colors['main_bg'], fg = colors['white'], bd = 1, width = 14)
        cancel_b.grid(row = 1, column = 1, pady = 10, padx = (10, 5))

    addtask_b = Button(task_f, text = "+", font = ("Verdana", 10, "bold"), fg = colors['white'], bg = colors['dark_light'], command=task)
    addtask_b.grid(row=0, column=0, padx = 5, pady = 5)


#   *********************************************** This is Main Screen of To-Do List App ************************************************

def mainscreen():
    global main_f
    main_f = Canvas(win)
    main_f.configure(bg = colors['main_bg'], highlightthickness = 1, highlightbackground = colors['main_bg'])
    main_f.place(relx = 0, rely = 0, relheight = 1, relwidth = 1)

    banner_image = PhotoImage(file = f"{os.getcwd()}/images/banner.png")
    b_image = Label(main_f, text = "To-Do List Banner", image = banner_image, bg = colors['main_bg'])
    b_image.image = banner_image
    b_image.place(relx = 0.025, rely = 0)

    button_f = Frame(main_f)
    button_f.configure(bg = colors['main_bg'])
    button_f.place(relx = 0.025, rely = 0.3, relheight = 0.5, relwidth = 0.257)

    view_b = Button(button_f, text = "View All", command = viewtask, font = ("Comic Sans MS", 14, "normal"), fg = colors['main_bg'], bg = colors['light'], bd = 1, width = 14)
    view_b.grid(row = 0, column = 0, pady = 10, padx = 0)

    new_b = Button(button_f, text = "New Task", command = newtask, font = ("Comic Sans MS", 14, "normal"), fg = colors['main_bg'], bg = colors['light'], bd = 1, width = 14)
    new_b.grid(row = 1, column = 0, pady = 10, padx = 0)

    update_b = Button(button_f, text = "Update", command = update, font = ("Comic Sans MS", 14, "normal"), fg = colors['main_bg'], bg = colors['light'], bd = 1, width = 14)
    update_b.grid(row = 2, column = 0, pady = 10)

    delete_b = Button(button_f, text = "Delete", command = delete_task, font = ("Comic Sans MS", 14, "normal"), fg = colors['main_bg'], bg = colors['light'], bd = 1, width = 14)
    delete_b.grid(row = 3, column = 0, pady = 10)

    faq_b = Button(button_f, text = "FAQs", command = faqs, font = ("Comic Sans MS", 14, "normal"), fg = colors['main_bg'], bg = colors['light'], bd = 1, width = 14)
    faq_b.grid(row = 4, column = 0, pady = 10)


t = threading.Timer(3, mainscreen)
t.start()

win.mainloop()