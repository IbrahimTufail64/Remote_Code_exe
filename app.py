from flask import Flask, request, jsonify
import os
import subprocess
import requests
from flask_apscheduler import APScheduler
import datetime

app = Flask(__name__)

class Config:
    SCHEDULER_API_ENABLED = True

app.config.from_object(Config)

scheduler = APScheduler()
scheduler.init_app(app)

#global variable 
current_exe_script = "scripts.exe"
current_hex_script = "scripts.hex"
target_url = "https://remote-code-cloud.onrender.com"


# --- API Endpoints ---

@app.route("/submit_exe",methods=['POST']) 
def recieve_file():
    file = request.files.get('exe_file')

    print(file)
    # save the file
    UPLOAD_FOLDER = os.path.abspath("./formdata_exe_files")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the folder exists
    
    if file:
        file.save(f"./formdata_exe_files/{file.filename}");
        file_info = {"filename": file.filename, "content_type": file.content_type}
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        subprocess.call(["open", file_path])
        # os.startfile(file_path)
        return jsonify(file_info),200
    return jsonify({"Error": "Can't create file"}),400


@app.route('/flash_hex', methods=['POST'])
def flash_hex():
    hex_file = request.files.get('hex_file')

    if not hex_file:
        return jsonify({"error": "No hex file provided"}), 400

    try:
        # Save the uploaded hex file to a specific directory
        UPLOAD_FOLDER = os.path.abspath("./formdata_hex_files")
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the folder exists

        file_path = os.path.join(UPLOAD_FOLDER, hex_file.filename)
        hex_file.save(file_path)

        # avrdude command
        com_port = "/dev/ttyUSB0"  # Replace with your device's actual port
        command = [
            "avrdude",
            "-v",  # Verbose output
            "-patmega328p",  # Change this based on your Arduino model
            "-carduino",  # Programmer type
            f"-P{com_port}",  # Device path (Linux)
            "-b115200",  # Baud rate
            f"-Uflash:w:{file_path}:i"  # Write the hex file to flash memory
        ]

        # Execute the avrdude command
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            # Flashing failed
            return jsonify({"error": "Flashing failed", "details": result.stderr}), 500

        # Flashing succeeded
        return jsonify({"message": "Flashing successful", "details": result.stdout})

    except Exception as e:
        # Handle exceptions
        return jsonify({"error": "An error occurred while flashing", "details": str(e)}), 500


def fetch_execute_exe():
    global target_url, current_exe_script
    
    # Make a request to fetch the file
    UPLOAD_FOLDER = os.path.abspath("./formdata_exe_files")
    response = requests.get(f"{target_url}/get-exe/{current_exe_script}", stream=True)
    
    if response.status_code == 200:
        # Save the file
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the folder exists
        
        # Extract the file name from the headers or use a default
        # filename = response.headers.get('Content-Disposition', '').split('filename=')[-1].strip('"') or "downloaded_file.inf"
        filename = current_exe_script
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Write the binary content to a file
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        print(f"File saved at {file_path}")
        
        # Execute the file (Linux specific)
        # try:
            # Use subprocess to execute the file
            
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        print(file_path)
        # os.startfile(file_path) # for windows only
        command = [
            "wine",
            f"./formdata_exe_files/{current_exe_script}"
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) # for linux
        # subprocess.call(["open", file_path])
            # result = subprocess.run(["chmod", "+x", file_path], check=True)
            # execution_result = subprocess.run([file_path], check=True)
        print(f"File executed successfully: ")
        # except Exception as e:
        #     print(f"Error while executing the file: {e}")
    else:
        print(f"Failed to fetch file: {response.status_code}, {response.text}")

def fetch_execute_hex():
    global target_url, current_hex_script
    
    # Make a request to fetch the file
    UPLOAD_FOLDER = os.path.abspath("./formdata_hex_files")
    response = requests.get(f"{target_url}/get-hex/{current_hex_script}", stream=True)
    
    if response.status_code == 200:
        # Save the file
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the folder exists
        
        # Extract the file name from the headers or use a default
        # filename = response.headers.get('Content-Disposition', '').split('filename=')[-1].strip('"') or "downloaded_file.inf"
        filename = current_hex_script
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Write the binary content to a file
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        print(f"File saved at {file_path}")
        
        # Execute the file (Linux specific)
        # try:
            # Use subprocess to execute the file
            
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        print(file_path)
        com_port = "/dev/ttyUSB0"  # Replace with your device's actual port
        command = [
            "avrdude",
            "-v",  # Verbose output
            "-patmega328p",  # Change this based on your Arduino model
            "-carduino",  # Programmer type
            f"-P{com_port}",  # Device path (Linux)
            "-b115200",  # Baud rate
            f"-Uflash:w:{file_path}:i"  # Write the hex file to flash memory
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print(f"File executed successfully: {result}")
        # except Exception as e:
        #     print(f"Error while executing the file: {e}")
    else:
        print(f"Failed to fetch file: {response.status_code}, {response.text}")

def pool_for_exe():
    global target_url
    global current_exe_script
    print("Scheduler task running...")  # Add a log here

    try:
        # Make a GET request to the target server
        response = requests.get(f"{target_url}/pool-for-exe")
        print(f"Response status code: {response.status_code}")  # Log status code

        if response.status_code == 200:
            data = response.json()
            print(f"Fetched data: {data['file_name']}")  # Log fetched data
            
            if(data['file_name'] != current_exe_script):
                current_exe_script = data['file_name']
                fetch_execute_exe()
                
            return "Data fetched successfully"
        else:
            print(f"Failed to fetch data: {response.text}")  # Log response text
            return "Failed to fetch data"
    except Exception as e:
        print(f"Exception occurred: {e}")  # Log any exception
        return str(e)
        
def pool_for_hex():
    global target_url
    global current_hex_script
    print("Scheduler task running...")  # Add a log here

    try:
        # Make a GET request to the target server
        response = requests.get(f"{target_url}/pool-for-hex")
        print(f"Response status code: {response.status_code}")  # Log status code

        if response.status_code == 200:
            data = response.json()
            print(f"Fetched data: {data['file_name']}")  # Log fetched data
            
            if(data['file_name'] != current_hex_script):
                current_hex_script = data['file_name']
                fetch_execute_hex()
                
            return "Data fetched successfully"
        else:
            print(f"Failed to fetch data: {response.text}")  # Log response text
            return "Failed to fetch data"
    except Exception as e:
        print(f"Exception occurred: {e}")  # Log any exception
        return str(e)
        
scheduler.add_job(id='Scheduled Task', func=pool_for_exe, trigger='interval', seconds=20)
scheduler.add_job(id='Scheduled Task2', func=pool_for_hex, trigger='interval', seconds=20)


if __name__ == "__main__":
    scheduler.start()
    app.run(debug=True)
