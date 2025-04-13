import json
import re
import os

def filter_scale_data():
    script_dir = os.path.dirname(__file__)  # Directory of the script file
    scale_data_path = os.path.join(script_dir, '..', 'data', 'scale_data.json')
    
    try:
        with open(scale_data_path, "r") as f:
            data = json.load(f)
        
        filtered_data = []
        for entry in data["data"]:
            # Extract numerical value using regular expression
            match = re.search(r"(\d+\.\d+)", entry)
            if match:
                filtered_data.append(match.group(1))
        
        with open(scale_data_path, "w") as f:
            json.dump({"data": filtered_data}, f)

        print("Scale data has been filtered.")

    except Exception as e:
        print(f"An error occurred while filtering scale data: {e}")

if __name__ == '__main__':
    filter_scale_data()