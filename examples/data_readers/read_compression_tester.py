import serial
import json
import os

def read_compression_tester():
    # Path relative to this script file
    script_dir = os.path.dirname(__file__)  # Directory of the script file
    compression_path = os.path.join(script_dir, '..', 'data', 'compression_tester_data.json')
    
    try:
        ser = serial.Serial(
            port='/dev/ttyACM0',
            baudrate=38400,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            xonxoff=True,
            timeout=1
        )
        
        if not os.path.exists(compression_path) or os.path.getsize(compression_path) == 0:
            existing_data = {"data": []}
        else:
            with open(compression_path, 'r') as f:
                existing_data = json.load(f)
        
        flag = True
        while flag:
            data = ser.readline().decode("utf-8", errors='ignore').strip()
            if data:
                existing_data["data"].append(data)
                with open(compression_path, 'w') as f:
                    json.dump(existing_data, f)
                
                flag = False
                                
    except Exception as e:
        print(f"An error occurred with the compression tester: {e}")
