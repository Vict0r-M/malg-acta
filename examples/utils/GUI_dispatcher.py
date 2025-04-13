#%%

# Import libraries:
import tkinter as tk
from tkinter import ttk
import re
import json
import threading
import os

#%%

# Define the main window:
def create_window():
    root = tk.Tk()
    root.title("Achiziție de date")
    root.attributes('-fullscreen', True) # Set window to fullscreen

    # Configure window as a multirow, multicolumn grid:
    for i in range(5):
        root.rowconfigure(i, weight=1)
    for i in range(2):
        root.columnconfigure(i, weight=1)

    return root

# Display window:
def run_window(root):
    if not isinstance(root, tk.Tk):
        raise TypeError("'root' must be a Tk instance when creating a window.")
    
    root.mainloop()

#%%

# Define date format validation:
def validate_date(date_entry, error_label):
    pattern = r'^\d{2}\.\d{2}\.\d{4}$'

    if not bool(re.match(pattern, date_entry.get())):
            error_label.config(text="Format de dată invalid. Folosește 'zz.ll.aaaa', e.g. '11.09.2001'.")
            date_entry.delete(0, tk.END) # Clear the entry field
            return False
    else:
        error_label.config(text='') # Clear the error message
        return True

# Define numerical validation:
def validate_numerical(numerical_entry, error_label):
    try: # Try to convert entry to an integer
        value = int(numerical_entry.get())
        if value < 0: # Value is an integer but negative
            raise ValueError("Numarul de teste trebuie sa fie un numar natural nenul.")
        
    except ValueError: # Entry is not an integer or negative
        error_label.config(text="Numarul de teste trebuie sa fie un numar natural nenul.")
        numerical_entry.delete(0, tk.END) # Clear entry field
        return False
    
    else: # Entry is a non-negative integer
        error_label.config(text='') # Clear error message
        return True

# Define empty dropdown validation:
def validate_dropdown(dropdown, error_label):
    if dropdown.get() == "":
        error_label.config(text="Acest câmp nu poate fi lăsat gol.")
        return False
    
    else:
        error_label.config(text="") # Clear error message
        return True

# Define data conversion to JSON:
def save_data(beneficiary_dropdown, cement_dropdown, date_entry, numerical_entry, internal_code_entry):
    data = {
        "probe_date": date_entry.get(),
        "beneficiar": beneficiary_dropdown.get(),
        "clasa_betonului": cement_dropdown.get(),
        "numar_teste": numerical_entry.get(),
        "internal_code": internal_code_entry.get()
    }

    # Path relative to this script file
    script_dir = os.path.dirname(__file__)  # Directory of the script file
    json_path = os.path.join(script_dir, '..', 'data', 'keyboard_inputs.json')

    # Append data to JSON:
    try:
        with open(json_path, 'r+') as file:
            try:
                file_data = json.load(file)
            except json.JSONDecodeError:
                # File is empty, start with an empty list
                file_data = []
            
            file_data.append(data)
            file.seek(0)
            file.truncate()  # Truncate the file to remove old data
            json.dump(file_data, file, indent=4)

    except FileNotFoundError:
        with open(json_path, 'w') as file:
            json.dump([data], file, indent=4)

# Define action of submitting information:
def submit_data(beneficiary_dropdown, cement_dropdown, date_entry, numerical_entry, internal_code_entry, error_label_beneficiary, 
                error_label_cement, error_label_date, error_label_numerical, error_label_internal_code, data_ready):
    # Call validation functions for each field:
    valid_date = validate_date(date_entry, error_label_date)
    valid_numerical = validate_numerical(numerical_entry, error_label_numerical)
    valid_beneficiary = validate_dropdown(beneficiary_dropdown, error_label_beneficiary)
    valid_cement = validate_dropdown(cement_dropdown, error_label_cement)
    valid_internal_code = validate_numerical(internal_code_entry, error_label_internal_code)

    if valid_date and valid_numerical and valid_beneficiary and valid_cement and valid_internal_code:    
        # If all validations pass, disable input fields:
        beneficiary_dropdown.config(state='disabled')
        cement_dropdown.config(state='disabled')
        date_entry.config(state='disabled')
        numerical_entry.config(state='disabled')
        internal_code_entry.config(state='disabled')

        # Save data to JSON:
        save_data(beneficiary_dropdown, cement_dropdown, date_entry, numerical_entry, internal_code_entry)

        # Set threading event:
        data_ready.set()

    else: pass # If any validation fails, do nothing (error messages are already set by validation functions)

#%%

# Define title component:
def create_title(root, title_text):
    # Parameter validation:
    if not isinstance(root, (tk.Tk, tk.Frame)):
        raise TypeError("'root' must be a Tk or Frame instance when creating a title.")
    
    if not isinstance(title_text, str):
        raise TypeError("The title text must be a string.")
    
    title_label = tk.Label(root, text=title_text, font=("Calibri", 30))
    title_label.grid(row=0, column=0, columnspan=2, sticky='EW') # No column splitting, default value 0

# Define a prompt + dropdown component:
def create_dropdown_entry(root, row_number, label_text, dropdown_width, dropdown_options):   
    # Parameter validation:
    if not isinstance(root, (tk.Tk, tk.Frame)):
        raise TypeError("'root' must be a Tk or Frame instance when creating a dropdown entry.")
    
    if not isinstance(row_number, int) or row_number < 0:
        raise ValueError("The row number of a dropdown entry must be a non-negative integer.")
    
    if not isinstance(label_text, str):
        raise TypeError("The label text of a dropdown entry must be a string.")
    
    if not isinstance(dropdown_width, int) or dropdown_width <= 0:
        raise ValueError("The width of a dropdown list must be a positive integer.")
    
    if not isinstance(dropdown_options, list) or not dropdown_options:
        raise ValueError("The options of a dropdown list must be a non-empty list.")

    # Create frame within the row:
    frame = tk.Frame(root)
    frame.grid(row=row_number, column=0, sticky="EW") # No column splitting, default value 0
    
    # Create a custom style for the Combobox with the desired font size:
    style = ttk.Style()
    style.configure("Custom.TCombobox", font=("Calibri", 15))

    # Auto weights for column label and dropdown:
    label = tk.Label(frame, text=label_text, font=("Calibri", 15))
    label.grid(row=0, column=0, sticky='W')

    dropdown = ttk.Combobox(frame, values=dropdown_options, width=dropdown_width, style="Custom.TCombobox")
    dropdown.grid(row=0, column=1, sticky='W')

    # Create error message label (initially empty):
    error_label = tk.Label(frame, text='', fg='red', font=("Calibri", 15))
    error_label.grid(row=1, column=0, columnspan=2, sticky='W')

    return dropdown, error_label

# Define prompt + keyboard input component:
def create_keyboard_entry(root, entry_type, row_number, column_number, label_text):
    # Parameter validation:
    if not isinstance(root, (tk.Tk, tk.Frame)):
        raise TypeError("'root' must be a Tk or Frame instance when creating a keyboard entry.")
    
    if not isinstance(row_number, int) or row_number < 0:
        raise ValueError("The row number of a keyboard entry must be a non-negative integer.")
    
    if not isinstance(label_text, str):
        raise TypeError("The text label of a keyboard entry must be a string.")
    
    if not isinstance(entry_type, str) or entry_type not in ("date", "numerical"):
        raise ValueError("The entry type must be either 'date' or 'numerical'.")
    
    # Create frame for the label and entry:
    frame = tk.Frame(root)
    frame.grid(row=row_number, column=column_number, sticky="EW") # No column splitting, default value 0

    # Create label:
    label = tk.Label(frame, text=label_text, font=("Calibri", 15))
    label.grid(row=0, column=0, sticky='W')

    # Create entry widget:
    keyboard_entry = tk.Entry(frame, font=("Calibri", 15))
    keyboard_entry.grid(row=0, column=1, sticky='W')

    # Create error message label (initially empty):
    error_label = tk.Label(frame, text='', fg='red', font=("Calibri", 15))
    error_label.grid(row=1, column=0, columnspan=3, sticky='W')

    return keyboard_entry, error_label

def create_button(root, row_number, button_text, beneficiary_dropdown, cement_dropdown, date_entry, numerical_entry, internal_code_entry, 
                  error_label_beneficiary, error_label_cement, error_label_date, error_label_numerical, error_label_internal_code, data_ready):
    # Create and split frame into columns:
    frame = tk.Frame(root)
    frame.grid(row=row_number, column=1, sticky="EW")

    # Configure frame as a multicolumn grid:
    for i in range(5):
        frame.columnconfigure(i, weight=1)
    
    # Create button widget in the middle column:
    button = tk.Button(frame, text=button_text, 
                       command=lambda: submit_data(beneficiary_dropdown, cement_dropdown, date_entry, numerical_entry, internal_code_entry,
                                                   error_label_beneficiary, error_label_cement, error_label_date, 
                                                   error_label_numerical, error_label_internal_code, data_ready), font=("Calibri", 20))
    button.grid(row=0, column=0, sticky="EW")

#%%
