import json
import os

def compile_final_data():
    script_dir = os.path.dirname(__file__)  # Directory of the script file
    scale_data_path = os.path.join(script_dir, '..', 'data', 'scale_data.json')
    compression_data_path = os.path.join(script_dir, '..', 'data', 'compression_tester_data.json')
    keyboard_data_path = os.path.join(script_dir, '..', 'data', 'keyboard_inputs.json')
    final_data_path = os.path.join(script_dir, '..', 'data', 'final_data.json')
    
    try:
        final_data = []

        with open(keyboard_data_path, "r") as f:
            keyboard_inputs = json.load(f)
        
        with open(scale_data_path, "r") as f:
            scale_data_filtered = json.load(f)['data']
        
        with open(compression_data_path, "r") as f:
            compression_tester_data_filtered = json.load(f)['data']


        for keyboard_input in keyboard_inputs:
            numar_teste = int(keyboard_input["numar_teste"])
            internal_code = int(keyboard_input["internal_code"])
            series_data = {
                "probe_date": keyboard_input["probe_date"],
                "beneficiar": keyboard_input["beneficiar"],
                "clasa_betonului": keyboard_input["clasa_betonului"],
                "numar_teste": numar_teste,
                "tests": [],
                "internal_code": internal_code
            }
            
        for i in range(numar_teste):
            # Extract try_date before creating test_data:
            try_date = compression_tester_data_filtered[i].get('try_date')
            
            # Create a copy of compression data without try_date:
            compression_data = compression_tester_data_filtered[i].copy()
            if 'try_date' in compression_data:
                del compression_data['try_date']
            
            test_data = {
                "scale_data": scale_data_filtered[i],
                "compression_data": compression_data
            }
            series_data["tests"].append(test_data)
            
            # Update series_data try_date (last one will persist):
            if try_date:
                series_data["try_date"] = try_date
        
        final_data.append(series_data)

        with open(final_data_path, "w") as f:
            json.dump(final_data, f, indent=4)

        print("Data compiled successfully into final_data.json.")

        # Clearing the other files:
        for path in [scale_data_path, compression_data_path, keyboard_data_path]:
            with open(path, "w") as f:
                pass  # Don't write anything to the file

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        print("Exception traceback:")
        traceback.print_exc()