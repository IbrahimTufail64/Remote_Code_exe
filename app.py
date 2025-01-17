from flask import Flask, request, jsonify
import os
import subprocess
app = Flask(__name__)


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




if __name__ == "__main__":
    app.run(debug=True)
