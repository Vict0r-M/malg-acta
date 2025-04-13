#!/usr/bin/env python3
#%%

# Import functions and libraries:
import threading
import json
import os

from .data_parsing import filter_scale_data as ps
from .data_parsing import filter_compression_tester_data as pc
from .data_parsing import compile_final_data as pf

from .data_readers import read_keyboard_inputs as rk
from .data_readers import read_scale as rs
from .data_readers import read_compression_tester as rc

from .utils import create_pdf as pdf

#%%

# Function to read the file and extract the number from "numar_teste"
def extract_numerical(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            # Check if the file contains exactly one entry
            if len(data) != 1:
                return "Error: JSON file should contain exactly one entry."
            # Extract the number from "numar_teste" and convert it to an int
            numar_teste_value = int(data[0]["numar_teste"])
            return numar_teste_value
    except Exception as e:
        return f"Error reading file or extracting data: {e}"

# Extract last line of the final data file to create PDF with:
def get_last_entry(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            # Assuming the JSON structure is a list of entries
            if isinstance(data, list) and data:
                return data[-1]  # Return the last entry
            elif isinstance(data, dict):
                return data  # If the JSON structure is a single dictionary
            else:
                return None  # If the JSON is empty or has an unexpected structure
    except FileNotFoundError:
        print("File not found:", file_path)
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON from the file.")
        return None

# Event for synchronization:
data_ready = threading.Event()
gui_unlock = threading.Event()
stop_event = threading.Event()  # Event to signal threads to stop

def process_data():
    while not stop_event.is_set():
        # Wait for event to be set by GUI thread:
        data_ready.wait()
        # Reset event for next iteration:
        data_ready.clear()

        # Path relative to this script file:
        script_dir = os.path.dirname(__file__)  # Directory of the script file
        keyboard_inputs_path = os.path.join(script_dir, 'data', 'keyboard_inputs.json')
        final_data_path = os.path.join(script_dir, 'data', 'final_data.json')

        for _ in range (extract_numerical(keyboard_inputs_path)):
            rs.read_scale()
            rc.read_compression_tester()

        ps.filter_scale_data()
        pc.filter_compression_tester_data()
        pf.compile_final_data()
        pdf.printPDFV2(get_last_entry(final_data_path))

        # Set the gui_unlock event
        gui_unlock.set()

        if stop_event.is_set():
            break  # Exit the loop if stop signal is received

def run_app():
    rk.run_GUI(data_ready, gui_unlock)
    stop_event.set()  # Signal the process_data thread to stop

# Threads setup:
data_processing_thread = threading.Thread(target=process_data, daemon=True)

# Starting threads:
data_processing_thread.start()
run_app()
