#%%

# Import libraries:
import threading
import tkinter as tk
from tkinter import ttk

from ..utils.GUI_dispatcher import create_window, run_window, create_title, create_dropdown_entry, create_keyboard_entry, create_button

#%%

# Define the main function:
def run_GUI(data_ready, gui_unlock):

    # Define constants:
    beneficiaries = ["HIDROTERRA SA", "CHEZA SRL", "ROT CONSTRUCT SRL", "AGREMIN SRL", "SIMION TEHNOCONSTRUCT SRL", 
                     "CLASIMI DRUM CONSTRUCT SRL", "CON INDUSTRY SRL", "DER BAU EXPERT SRL", "KHINEZU BETON SRL", 
                     "VLADCOST SRL", "MIS GRUP SRL", "REVINE IMPEX SRL", "MAGHEBO SRL", "GAV CONTRUCT SRL", "CARPAT FAUR SRL", 
                     "ADN GLOBAL EARTH", "ADROIT IMOBILIARE", "AGA TRANS", "ARCIF AG SRL", "ALCAROM SRL", "BAVARIA RESIDENCE", 
                     "BUILDARIA CONSTRUCT SRL", "ARDENT COM SRL", "CID TURISM", "COMTRANSPORT SA", "CONYSAL COMPANY SRL", 
                     "DNA RESIDENCE SRL", "DAVOGDARIS SRL", "DANZICON SRL", "ELBI SA", "EOLIAN SRL", "IOMICAR SRL", "LABIRINT SRL",
                     "OCSA CONSTRUCTII SI INFRASTRUCTURA SRL", "PALAS IMPERIUM SRL", "POLARIS CAFE SRL", "TRANS RAPID SRL", 
                     "TOP SCAV SRL", "TRECATORUL SRL", "TRASERBUS DOROHOI", "VIVAT CONSTRUCT SRL", 
                     "Alt beneficiar"]
    
    cement_classes = [
        "C 2.8/3.5", "C 4/5", "C 6/7.5", "C 8/10", "C 12/15", "C 16/20", "C 18/22.5",
        "C 20/25", "C 25/30", "C 25/35", "C 28/35", "C 32/40", "C 30/37", "C 35/45", "C 40/50", "C 50/60"
    ]
    
    # Ensure constants are valid:
    if not all(isinstance(item, str) and item for item in beneficiaries):
        raise ValueError("All items in the beneficiary list must be non-empty strings.")

    # Create the elements of the window:
    root = create_window()

    create_title(root, title_text="Încercări compresiune")

    beneficiary_dropdown, error_label_beneficiary = create_dropdown_entry(root, row_number=1, label_text="Selectați beneficiarul:", 
                          dropdown_width=29, dropdown_options=beneficiaries)
    
    date_entry, error_label_date = create_keyboard_entry(root, entry_type="date", row_number=1, column_number=1,
                                                          label_text="Introduceți data turnării (zz.ll.aaaa):")

    cement_dropdown, error_label_cement = create_dropdown_entry(root, row_number=2, label_text="Clasa betonului:", 
                                                                dropdown_width=20, dropdown_options=cement_classes)
    
    numerical_entry, error_label_numerical = create_keyboard_entry(root, entry_type="numerical", row_number=2, column_number=1,
                                                                   label_text="Introduceți numarul de teste:")
    
    internal_code_entry, error_label_internal_code = create_keyboard_entry(root, entry_type="numerical", row_number=3, column_number=0,
                                                                           label_text="Introduceți indicativul probei:")
    
    create_button(root, row_number=3, button_text="Salvează și începe testul", beneficiary_dropdown=beneficiary_dropdown, 
                  cement_dropdown=cement_dropdown, date_entry=date_entry, numerical_entry=numerical_entry, 
                  internal_code_entry=internal_code_entry, error_label_beneficiary=error_label_beneficiary, 
                  error_label_cement=error_label_cement, error_label_date=error_label_date, 
                  error_label_numerical=error_label_numerical, error_label_internal_code=error_label_internal_code, data_ready=data_ready)

    def unlock_gui():
        # Unlocking and clearing the widgets
        beneficiary_dropdown.config(state='normal')
        beneficiary_dropdown.set('')  # Clear the dropdown

        cement_dropdown.config(state='normal')
        cement_dropdown.set('')  # Clear the dropdown

        date_entry.config(state='normal')
        date_entry.delete(0, tk.END)  # Clear the entry
        
        numerical_entry.config(state='normal')
        numerical_entry.delete(0, tk.END)  # Clear the entry

        internal_code_entry.config(state='normal')
        internal_code_entry.delete(0, tk.END)  # Clear the entry

        pass

    def check_unlock_event():
        if gui_unlock.is_set():
            unlock_gui()
            gui_unlock.clear()  # Reset the event for the next cycle
        root.after(100, check_unlock_event)  # Schedule to check again after 100ms

    # Schedule the first check
    root.after(100, check_unlock_event)

    run_window(root)

if __name__ == "__main__":
    data_ready = threading.Event()
    gui_unlock = threading.Event()
    data_ready.clear()
    gui_unlock.set()  # Just call set() without arguments
    run_GUI(data_ready, gui_unlock)  # Pass both events to run_GUI
