from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image
import json

p = lambda:None
CwaDataToIotCore_json = 'D:/FuelProject/resources/parameters.json'
with open(CwaDataToIotCore_json) as f:
    json_data = f.read()
    #print(json_data)
    p.__dict__ = json.loads(json_data)
    f.close()

UserId=p.UserId
pump_name=p.pump_name
issues=p.Today_total_full_issues
transactions=p.Toatl_Transactions
Nozil_status=p.Nozil_status
dispenser_No=p.dispenser_no
Nozil_No=p.Nozil_no
price=p.Price
density=p.density
Fuel=p.Fuel_type
 
# Login window
def login_window():
    # Create the window and set it to full screen
    login = Tk()
    login.title("Login")
    login.attributes('-fullscreen', True)
    login.configure(bg="white")
    
    # Load the logo image
    logo_image = Image.open("logo.png")

    # Resize the image to fit the window
    logo_image = logo_image.resize((400, 400), Image.ANTIALIAS)

    # Convert the image to a Tkinter PhotoImage
    logo_photo = ImageTk.PhotoImage(logo_image)

    # Create a label to display the logo
    logo_label = Label(login, image=logo_photo, bg="white")
    logo_label.pack(side=TOP, pady=0.001)

    # Create the login form
    username_label = Label(login, text="Username:", bg="white", font=("Helvetica", 12))
    password_label = Label(login, text="Password:", bg="white", font=("Helvetica", 12))
    username_entry = Entry(login, width=25, font=("Helvetica", 12))
    password_entry = Entry(login, width=25, show="*", font=("Helvetica", 12))
    login_status_label = Label(login, text="", bg="white", font=("Helvetica", 12))
    
    username_label.pack(pady=10)
    username_entry.pack()
    password_label.pack(pady=10)
    password_entry.pack()
    login_status_label.pack(pady=10)

    def login_action():
        # Authenticate user credentials here
        if username_entry.get()=="admin" and password_entry.get()=="admin123":
            login.destroy()
            if UserId != None:
                dashboard_window()
        else:
            login_status_label.config(text="Invalid username or password")

    # Exit the application
    def exit_app():
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            login.destroy()

    Button(login, text="Login", bg="#0B5394", fg="white", font=("Helvetica", 12), command=login_action).pack(pady=20)
    
    # Add an exit button to quit the application
    exit_button = Button(login, text="Exit", bg="red", fg="white", font=("Helvetica", 12), command=exit_app)
    exit_button.pack(side=BOTTOM, pady=10)

    login.mainloop()
def settings_window(dashboard):
    settings = Tk()
    settings.title("Settings")
    settings.attributes('-fullscreen', True)
    settings.configure(bg="white")
    
    # Create the Frames
    button_frame1 = Frame(settings)
    details_frame1 = Frame(settings)
    
    # Create the settings and logout buttons
    settings_btn = Button(button_frame1, text="Settings", bg="blue", fg="white", font=("Arial", 14),command=settings_window)
    logout_btn = Button(button_frame1, text="Logout", bg="red", fg="white", font=("Arial", 14), command=lambda: [settings.destroy(),dashboard.destroy(),login_window()])
    
    # Pack the buttons inside the frame
    settings_btn.pack(side="left", padx=10, pady=10)
    logout_btn.pack(side="left", padx=10, pady=10)
    
    # Place the frame at the top right corner of the window
    button_frame1.place(relx=1.0, x=-10, y=10, anchor="ne")
    
    # # Create the User Id label 
    # id_label = Label(settings, text="Login User id : {}".format(UserId), bg="white", font=("Helvetica", 24))
    # id_label.pack(side="top", padx=30, pady=50)
    
    # Create the login form
    id_label = Label(settings, text="Login User id:", bg="white", font=("Helvetica", 12))
    id_entry = Entry(settings, width=25, font=("Helvetica", 12))
    pumpname_label = Label(settings, text="pump_name:", bg="white", font=("Helvetica", 12))
    pumpname_entry = Entry(settings, width=25, font=("Helvetica", 12))
    dispenser_label = Label(settings, text="dispenser_no:", bg="white", font=("Helvetica", 12))
    dispenser_entry = Entry(settings, width=25, font=("Helvetica", 12))
    nozil_label = Label(settings, text="Nozil_No:", bg="white", font=("Helvetica", 12))
    nozil_entry = Entry(settings, width=25, font=("Helvetica", 12))
    price_label = Label(settings, text="dispenser_no:", bg="white", font=("Helvetica", 12))
    price_entry = Entry(settings, width=25, font=("Helvetica", 12))
    density_label = Label(settings, text="density:", bg="white", font=("Helvetica", 12))
    density_entry = Entry(settings, width=25, font=("Helvetica", 12))
    Fuel_label = Label(settings, text="Fuel Type:", bg="white", font=("Helvetica", 12))
    Fuel_entry = Entry(settings, width=25, font=("Helvetica", 12))
    
    id_label.pack(pady=10)
    id_entry.pack()
    pumpname_label.pack(pady=10)
    pumpname_entry.pack()
    dispenser_label.pack(pady=10)
    dispenser_entry.pack()
    nozil_label.pack(pady=10)
    nozil_entry.pack()
    price_label.pack(pady=10)
    price_entry.pack()
    density_label.pack(pady=10)
    density_entry.pack()
    Fuel_label.pack(pady=10)
    Fuel_entry.pack()
    
    def save_action():
        # save user data here
        id=id_entry.get()
        pump_name=pumpname_entry.get()
        dispenser_No=dispenser_entry.get()
        Nozil_No=nozil_entry.get()
        price=price_entry.get()
        density=density_entry.get()
        Fuel=Fuel_entry.get()
        print("id :{},pump_name : {},dispenser_No :{},Nozil_No : {},price : {},density {},Fuel : {}".format(id,pump_name,dispenser_No,Nozil_No,price,density,Fuel))

    Button(settings, text="Save", bg="#0B5394", fg="white", font=("Helvetica", 12), command=save_action).pack(pady=20)
    
    
    # # Create the details Frame label
    # pump_label = Label(details_frame1, text=" pump_name : {}".format(pump_name), bg="white", font=("Helvetica", 24))
    # pump_label.grid(row=1, column=0, padx=30, pady=10)
    
    # dispenser_label = Label(details_frame1, text=" dispenser_no : {}".format(dispenser_No), bg="white", font=("Helvetica", 24))
    # dispenser_label.grid(row=2, column=0, padx=30, pady=10)
    
    # nozil_label = Label(details_frame1, text=" nozil_no : {}".format(Nozil_No), bg="white", font=("Helvetica", 24))
    # nozil_label.grid(row=3, column=0, padx=30, pady=10)
    
    # price_label = Label(details_frame1, text=" price : {}".format(price), bg="white", font=("Helvetica", 24))
    # price_label.grid(row=4, column=0, padx=30, pady=10)
    
    # density_label = Label(details_frame1, text=" density : {}".format(density), bg="white", font=("Helvetica", 24))
    # density_label.grid(row=5, column=0, padx=30, pady=10)
    
    # Fuel_label = Label(details_frame1, text=" Fuel_type : {}".format(Fuel), bg="white", font=("Helvetica", 24))
    # Fuel_label.grid(row=6, column=0, padx=30, pady=10)
    
    # save_btn = Button(details_frame1, text="save", bg="blue", fg="white", font=("Arial", 14))
    # save_btn.grid(row=7, column=0, padx=50, pady=10)
    
    # # Place the frame at the middle of the window
    # details_frame1.place(relx=0.3,rely=0.2,x=10,y=5)
    

# Dashboard window
def dashboard_window():
    # Create the window and set it to full screen
    dashboard = Tk()
    dashboard.title("Dashboard")
    dashboard.attributes('-fullscreen', True)
    dashboard.configure(bg="white")

    # Create a frame to hold the buttons
    button_frame = Frame(dashboard)
    details_frame = Frame(dashboard)
    pump_detail_frame = Frame(dashboard)

    def settings():
        settings_window(dashboard)
    # Create the settings and logout buttons
    settings_btn = Button(button_frame, text="Settings", bg="blue", fg="white", font=("Arial", 14),command=settings) #(command=settings)
    logout_btn = Button(button_frame, text="Logout", bg="red", fg="white", font=("Arial", 14), command=lambda: [dashboard.destroy(), login_window()])

    # Pack the buttons inside the frame
    settings_btn.pack(side="left", padx=10, pady=10)
    logout_btn.pack(side="left", padx=10, pady=10)
    

    # Place the frame at the top right corner of the window
    button_frame.place(relx=1.0, x=-10, y=10, anchor="ne")
    
    userId_label = Label(dashboard, text="Login User id : {} ".format(UserId), bg="white", font=("Helvetica", 24))
    userId_label.pack(side="top", padx=40, pady=120)
    
    issue_label = Label(details_frame, text="Today Total Full issues : {} ".format(issues), bg="white", font=("Helvetica", 18))
    issue_label.grid(row=0, column=0, padx=10, pady=10)

    transaction_label = Label(details_frame, text="Today Transactions : {} ".format(transactions), bg="white", font=("Helvetica", 18))
    transaction_label.grid(row=0, column=1, padx=10, pady=10)

    nozil_label = Label(details_frame, text="nozil status : {}".format(Nozil_status), bg="white", font=("Helvetica", 18))
    nozil_label.grid(row=0, column=2, padx=10, pady=10)
    
    details_frame.place(relx=0.25,rely=0.3)
        
    # create a frame for the labels
    details_frame = Frame(dashboard)
    details_frame.pack(side=LEFT, padx=10, pady=5)

    # create the labels and add them to the frame
    dispenser_no_label = Label(pump_detail_frame, text="Dispenser No: {}".format(dispenser_No), bg="white", font=("Arial", 24))
    dispenser_no_label.pack(pady=4)

    nozzle_no_label = Label(pump_detail_frame, text="Nozzle No: {}".format(Nozil_No), bg="white", font=("Arial", 24))
    nozzle_no_label.pack(pady=4)

    price_label = Label(pump_detail_frame, text="Price: {}".format(price), bg="white", font=("Arial", 24))
    price_label.pack(pady=4)

    density_label = Label(pump_detail_frame, text="Density: {}".format(density), bg="white", font=("Arial", 24))
    density_label.pack(pady=4)

    fuel_type_label = Label(pump_detail_frame, text="Fuel Type: {}".format(Fuel), bg="white", font=("Arial", 24))
    fuel_type_label.pack(pady=4)

    pump_detail_frame.place(relx=0,rely=0.45)
    
    dashboard.mainloop()

# Start the application by showing the login window
login_window()
