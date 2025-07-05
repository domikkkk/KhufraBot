import socket
import threading
from multicast import Multicast, MCAST_PORT, MCAST_GRP
from typing import Dict
from message import Message


TCP_PORT = 12345


class Broker:
    def __init__(self):
        self.multicast: Multicast = Multicast()
        self.dc_bots: Dict[str, str] = {}
        self.bots: Dict[str, str] = {}
        self.port = TCP_PORT

    def udp_multicast_discovery(self):
        sock = self.multicast.udp_discovery()
        while True:
            data, addr = sock.recvfrom(1024)
            msg = Message.from_bytes(data)
            message = msg.content.decode('utf-8', errors='ignore')
            print(f"Otrzymano od {addr}: {message}")
            if message == "DISCOVER_BROKER":
                if msg.bot_type == '1':
                    self.dc_bots[msg.bot_id] = addr
                elif msg.bot_type == '2':
                    self.bots[msg.bot_id] = addr
                response = f"BROKER_IP={self.multicast.local_ip};BROKER_PORT={self.port}"
                sock.sendto(response.encode('utf-8'), addr)


def handle_client(conn, addr):
    print(f"Nowe połączenie od {addr}")
    try:
        bot_id = conn.recv(1024).decode().strip()
        if not bot_id:
            conn.close()
            return
        clients[bot_id] = conn
        print(f"Bot zalogowany z ID: {bot_id}")

        while True:
            data = conn.recv(1024)
            if not data:
                break
            try:
                target_id, msg = data.decode().split('|', 1)
            except Exception:
                print(f"Niepoprawny format wiadomości od {bot_id}")
                continue
            if target_id in clients:
                clients[target_id].sendall(f"Od {bot_id}: {msg}".encode())
            else:
                conn.sendall(f"Bot {target_id} nie jest podłączony.".encode())
    except Exception as e:
        print(f"Błąd w połączeniu z {addr}: {e}")
    finally:
        print(f"Rozłączono {addr}")
        if bot_id in clients:
            del clients[bot_id]
        conn.close()


def tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', TCP_PORT))
    server.listen()
    print(f"TCP serwer działa na porcie {TCP_PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


def main():
    broker = Broker()
    threading.Thread(target=broker.udp_multicast_discovery, daemon=True).start()
    # threading.Thread(target=tcp_server, daemon=True).start()

    print("Serwer uruchomiony. Ctrl+C, aby zakończyć.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Zamykanie serwera...")


if __name__ == "__main__":
    main()
