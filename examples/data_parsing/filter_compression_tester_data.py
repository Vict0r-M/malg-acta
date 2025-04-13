import json
import re
import os
from datetime import datetime

def filter_compression_tester_data():
    script_dir = os.path.dirname(__file__)  # Directory of the script file
    compression_path = os.path.join(script_dir, '..', 'data', 'compression_tester_data.json')
    #raw_data_path = os.path.join(script_dir, '..', 'data', 'raw_compression_tester_data.json')
    
    try:
        with open(compression_path, "r") as f:
            data = json.load(f)
            
        # Save raw data before filtering:
        #with open(raw_data_path, "w") as f:
        #    json.dump(data, f)
        
        filtered_data = []
        for entry in data["data"]:
            # Extract kN value (e.g., "Fm [ kN    ]: 45.32" -> "45.32"):
            kN_match = re.search(r"Fm \[ kN    \]:\s*([\d\.]+)", entry)
            
            # Extract MPa value (e.g., "Rm [ MPa   ]: 892.45" -> "892.45"):
            MPa_match = re.search(r"Rm \[ MPa   \]:\s*([\d\.]+)", entry)

            # Extract date (e.g., "04/02/25       14:34:36" -> "04/02/25"):
            date_match = re.search(r"(\d{2}/\d{2}/\d{2})\s+\d{2}:\d{2}:\d{2}", entry)

            if kN_match and MPa_match and date_match:
                kN_value = kN_match.group(1)
                MPa_value = MPa_match.group(1)

                # Convert date from DD/MM/YY to DD.MM.YYYY:
                date_str = date_match.group(1)
                try:
                    date_obj = datetime.strptime(date_str, "%d/%m/%y")
                    formatted_date = date_obj.strftime("%d.%m.%Y")
                except ValueError as e:
                    print(f"Error parsing date {date_str}: {e}")
                    formatted_date = None

                # Creates clean key-value pairs (e.g., {"kN": "45.32", "MPa": "892.45", "try_date": "04.02.2025"}):
                filtered_data.append({
                    "kN": kN_value,
                    "MPa": MPa_value,
                    "try_date": formatted_date
                })
        
        with open(compression_path, "w") as f:
            json.dump({"data": filtered_data}, f)

        print("Compression tester data has been filtered.")

    except Exception as e:
        print(f"An error occurred while filtering compression tester data: {e}")

if __name__ == '__main__':
    filter_compression_tester_data()