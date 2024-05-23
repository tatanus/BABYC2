import cmd
import importlib.util
import os
import threading
from time import sleep

from globalvars import GlobalVar
from c2exception import BackgroundSession, KillAgent
from protocols.c2prototemplate import C2ProtoTemplate

_SESSIONS = GlobalVar._SESSIONS


class C2Base(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "Main > "
        self.interacting = None
        self.listeners = {}

    def addListener(self, sessiontype, listener):
        self.listeners[sessiontype] = listener

    def do_interact(self, cmd):
        """interact <session_id>
        Sets the agent that you want to interact with"""
        if cmd in _SESSIONS.keys():
            session_type = _SESSIONS[cmd].get_type()
            self.listeners[session_type].activeSession = cmd
            self.listeners[session_type].prompt = f"Session {cmd} > "

            print(f"Interacting with session {cmd} ({session_type}). Type 'back' to return to the main prompt.")

            try:
                self.listeners[session_type].cmdloop()
            except BackgroundSession as e:
                pass
            except KillAgent as e:
                _SESSIONS[cmd].close()
                pass
        else:
            print("Please choose a valid session")

    def complete_interact(self, text, line, start_index, end_index):
        results = []
        for key in _SESSIONS.keys():
            if key.startswith(text):
                results.append(key)
        if len(results) == 0:
            results = _SESSIONS.keys()
        return results

    def do_list(self, cmd):
        """list
        Lists all agent ID's and Hostnames"""
        self.do_sessions(cmd)

    def do_listeners(self, cmd):
        """listeners
        Lists all active listeners"""
        for listener_type, listener in self.listeners.items():
            print(f"{listener_type} - ({listener.port})")

    def do_sessions(self, cmd):
        """sessions
        Lists all agent ID's and Hostnames"""
        for session_id, session in _SESSIONS.items():
            print(str(session))

    def do_exit(self, cmd):
        """exit
        Exit and shutdown the c2 server."""

        # close all active sessions
        for session_id, session in _SESSIONS.items():
            session.close()

        # close all listeners
        for listener_type, listener in self.listeners.items():
            listener.close()

        return True

    def emptyline(self):
        pass


def main():
    # Display Banner
    print(GlobalVar._BANNER)
    print(f"Version: {GlobalVar._VERSION}")
    print("Created by: Adam Compton @tatanus\n")

    # Initialize the base class
    c2base = C2Base()

    # Add in additional protocol listeners
    print("Starting Protocol Listeners")

    # Iterate over each module in the protocols directory
    for filename in os.listdir("protocols"):
        if filename.endswith(".py"):
            module_name = filename[:-3]  # Remove the ".py" extension
            module_path = f"protocols.{module_name}"
            module_spec = importlib.util.find_spec(module_path)
            if module_spec:
                module = importlib.util.module_from_spec(module_spec)
                module_spec.loader.exec_module(module)

                # Find classes that inherit from C2ProtoTemplate
                for name in dir(module):
                    obj = getattr(module, name)
                    if hasattr(obj, "__bases__") and C2ProtoTemplate in obj.__bases__:
                        listener_instance = obj()  # Create an instance of the class
                        if listener_instance.enabled:
                            c2base.addListener(listener_instance.session_type, listener_instance)
                            sleep(1)

    print("")

    # Start the main loop in a separate thread
    def run_cmdloop():
        c2base.cmdloop()

    cmdloop_thread = threading.Thread(target=run_cmdloop)
    cmdloop_thread.start()


if __name__ == "__main__":
    main()
