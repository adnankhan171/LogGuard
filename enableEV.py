import subprocess

def enable_failed_login_auditing():
    try:
        # Define the PowerShell command
        command = 'AuditPol /set /subcategory:"Logon" /success:enable /failure:enable'
        
        # Run the command using subprocess
        result = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,
            shell=True  # Use `shell=True` for Windows compatibility
        )

        # Check the result
        if result.returncode == 0:
            print("Failed login auditing has been enabled successfully.")
        else:
            print(f"Failed to enable auditing. Error: {result.stderr}")

    except Exception as e:
        print(f"An error occurred: {e}")

