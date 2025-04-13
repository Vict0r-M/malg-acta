import serial
import json
import os

def read_scale():
    # Path relative to this script file
    script_dir = os.path.dirname(__file__)  # Directory of the script file
    scale_data_path = os.path.join(script_dir, '..', 'data', 'scale_data.json')
    
    try:
        ser = serial.Serial(
            port='/dev/ttyACM1',
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            xonxoff=True,
            timeout=1
        )
        
        if not os.path.exists(scale_data_path) or os.path.getsize(scale_data_path) == 0:
            existing_data = {"data": []}
        else:
            with open(scale_data_path, 'r') as f:
                existing_data = json.load(f)

        flag = True
        while flag:
            data = ser.readline().decode("utf-8", errors='ignore').strip()
            if data:
                existing_data["data"].append(data)
                with open(scale_data_path, 'w') as f:
                    json.dump(existing_data, f)

                flag = False
                                
    except Exception as e:
        print(f"An error occurred with the scale: {e}")