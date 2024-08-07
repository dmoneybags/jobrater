'''
Simple class of helper functions.

Miscellaneous, no common theme
'''
import os
import signal
import sys

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
    '''
    remove_pid_file

    removes the pid file for the process as part of its graceful shutdown

    args:
        caller_name: the caller requesting for their pid to be deleted
    '''
    def remove_pid_file(caller_name: str):
        file_path: str = os.path.join(os.getcwd(), "src", "background", "temp", caller_name + "_pid")
        print(file_path)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print("Removed temp file for " + caller_name)
        else:
            print("Can't remove PID " + file_path + " does not exist")
    '''
    handle_sigterm

    graceful shutdown on rebuild, handles kill -TERM

    args:
        caller_name: the name of the caller, helps us locate the pid file
    '''
    def handle_sigterm(caller_name: str):
        print("Received SIGTERM. Shutting down gracefully...")
        HelperFunctions.remove_pid_file(caller_name)
