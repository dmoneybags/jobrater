'''
Simple class of helper functions.

Miscellaneous, no common theme
'''
import os

class HelperFunctions:
    '''
    write_pid_to_temp_file

    args:
        caller_name: str, the name of the file we are being
        called from
    '''
    def write_pid_to_temp_file(caller_name: str):
        file_path: str = os.path.join(os.getcwd(), "src", "background", "temp", caller_name + "_pid")
        print("Writing pid to " + file_path)
        try:
            with open(file_path, "w") as f:
                f.write(str(os.getpid()))
                print("Successfully wrote PID: " + str(os.getpid()) + " FOR " + caller_name)
        except OSError as e:
            print(f"Error writing PID to file: {e}")
            print("failing writing PID: FOR " + caller_name)
    def remove_pid_file(caller_name: str):
        file_path: str = os.path.join(os.getcwd(), "src", "background", "temp", caller_name + "_pid")
        print(file_path)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print("Removed temp file for " + caller_name)
        else:
            print("Can't remove PID " + file_path + " does not exist")
