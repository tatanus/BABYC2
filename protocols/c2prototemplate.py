import cmd
import socket
from c2exception import BackgroundSession, KillAgent
from globalvars import GlobalVar

_SESSIONS = GlobalVar._SESSIONS

class C2ProtoTemplate(cmd.Cmd):
    def __init__(self, host: str = "0.0.0.0", port: int = 4446):
        cmd.Cmd.__init__(self)
        self.prompt = "Session > "
        self.host = host
        self.port = self.find_available_port(port)  # Find an available port
        self.listener = None
        self.connThread = None
        self.activeSession = None
        self.enabled = False
        self.session_type = "proto_template"

    def close(self):
        if self.listener:
            self.listener.close()
        if self.connThread:
            self.connThread.join()

    def find_available_port(self, start_port):
        port = start_port
        while True:
            if not self.is_port_in_use(port):
                return port
            port += 1

    def is_port_in_use(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("localhost", port))
            except socket.error as e:
                return True  # Port is already in use
            return False  # Port is available

    def start(self) -> None:
        pass

    def accept_connections(self) -> None:
        pass

    def get_system_info(self) -> None:
        self.send_command("uname -s")
        data = self.recv_response(self.activeSession)
        _SESSIONS[self.activeSession].set_os(data)
        self.send_command("hostname")
        data = self.recv_response(self.activeSession)
        _SESSIONS[self.activeSession].set_hostname(data)
        self.send_command("whoami")
        data = self.recv_response(self.activeSession)
        _SESSIONS[self.activeSession].set_user(data)
        self.send_command("pwd")
        data = self.recv_response(self.activeSession)
        _SESSIONS[self.activeSession].set_pwd(data)
    
    def process_results(self, session_id: str) -> None:
        pass
    
    def send_command(self, cmd: str) -> None:
        pass

    def recv_response(self, session_id: str) -> str:
        pass

    def default(self, cmd) -> None:
        self.send_command(cmd)
        self.process_results(self.activeSession)

    def do_back(self, arg):
        """Exit the shell"""
        print("Exiting session...")
        raise BackgroundSession        

    def do_exit(self, arg):
        """Exit the agent"""
        session = _SESSIONS[self.activeSession]
        cmd = "exit"
        command = f'{cmd}'  # Wrap command in quotes
        session.get_socket().sendall(command.encode('utf-8') + b"\n")
        """Kill the agent"""
        raise KillAgent 

    def do_screenshot(self, arg):
        """Take a screenshot of the agent's screen"""
        pass

    def do_upload(self, arg):
        """Upload a file to the agent"""
        pass

    def do_download(self, arg):
        """Download a file from the agent"""
        pass

    def do_spawn(self, arg):
        """Spawn a new/different shell on the agent"""
        pass

    def emptyline(self):
        pass

    @staticmethod
    def is_empty_or_whitespace(s: str) -> bool:
        return s is None or len(s.strip()) == 0
