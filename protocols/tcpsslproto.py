import os
import socket
import ssl
import threading
import uuid

from c2session import C2Session
from globalvars import GlobalVar
from protocols.c2prototemplate import C2ProtoTemplate

_SESSIONS = GlobalVar._SESSIONS


class TCP_SSL_Proto(C2ProtoTemplate):
    def __init__(self, host: str = "0.0.0.0", port: int = 4000):
        C2ProtoTemplate.__init__(self, host, port)
        self.prompt = "TCP (ssl) Session > "
        self.session_type = "tcp_ssl"
        self.enabled = True

        if self.enabled:
            self.start()
            self.connThread = threading.Thread(target=self.accept_connections)
            self.connThread.start()

    def start(self) -> None:
        self.certfile = "server.pem"
        self.generate_certificate(self.certfile)
        self.ssl_context = None

        try:
            # Create a self-signed SSL certificate
            self.generate_certificate(self.certfile)

            self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            self.ssl_context.check_hostname = False
            self.ssl_context.load_cert_chain(self.certfile)

            self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            self.listener.bind((self.host, self.port))
            self.listener.listen(10)

            print(f"{self.host}:{self.port} - TCP (ssl) listener")
        except Exception as e:
            print(f"Error starting server: {e}")

    def generate_certificate(self, cert_file="server.pem"):
        # Check if certificate file exists
        if not os.path.exists(cert_file):
            # Generate a self-signed certificate
            os.system(
                f"openssl req -x509 -newkey rsa:4096 -keyout {cert_file} -out {cert_file} -days 365 -nodes -subj '/CN=localhost'")

    def accept_connections(self) -> None:
        while True:
            try:
                client_socket, client_address = self.listener.accept()
                mysslsocket = self.ssl_context.wrap_socket(client_socket, server_side=True)

                session_id = str(uuid.uuid4())[:8]
                self.activeSession = session_id
                temp_session = C2Session(session_id, mysslsocket, "tcp_ssl")
                temp_session.set_address(client_address)

                _SESSIONS[session_id] = temp_session
                print(f"New session created: {session_id} - {client_address[0]} (tcp_ssl)")
                self.get_system_info()
                threading.Thread(target=self.handle_session, args=(session_id,)).start()
            except Exception as e:
                print(f"Error accepting tcp connection: {e}")
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
        session.get_socket().sendall(command.encode('utf-8') + b"\n")

    def recv_response(self, session_id: str) -> str:
        session = _SESSIONS[session_id]
        data = session.get_socket().recv(1024).decode()
        return data.strip()