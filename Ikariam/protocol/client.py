import socket
import threading


MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007


def discover_server(timeout=5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(timeout)

    message = "DISCOVER_BROKER".encode('utf-8')
    sock.sendto(message, (MCAST_GRP, MCAST_PORT))
    try:
        data, addr = sock.recvfrom(1024)
        response = data.decode('utf-8')
        print(f"Znaleziono serwer: {response} od {addr}")
        parts = dict(part.split('=') for part in response.split(';'))
        ip = parts.get('BROKER_IP')
        port = int(parts.get('BROKER_PORT'))
        return ip, port
    except socket.timeout:
        print("Nie znaleziono serwera (timeout)")
        return None, None


def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024)
            if data:
                print("\n[Otrzymano]:", data.decode())
            else:
                print("Serwer rozłączył połączenie.")
                break
        except Exception as e:
            print(f"Błąd odbierania: {e}")
            break


def main():
    ip, port = discover_server()
    if not ip:
        return

    bot_id = input("Podaj ID bota: ").strip()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    sock.sendall(bot_id.encode())

    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    print("Wpisuj wiadomości w formacie target_id|wiadomość")
    while True:
        try:
            msg = input()
            if msg.lower() in ('exit', 'quit'):
                break
            sock.sendall(msg.encode())
        except Exception as e:
            print("Błąd:", e)
            break

    sock.close()
    print("Zakończono klienta.")


if __name__ == "__main__":
    main()
