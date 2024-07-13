import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkcalendar import Calendar
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta

def create_db_connection(host_name, user_name, user_password, db_name, port_number):
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            password=user_password,
            database=db_name,
            port=port_number
        )
        if connection.is_connected():
            print("MySQL Database connection successful")
            return connection
    except Error as e:
        print(f"Error: '{e}' occurred")
        messagebox.showerror("Database Connection Error", f"Error: '{e}' occurred")
    return None

def read_query(connection, query, params=None):
    cursor = connection.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
    except Error as e:
        print(f"Error: '{e}' occurred")
        messagebox.showerror("Query Error", f"Error: '{e}' occurred")
    return None

def execute_query(connection, query, params=None, show_error=True):
    cursor = connection.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"Error: '{e}' occurred")
        if show_error:
            messagebox.showerror("Query Error", f"Error: '{e}' occurred")

def login(user_type):
    global user_id
    email = user_email_entry.get() if user_type == "user" else admin_email_entry.get()
    password = user_password_entry.get() if user_type == "user" else admin_password_entry.get()
    
    if not email or not password:
        messagebox.showerror("Invalid Input", "Both fields are required.")
        return
    
    table = "ADMIN" if user_type == "admin" else "USER"
    query = f"SELECT * FROM {table} WHERE email = %s AND password = %s"
    params = (email, password)
    print(f"Executing query: {query} with params: {params}")
    result = read_query(connection, query, params)
    
    if result:
        user_id = result[0][0]
        messagebox.showinfo("Login Status", "Login successful")
        switch_frame(login_frame if user_type == "user" else admin_login_frame, admin_frame if user_type == "admin" else date_selection_frame)
    else:
        print(f"No user found with email: {email} and password: {password}")
        messagebox.showerror("Login Status", "Invalid email or password")

def register(user_type):
    name = name_entry.get()
    email = reg_email_entry.get()
    phone = phone_entry.get()
    password = reg_password_entry.get()
    dob = dob_entry.get()
    age = calculate_age(dob)

    if not name or not email or not phone or not password or not dob:
        messagebox.showerror("Invalid Input", "All fields are required.")
        return

    try:
        datetime.strptime(dob, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Invalid Input", "Date must be in YYYY-MM-DD format.")
        return

    table = "ADMIN" if user_type == "admin" else "USER"
    query = f"""
    INSERT INTO {table} (name, birthday, phone_Number, age, email, password)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    params = (name, dob, phone, age, email, password)
    print(f"Executing query: {query} with params: {params}")
    execute_query(connection, query, params)
    
    messagebox.showinfo("Registration Status", "Registration successful")
    switch_frame(register_frame, login_frame)

def calculate_age(birthday):
    birthdate = datetime.strptime(birthday, "%Y-%m-%d")
    today = datetime.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

def switch_frame(current_frame, next_frame):
    current_frame.pack_forget()
    next_frame.pack(pady=20)

def execute_custom_sql():
    sql_command = sql_command_entry.get("1.0", tk.END).strip()
    if not sql_command:
        messagebox.showerror("Invalid Input", "SQL command cannot be empty.")
        return

    try:
        cursor = connection.cursor()
        cursor.execute(sql_command)
        if cursor.with_rows:
            result = cursor.fetchall()
            output = "\n".join([str(row) for row in result])
        else:
            connection.commit()
            output = "Query executed successfully."
        sql_result_entry.config(state=tk.NORMAL)
        sql_result_entry.delete("1.0", tk.END)
        sql_result_entry.insert(tk.END, output)
        sql_result_entry.config(state=tk.DISABLED)
    except Error as e:
        messagebox.showerror("Query Error", f"Error: '{e}' occurred")

def run_sql_commands():
    switch_frame(admin_frame, sql_commands_frame)

def manage_users():
    switch_frame(admin_frame, manage_users_frame)

def manage_plays():
    switch_frame(admin_frame, manage_plays_frame)

def manage_preset_queries():
    switch_frame(admin_frame, preset_queries_frame)

def view_preset_queries():
    preset_queries_listbox.delete(0, tk.END)
    query = "SELECT * FROM PRESET_QUERIES"
    preset_queries = read_query(connection, query)
    if preset_queries:
        for preset_query in preset_queries:
            preset_queries_listbox.insert(tk.END, f"ID: {preset_query[0]}, Query: {preset_query[1]}")
    else:
        messagebox.showinfo("View Preset Queries", "No preset queries found.")
    switch_frame(preset_queries_frame, view_preset_queries_frame)

def add_preset_query():
    switch_frame(preset_queries_frame, add_preset_query_frame)

def submit_add_preset_query():
    preset_query = add_preset_query_entry.get("1.0", tk.END).strip()

    if not preset_query:
        messagebox.showerror("Invalid Input", "Preset query cannot be empty.")
        return

    # Insert the new preset query into the database
    insert_query = "INSERT INTO PRESET_QUERIES (query) VALUES (%s)"
    params = (preset_query,)
    execute_query(connection, insert_query, params)

    # Execute the newly added preset query
    try:
        cursor = connection.cursor()
        cursor.execute(preset_query)
        if cursor.with_rows:
            result = cursor.fetchall()
            output = "\n".join([str(row) for row in result])
        else:
            connection.commit()
            output = "Preset query executed successfully."
        
        sql_result_entry.config(state=tk.NORMAL)
        sql_result_entry.delete("1.0", tk.END)
        sql_result_entry.insert(tk.END, output)
        sql_result_entry.config(state=tk.DISABLED)
        
        messagebox.showinfo("Add Preset Query", "Preset query added and executed successfully")
    except Error as e:
        messagebox.showerror("Query Error", f"Error: '{e}' occurred while executing the preset query")
    
    add_preset_query_entry.delete("1.0", tk.END)
    switch_frame(add_preset_query_frame, preset_queries_frame)

def remove_preset_query():
    switch_frame(preset_queries_frame, remove_preset_query_frame)

def submit_remove_preset_query():
    preset_query_id = remove_preset_query_id_entry.get()

    if not preset_query_id:
        messagebox.showerror("Invalid Input", "Preset query ID is required.")
        return

    query = "DELETE FROM PRESET_QUERIES WHERE query_ID = %s"
    params = (preset_query_id,)
    execute_query(connection, query, params)
    messagebox.showinfo("Remove Preset Query", "Preset query removed successfully")
    remove_preset_query_id_entry.delete(0, tk.END)
    switch_frame(remove_preset_query_frame, preset_queries_frame)

def view_plays():
    plays_listbox.delete(0, tk.END)
    query = "SELECT STAGE.name, PLAY.play_Name, PLAY.director FROM STAGE JOIN PLAY ON STAGE.stage_PhoneNumber = PLAY.stage_PhoneNumber"
    plays = read_query(connection, query)
    if plays:
        for play in plays:
            plays_listbox.insert(tk.END, f"Theater: {play[0]}, Play: {play[1]}, Director: {play[2]}")
    else:
        messagebox.showinfo("View Plays", "No plays found.")
    switch_frame(admin_frame, view_plays_frame)

def add_play():
    switch_frame(manage_plays_frame, add_play_frame)

def submit_play():
    play_name = play_name_entry.get()
    director = director_entry.get()
    stage_phone = stage_phone_entry.get()

    if not play_name or not director or not stage_phone:
        messagebox.showerror("Invalid Input", "All fields are required.")
        return

    query = "INSERT INTO PLAY (play_Name, director, stage_PhoneNumber) VALUES (%s, %s, %s)"
    params = (play_name, director, stage_phone)
    execute_query(connection, query, params)
    messagebox.showinfo("Add Play", "Play added successfully")
    play_name_entry.delete(0, tk.END)
    director_entry.delete(0, tk.END)
    stage_phone_entry.delete(0, tk.END)
    switch_frame(add_play_frame, manage_plays_frame)

def remove_play():
    switch_frame(manage_plays_frame, remove_play_frame)

def submit_remove_play():
    play_id = remove_play_id_entry.get()

    if not play_id:
        messagebox.showerror("Invalid Input", "Play ID is required.")
        return

    query = "DELETE FROM PLAY WHERE play_ID = %s"
    params = (play_id,)
    execute_query(connection, query, params)
    messagebox.showinfo("Remove Play", "Play removed successfully")
    remove_play_id_entry.delete(0, tk.END)
    switch_frame(remove_play_frame, manage_plays_frame)

def logout():
    switch_frame(admin_frame, main_selection_frame)

def back_to_admin_page():
    current_frames = [view_preset_queries_frame, add_preset_query_frame, remove_preset_query_frame, view_plays_frame, add_play_frame, remove_play_frame, sql_commands_frame, manage_users_frame]
    for frame in current_frames:
        frame.pack_forget()
    admin_frame.pack(pady=20)

def show_plays():
    selected_theater_index = theaters_listbox.curselection()
    if not selected_theater_index:
        messagebox.showerror("Selection Error", "Please select a theater.")
        return

    selected_theater = theaters_listbox.get(selected_theater_index)
    query = """
    SELECT PLAY.play_Name, PLAY.director, PLAY.play_ID
    FROM PLAY
    JOIN STAGE ON PLAY.stage_PhoneNumber = STAGE.stage_PhoneNumber
    WHERE STAGE.name = %s
    """
    params = (selected_theater,)
    plays = read_query(connection, query, params)

    if not plays:
        messagebox.showinfo("Plays Info", "No plays available for the selected theater.")
    else:
        plays_listbox.delete(0, tk.END)
        for play in plays:
            play_info = f"{play[0]} directed by {play[1]}"
            plays_listbox.insert(tk.END, (play_info, play[2]))
        switch_frame(homepage_frame, plays_frame)

def select_play():
    selected_play_index = plays_listbox.curselection()
    if not selected_play_index:
        messagebox.showerror("Selection Error", "Please select a play.")
        return

    selected_play = plays_listbox.get(selected_play_index)
    play_id = selected_play[1]
    show_seat_selection(play_id)

def show_seat_selection(play_id):
    plays_frame.pack_forget()
    seat_selection_frame.pack(pady=20)

    seats_listbox.delete(0, tk.END)
    query = """
    SELECT seat_No, rrow_Number, column_Number
    FROM SEAT
    WHERE status = 'Available'
    """
    seats = read_query(connection, query)
    for seat in seats:
        seat_info = f"Row {seat[1]}, Column {seat[2]}"
        seats_listbox.insert(tk.END, (seat_info, seat[0]))

def select_seat():
    global selected_seat_id
    selected_seat_index = seats_listbox.curselection()
    if not selected_seat_index:
        messagebox.showerror("Selection Error", "Please select a seat.")
        return

    selected_seat = seats_listbox.get(selected_seat_index)
    selected_seat_id = selected_seat[1]
    messagebox.showinfo("Seat Selection", f"You have selected seat {selected_seat[0]}")
    seat_selection_frame.pack_forget()
    show_payment_screen()

def show_payment_screen():
    payment_frame.pack(pady=20)

def return_to_date_selection():
    payment_frame.pack_forget()
    show_date_selection()

def process_payment():
    card_number = card_number_entry.get()
    expiry_date = expiry_date_entry.get()
    cvc = cvc_entry.get()
    
    if not card_number or not expiry_date or not cvc:
        messagebox.showerror("Invalid Input", "All fields are required.")
        return
    
    if len(card_number) != 16 or not card_number.isdigit():
        messagebox.showerror("Invalid Input", "Credit card number must be 16 digits.")
        return
    
    if len(cvc) != 3 or not cvc.isdigit():
        messagebox.showerror("Invalid Input", "CVC must be 3 digits.")
        return

    try:
        expiry_year, expiry_month = map(int, expiry_date.split('-'))
        if expiry_month < 1 or expiry_month > 12:
            raise ValueError
        if expiry_year < 2024 or expiry_year > 2032:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Input", "Expiry date is invalid.")
        return

    amount = 50.00
    discount = 0.0
    query = "SELECT status FROM STUDENT_VERIFICATION WHERE user_ID = %s"
    params = (user_id,)
    status = read_query(connection, query, params)
    
    if status and status[0][0] == 'Verified':
        discount = amount * 0.15
        discount_label.config(text=f"Student Discount Applied: 15%\nOriginal Amount: ${amount}\nDiscounted Amount: ${amount - discount}")
    
    final_amount = amount - discount

    query = "INSERT INTO PAYMENT (booking_ID, amount, credit_card_no, credit_card_last_date, cvc) VALUES (%s, %s, %s, %s, %s)"
    params = (None, final_amount, card_number, expiry_date, cvc)
    execute_query(connection, query, params, show_error=False)
    
    messagebox.showinfo("Payment Status", f"Payment successful! Amount: ${final_amount:.2f}")

    payment_frame.pack_forget()
    return_to_date_selection()

def show_date_selection():
    date_selection_frame.pack(pady=20)

def select_date():
    global selected_date
    selected_date = cal.get_date()
    date_selection_frame.pack_forget()
    show_time_selection()

def show_time_selection():
    time_selection_frame.pack(pady=20)

def select_time():
    global selected_time
    selected_time = time_combobox.get()
    time_selection_frame.pack_forget()
    show_homepage()

def show_homepage():
    homepage_frame.pack(pady=20)
    theaters = get_theaters()
    for theater in theaters:
        theaters_listbox.insert(tk.END, theater[0])

def get_theaters():
    query = "SELECT name FROM STAGE"
    result = read_query(connection, query)
    return result

# Additional functions for managing users

def view_users():
    users_listbox.delete(0, tk.END)
    query = "SELECT * FROM USER"
    users = read_query(connection, query)
    if users:
        for user in users:
            user_info = f"ID: {user[0]}, Name: {user[1]}, Email: {user[4]}"
            users_listbox.insert(tk.END, user_info)
    else:
        messagebox.showinfo("View Users", "No users found.")
    switch_frame(manage_users_frame, view_users_frame)

def remove_user():
    switch_frame(manage_users_frame, remove_user_frame)

def submit_remove_user():
    user_id = remove_user_id_entry.get()

    if not user_id:
        messagebox.showerror("Invalid Input", "User ID is required.")
        return

    query = "DELETE FROM USER WHERE user_ID = %s"
    params = (user_id,)
    execute_query(connection, query, params)
    messagebox.showinfo("Remove User", "User removed successfully")
    remove_user_id_entry.delete(0, tk.END)
    switch_frame(remove_user_frame, manage_users_frame)

def show_manage_account():
    global manage_account_window
    manage_account_window = tk.Toplevel(app)
    manage_account_window.title("Manage Account")

    # Fetch current user info
    query = "SELECT name, email, password, birthday, phone_Number FROM USER WHERE user_ID = %s"
    params = (user_id,)
    user_info = read_query(connection, query, params)
    
    if user_info:
        name_entry_manage = ttk.Entry(manage_account_window)
        name_entry_manage.insert(0, user_info[0][0])
        email_entry_manage = ttk.Entry(manage_account_window)
        email_entry_manage.insert(0, user_info[0][1])
        password_entry_manage = ttk.Entry(manage_account_window, show='*')
        password_entry_manage.insert(0, user_info[0][2])
        dob_entry_manage = ttk.Entry(manage_account_window)
        dob_entry_manage.insert(0, user_info[0][3])
        phone_entry_manage = ttk.Entry(manage_account_window)
        phone_entry_manage.insert(0, user_info[0][4])
        
        name_label_manage = ttk.Label(manage_account_window, text="Full Name:")
        email_label_manage = ttk.Label(manage_account_window, text="Email:")
        password_label_manage = ttk.Label(manage_account_window, text="New Password:")
        dob_label_manage = ttk.Label(manage_account_window, text="Birth Date (YYYY-MM-DD):")
        phone_label_manage = ttk.Label(manage_account_window, text="Phone Number:")
        
        update_account_button = ttk.Button(manage_account_window, text="Update Account", command=lambda: update_account(name_entry_manage, email_entry_manage, password_entry_manage, dob_entry_manage, phone_entry_manage))
        back_button = ttk.Button(manage_account_window, text="Back", command=manage_account_window.destroy)
        
        name_label_manage.grid(row=0, column=0, padx=5, pady=5)
        name_entry_manage.grid(row=0, column=1, padx=5, pady=5)
        email_label_manage.grid(row=1, column=0, padx=5, pady=5)
        email_entry_manage.grid(row=1, column=1, padx=5, pady=5)
        password_label_manage.grid(row=2, column=0, padx=5, pady=5)
        password_entry_manage.grid(row=2, column=1, padx=5, pady=5)
        dob_label_manage.grid(row=3, column=0, padx=5, pady=5)
        dob_entry_manage.grid(row=3, column=1, padx=5, pady=5)
        phone_label_manage.grid(row=4, column=0, padx=5, pady=5)
        phone_entry_manage.grid(row=4, column=1, padx=5, pady=5)
        update_account_button.grid(row=5, column=0, columnspan=2, pady=10)
        back_button.grid(row=6, column=0, columnspan=2, pady=10)

def update_account(name_entry_manage, email_entry_manage, password_entry_manage, dob_entry_manage, phone_entry_manage):
    name = name_entry_manage.get()
    email = email_entry_manage.get()
    password = password_entry_manage.get()
    dob = dob_entry_manage.get()
    phone = phone_entry_manage.get()
    
    if not name or not email or not dob or not phone:
        messagebox.showerror("Invalid Input", "Name, email, birth date, and phone number are required.")
        return
    
    query = "UPDATE USER SET name = %s, email = %s, password = %s, birthday = %s, phone_Number = %s WHERE user_ID = %s"
    params = (name, email, password, dob, phone, user_id)
    execute_query(connection, query, params)
    messagebox.showinfo("Update Account", "Account updated successfully")
    manage_account_window.destroy()

# User logout function
def user_logout():
    switch_frame(homepage_frame, main_selection_frame)

# Veritabanı bağlantısı
connection = create_db_connection("localhost", "root", "1234", "theaterapp", 3306)

if connection:
    app = tk.Tk()
    app.title('Theater Booking System')

    main_selection_frame = ttk.Frame(app)
    main_selection_frame.pack(pady=20)

    user_button = ttk.Button(main_selection_frame, text="User Login", command=lambda: switch_frame(main_selection_frame, login_frame))
    user_button.pack(pady=10)

    admin_button = ttk.Button(main_selection_frame, text="Admin Login", command=lambda: switch_frame(main_selection_frame, admin_login_frame))
    admin_button.pack(pady=10)

    login_frame = ttk.Frame(app)

    login_label = ttk.Label(login_frame, text="User Login")
    login_label.grid(row=0, column=0, columnspan=2, pady=10)

    user_email_label = ttk.Label(login_frame, text="Email:")
    user_email_label.grid(row=1, column=0, padx=5, pady=5)
    user_email_entry = ttk.Entry(login_frame)
    user_email_entry.grid(row=1, column=1, padx=5, pady=5)

    user_password_label = ttk.Label(login_frame, text="Password:")
    user_password_label.grid(row=2, column=0, padx=5, pady=5)
    user_password_entry = ttk.Entry(login_frame, show='*')
    user_password_entry.grid(row=2, column=1, padx=5, pady=5)

    login_button = ttk.Button(login_frame, text="Login", command=lambda: login("user"))
    login_button.grid(row=3, column=0, columnspan=2, pady=10)

    register_button = ttk.Button(login_frame, text="Register", command=lambda: switch_frame(login_frame, register_frame))
    register_button.grid(row=4, column=0, columnspan=2, pady=10)

    register_frame = ttk.Frame(app)

    register_label = ttk.Label(register_frame, text="Register")
    register_label.grid(row=0, column=0, columnspan=2, pady=10)

    name_label = ttk.Label(register_frame, text="Full Name:")
    name_label.grid(row=1, column=0, padx=5, pady=5)
    name_entry = ttk.Entry(register_frame)
    name_entry.grid(row=1, column=1, padx=5, pady=5)

    reg_email_label = ttk.Label(register_frame, text="Email:")
    reg_email_label.grid(row=2, column=0, padx=5, pady=5)
    reg_email_entry = ttk.Entry(register_frame)
    reg_email_entry.grid(row=2, column=1, padx=5, pady=5)

    phone_label = ttk.Label(register_frame, text="Phone Number:")
    phone_label.grid(row=3, column=0, padx=5, pady=5)
    phone_entry = ttk.Entry(register_frame)
    phone_entry.grid(row=3, column=1, padx=5, pady=5)

    reg_password_label = ttk.Label(register_frame, text="Password:")
    reg_password_label.grid(row=4, column=0, padx=5, pady=5)
    reg_password_entry = ttk.Entry(register_frame, show='*')
    reg_password_entry.grid(row=4, column=1, padx=5, pady=5)

    dob_label = ttk.Label(register_frame, text="Date of Birth (YYYY-MM-DD):")
    dob_label.grid(row=5, column=0, padx=5, pady=5)
    dob_entry = ttk.Entry(register_frame)
    dob_entry.grid(row=5, column=1, padx=5, pady=5)

    register_submit_button = ttk.Button(register_frame, text="Submit", command=lambda: register("user"))
    register_submit_button.grid(row=6, column=0, columnspan=2, pady=10)

    back_to_login_button = ttk.Button(register_frame, text="Back to Login", command=lambda: switch_frame(register_frame, login_frame))
    back_to_login_button.grid(row=7, column=0, columnspan=2, pady=10)

    admin_login_frame = ttk.Frame(app)

    admin_login_label = ttk.Label(admin_login_frame, text="Admin Login")
    admin_login_label.grid(row=0, column=0, columnspan=2, pady=10)

    admin_email_label = ttk.Label(admin_login_frame, text="Email:")
    admin_email_label.grid(row=1, column=0, padx=5, pady=5)
    admin_email_entry = ttk.Entry(admin_login_frame)
    admin_email_entry.grid(row=1, column=1, padx=5, pady=5)

    admin_password_label = ttk.Label(admin_login_frame, text="Password:")
    admin_password_label.grid(row=2, column=0, padx=5, pady=5)
    admin_password_entry = ttk.Entry(admin_login_frame, show='*')
    admin_password_entry.grid(row=2, column=1, padx=5, pady=5)

    admin_login_button = ttk.Button(admin_login_frame, text="Login", command=lambda: login("admin"))
    admin_login_button.grid(row=3, column=0, columnspan=2, pady=10)

    admin_register_button = ttk.Button(admin_login_frame, text="Register", command=lambda: switch_frame(admin_login_frame, admin_register_frame))
    admin_register_button.grid(row=4, column=0, columnspan=2, pady=10)

    admin_register_frame = ttk.Frame(app)

    admin_register_label = ttk.Label(admin_register_frame, text="Admin Register")
    admin_register_label.grid(row=0, column=0, columnspan=2, pady=10)

    name_label = ttk.Label(admin_register_frame, text="Full Name:")
    name_label.grid(row=1, column=0, padx=5, pady=5)
    name_entry = ttk.Entry(admin_register_frame)
    name_entry.grid(row=1, column=1, padx=5, pady=5)

    reg_email_label = ttk.Label(admin_register_frame, text="Email:")
    reg_email_label.grid(row=2, column=0, padx=5, pady=5)
    reg_email_entry = ttk.Entry(admin_register_frame)
    reg_email_entry.grid(row=2, column=1, padx=5, pady=5)

    phone_label = ttk.Label(admin_register_frame, text="Phone Number:")
    phone_label.grid(row=3, column=0, padx=5, pady=5)
    phone_entry = ttk.Entry(admin_register_frame)
    phone_entry.grid(row=3, column=1, padx=5, pady=5)

    reg_password_label = ttk.Label(admin_register_frame, text="Password:")
    reg_password_label.grid(row=4, column=0, padx=5, pady=5)
    reg_password_entry = ttk.Entry(admin_register_frame, show='*')
    reg_password_entry.grid(row=4, column=1, padx=5, pady=5)

    dob_label = ttk.Label(admin_register_frame, text="Date of Birth (YYYY-MM-DD):")
    dob_label.grid(row=5, column=0, padx=5, pady=5)
    dob_entry = ttk.Entry(admin_register_frame)
    dob_entry.grid(row=5, column=1, padx=5, pady=5)

    register_submit_button = ttk.Button(admin_register_frame, text="Submit", command=lambda: register("admin"))
    register_submit_button.grid(row=6, column=0, columnspan=2, pady=10)

    back_to_login_button = ttk.Button(admin_register_frame, text="Back to Login", command=lambda: switch_frame(admin_register_frame, admin_login_frame))
    back_to_login_button.grid(row=7, column=0, columnspan=2, pady=10)

    admin_frame = ttk.Frame(app)

    admin_label = ttk.Label(admin_frame, text="Admin Page")
    admin_label.pack(pady=10)

    run_sql_button = ttk.Button(admin_frame, text="Run SQL Commands", command=run_sql_commands)
    run_sql_button.pack(pady=10)

    manage_users_button = ttk.Button(admin_frame, text="Manage Users", command=manage_users)
    manage_users_button.pack(pady=10)

    manage_plays_button = ttk.Button(admin_frame, text="Manage Plays", command=manage_plays)
    manage_plays_button.pack(pady=10)

    manage_preset_queries_button = ttk.Button(admin_frame, text="Manage Preset Queries", command=manage_preset_queries)
    manage_preset_queries_button.pack(pady=10)

    logout_button = ttk.Button(admin_frame, text="Logout", command=logout)
    logout_button.pack(pady=10)

    sql_commands_frame = ttk.Frame(app)
    sql_commands_label = ttk.Label(sql_commands_frame, text="SQL Commands")
    sql_commands_label.pack(pady=10)

    sql_command_entry = scrolledtext.ScrolledText(sql_commands_frame, width=80, height=10)
    sql_command_entry.pack(pady=10)

    execute_sql_button = ttk.Button(sql_commands_frame, text="Execute SQL", command=execute_custom_sql)
    execute_sql_button.pack(pady=10)

    sql_result_entry = scrolledtext.ScrolledText(sql_commands_frame, width=80, height=10, state=tk.DISABLED)
    sql_result_entry.pack(pady=10)

    back_to_admin_button = ttk.Button(sql_commands_frame, text="Back to Admin Page", command=back_to_admin_page)
    back_to_admin_button.pack(pady=10)

    manage_users_frame = ttk.Frame(app)
    manage_users_label = ttk.Label(manage_users_frame, text="Manage Users")
    manage_users_label.pack(pady=10)

    view_users_button = ttk.Button(manage_users_frame, text="View Users", command=view_users)
    view_users_button.pack(pady=10)

    remove_users_button = ttk.Button(manage_users_frame, text="Remove User", command=remove_user)
    remove_users_button.pack(pady=10)

    back_to_admin_button = ttk.Button(manage_users_frame, text="Back to Admin Page", command=back_to_admin_page)
    back_to_admin_button.pack(pady=10)

    view_users_frame = ttk.Frame(app)
    users_listbox = tk.Listbox(view_users_frame, width=50, height=10)
    users_listbox.pack(pady=10)
    back_to_manage_users_button = ttk.Button(view_users_frame, text="Back to Manage Users", command=lambda: switch_frame(view_users_frame, manage_users_frame))
    back_to_manage_users_button.pack(pady=10)

    remove_user_frame = ttk.Frame(app)
    remove_user_label = ttk.Label(remove_user_frame, text="Remove User")
    remove_user_label.pack(pady=10)
    remove_user_id_label = ttk.Label(remove_user_frame, text="User ID:")
    remove_user_id_label.pack(pady=5)
    remove_user_id_entry = ttk.Entry(remove_user_frame)
    remove_user_id_entry.pack(pady=5)
    submit_remove_user_button = ttk.Button(remove_user_frame, text="Submit", command=submit_remove_user)
    submit_remove_user_button.pack(pady=10)
    back_to_manage_users_button = ttk.Button(remove_user_frame, text="Back to Manage Users", command=lambda: switch_frame(remove_user_frame, manage_users_frame))
    back_to_manage_users_button.pack(pady=10)

    manage_plays_frame = ttk.Frame(app)

    view_plays_button = ttk.Button(manage_plays_frame, text="View Plays", command=view_plays)
    view_plays_button.pack(pady=10)

    add_play_button = ttk.Button(manage_plays_frame, text="Add Play", command=add_play)
    add_play_button.pack(pady=10)

    remove_play_button = ttk.Button(manage_plays_frame, text="Remove Play", command=remove_play)
    remove_play_button.pack(pady=10)

    back_to_admin_button = ttk.Button(manage_plays_frame, text="Back to Admin Page", command=back_to_admin_page)
    back_to_admin_button.pack(pady=10)

    view_plays_frame = ttk.Frame(app)
    plays_listbox = tk.Listbox(view_plays_frame, width=50, height=10)
    plays_listbox.pack(pady=10)
    back_to_manage_plays_button = ttk.Button(view_plays_frame, text="Back to Manage Plays", command=lambda: switch_frame(view_plays_frame, manage_plays_frame))
    back_to_manage_plays_button.pack(pady=10)

    add_play_frame = ttk.Frame(app)
    add_play_label = ttk.Label(add_play_frame, text="Add Play")
    add_play_label.pack(pady=10)
    play_name_label = ttk.Label(add_play_frame, text="Play Name:")
    play_name_label.pack(pady=5)
    play_name_entry = ttk.Entry(add_play_frame)
    play_name_entry.pack(pady=5)
    director_label = ttk.Label(add_play_frame, text="Director:")
    director_label.pack(pady=5)
    director_entry = ttk.Entry(add_play_frame)
    director_entry.pack(pady=5)
    stage_phone_label = ttk.Label(add_play_frame, text="Stage Phone Number:")
    stage_phone_label.pack(pady=5)
    stage_phone_entry = ttk.Entry(add_play_frame)
    stage_phone_entry.pack(pady=5)
    submit_play_button = ttk.Button(add_play_frame, text="Submit", command=submit_play)
    submit_play_button.pack(pady=10)
    back_to_manage_plays_button = ttk.Button(add_play_frame, text="Back to Manage Plays", command=lambda: switch_frame(add_play_frame, manage_plays_frame))
    back_to_manage_plays_button.pack(pady=10)

    remove_play_frame = ttk.Frame(app)
    remove_play_label = ttk.Label(remove_play_frame, text="Remove Play")
    remove_play_label.pack(pady=10)
    remove_play_id_label = ttk.Label(remove_play_frame, text="Play ID:")
    remove_play_id_label.pack(pady=5)
    remove_play_id_entry = ttk.Entry(remove_play_frame)
    remove_play_id_entry.pack(pady=5)
    submit_remove_play_button = ttk.Button(remove_play_frame, text="Submit", command=submit_remove_play)
    submit_remove_play_button.pack(pady=10)
    back_to_manage_plays_button = ttk.Button(remove_play_frame, text="Back to Manage Plays", command=lambda: switch_frame(remove_play_frame, manage_plays_frame))
    back_to_manage_plays_button.pack(pady=10)

    preset_queries_frame = ttk.Frame(app)

    view_preset_queries_button = ttk.Button(preset_queries_frame, text="View Preset Queries", command=view_preset_queries)
    view_preset_queries_button.pack(pady=10)

    add_preset_query_button = ttk.Button(preset_queries_frame, text="Add Preset Query", command=add_preset_query)
    add_preset_query_button.pack(pady=10)

    remove_preset_query_button = ttk.Button(preset_queries_frame, text="Remove Preset Query", command=remove_preset_query)
    remove_preset_query_button.pack(pady=10)

    back_to_admin_button = ttk.Button(preset_queries_frame, text="Back to Admin Page", command=back_to_admin_page)
    back_to_admin_button.pack(pady=10)

    view_preset_queries_frame = ttk.Frame(app)
    preset_queries_listbox = tk.Listbox(view_preset_queries_frame, width=50, height=10)
    preset_queries_listbox.pack(pady=10)
    back_to_preset_queries_button = ttk.Button(view_preset_queries_frame, text="Back to Manage Preset Queries", command=lambda: switch_frame(view_preset_queries_frame, preset_queries_frame))
    back_to_preset_queries_button.pack(pady=10)

    add_preset_query_frame = ttk.Frame(app)
    add_preset_query_label = ttk.Label(add_preset_query_frame, text="Add Preset Query")
    add_preset_query_label.pack(pady=10)
    add_preset_query_entry = scrolledtext.ScrolledText(add_preset_query_frame, width=80, height=10)
    add_preset_query_entry.pack(pady=10)
    submit_add_preset_query_button = ttk.Button(add_preset_query_frame, text="Submit", command=submit_add_preset_query)
    submit_add_preset_query_button.pack(pady=10)
    back_to_preset_queries_button = ttk.Button(add_preset_query_frame, text="Back to Manage Preset Queries", command=lambda: switch_frame(add_preset_query_frame, preset_queries_frame))
    back_to_preset_queries_button.pack(pady=10)

    remove_preset_query_frame = ttk.Frame(app)
    remove_preset_query_label = ttk.Label(remove_preset_query_frame, text="Remove Preset Query")
    remove_preset_query_label.pack(pady=10)
    remove_preset_query_id_label = ttk.Label(remove_preset_query_frame, text="Preset Query ID:")
    remove_preset_query_id_label.pack(pady=5)
    remove_preset_query_id_entry = ttk.Entry(remove_preset_query_frame)
    remove_preset_query_id_entry.pack(pady=5)
    submit_remove_preset_query_button = ttk.Button(remove_preset_query_frame, text="Submit", command=submit_remove_preset_query)
    submit_remove_preset_query_button.pack(pady=10)
    back_to_preset_queries_button = ttk.Button(remove_preset_query_frame, text="Back to Manage Preset Queries", command=lambda: switch_frame(remove_preset_query_frame, preset_queries_frame))
    back_to_preset_queries_button.pack(pady=10)

    date_selection_frame = ttk.Frame(app)

    cal_label = ttk.Label(date_selection_frame, text="Select a Date:")
    cal_label.pack(pady=10)

    today = datetime.today()
    week_later = today + timedelta(days=7)

    cal = Calendar(date_selection_frame, selectmode='day', mindate=today, maxdate=week_later)
    cal.pack(pady=10)

    select_date_button = ttk.Button(date_selection_frame, text="Select Date", command=select_date)
    select_date_button.pack(pady=10)

    manage_account_button = ttk.Button(date_selection_frame, text="Manage Account", command=show_manage_account)
    manage_account_button.pack(pady=10)

    logout_button_user = ttk.Button(date_selection_frame, text="Logout", command=user_logout)
    logout_button_user.pack(pady=10)

    time_selection_frame = ttk.Frame(app)

    time_label = ttk.Label(time_selection_frame, text="Select a Time:")
    time_label.pack(pady=10)

    times = [f"{hour}:00" for hour in range(12, 16)]
    time_combobox = ttk.Combobox(time_selection_frame, values=times)
    time_combobox.pack(pady=10)

    select_time_button = ttk.Button(time_selection_frame, text="Select Time", command=select_time)
    select_time_button.pack(pady=10)

    back_to_date_selection_button = ttk.Button(time_selection_frame, text="Back", command=lambda: switch_frame(time_selection_frame, date_selection_frame))
    back_to_date_selection_button.pack(pady=10)

    homepage_frame = ttk.Frame(app)
    
    theaters_label = ttk.Label(homepage_frame, text="Available Theaters:")
    theaters_label.pack(pady=5)
    
    theaters_listbox = tk.Listbox(homepage_frame, width=50, height=10)
    theaters_listbox.pack(pady=5)

    select_theater_button = ttk.Button(homepage_frame, text="Select Theater", command=show_plays)
    select_theater_button.pack(pady=5)

    manage_account_button_homepage = ttk.Button(homepage_frame, text="Manage Account", command=show_manage_account)
    manage_account_button_homepage.pack(pady=10)

    logout_button_homepage = ttk.Button(homepage_frame, text="Logout", command=user_logout)
    logout_button_homepage.pack(pady=10)

    back_to_time_selection_button = ttk.Button(homepage_frame, text="Back", command=lambda: switch_frame(homepage_frame, time_selection_frame))
    back_to_time_selection_button.pack(pady=10)

    plays_frame = ttk.Frame(app)
    
    plays_label = ttk.Label(plays_frame, text="Plays Available:")
    plays_label.pack(pady=5)
    
    plays_listbox = tk.Listbox(plays_frame, width=50, height=10)
    plays_listbox.pack(pady=5)

    select_play_button = ttk.Button(plays_frame, text="Select Play", command=select_play)
    select_play_button.pack(pady=5)

    manage_account_button_plays = ttk.Button(plays_frame, text="Manage Account", command=show_manage_account)
    manage_account_button_plays.pack(pady=10)

    logout_button_plays = ttk.Button(plays_frame, text="Logout", command=user_logout)
    logout_button_plays.pack(pady=10)

    back_to_homepage_button = ttk.Button(plays_frame, text="Back", command=lambda: switch_frame(plays_frame, homepage_frame))
    back_to_homepage_button.pack(pady=10)

    seat_selection_frame = ttk.Frame(app)
    
    seat_selection_label = ttk.Label(seat_selection_frame, text="Select Your Seat:")
    seat_selection_label.pack(pady=5)

    seats_listbox = tk.Listbox(seat_selection_frame, width=50, height=10)
    seats_listbox.pack(pady=5)

    select_seat_button = ttk.Button(seat_selection_frame, text="Select Seat", command=select_seat)
    select_seat_button.pack(pady=5)

    manage_account_button_seat_selection = ttk.Button(seat_selection_frame, text="Manage Account", command=show_manage_account)
    manage_account_button_seat_selection.pack(pady=10)

    logout_button_seat_selection = ttk.Button(seat_selection_frame, text="Logout", command=user_logout)
    logout_button_seat_selection.pack(pady=10)

    back_to_plays_button = ttk.Button(seat_selection_frame, text="Back", command=lambda: switch_frame(seat_selection_frame, plays_frame))
    back_to_plays_button.pack(pady=10)

    payment_frame = ttk.Frame(app)
    
    discount_label = ttk.Label(payment_frame, text="")
    discount_label.pack(pady=5)

    card_number_label = ttk.Label(payment_frame, text="Card Number:")
    card_number_label.pack(pady=5)
    card_number_entry = ttk.Entry(payment_frame)
    card_number_entry.pack(pady=5)

    expiry_date_label = ttk.Label(payment_frame, text="Expiry Date (YYYY-MM):")
    expiry_date_label.pack(pady=5)
    expiry_date_entry = ttk.Entry(payment_frame)
    expiry_date_entry.pack(pady=5)

    cvc_label = ttk.Label(payment_frame, text="CVC:")
    cvc_label.pack(pady=5)
    cvc_entry = ttk.Entry(payment_frame)
    cvc_entry.pack(pady=5)

    process_payment_button = ttk.Button(payment_frame, text="Process Payment", command=process_payment)
    process_payment_button.pack(pady=10)

    return_to_date_selection_button = ttk.Button(payment_frame, text="Return to Date Selection", command=return_to_date_selection)
    return_to_date_selection_button.pack(pady=10)

    manage_account_button_payment = ttk.Button(payment_frame, text="Manage Account", command=show_manage_account)
    manage_account_button_payment.pack(pady=10)

    logout_button_payment = ttk.Button(payment_frame, text="Logout", command=user_logout)
    logout_button_payment.pack(pady=10)

    back_to_seat_selection_button = ttk.Button(payment_frame, text="Back", command=lambda: switch_frame(payment_frame, seat_selection_frame))
    back_to_seat_selection_button.pack(pady=10)

    app.mainloop()