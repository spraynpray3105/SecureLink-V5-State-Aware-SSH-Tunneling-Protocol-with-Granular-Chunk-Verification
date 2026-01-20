#   Python Encryption Method
#   2026 (C) Elijah Martin
#   This script will establish communications over SSH and send
#   an encrypted file that will be decrypted by the receiving script.
import time
import random
import string
import socket
import re

# This ruleset is used to generate the key utilizing the Preamble.
# It will be in the decryptor code too.
keyruleset = [
  746,
  482,
  903,
  526,
  120,
  864,
  671,
  401,
  999,
  342,
  205,
  508,
  911,
  600,
  145,
  733,
  100,
  389,
  193,
  243,
  912
]

arr = [
    8401927359184,
    42,
    591028374650192837,
    905,
    730194615,
    371904582103,
    7,
    903817264509183,
    52910482,
    81029384756019234,
    3817,
    4729103847562019,
    90572183419,
    59102837465019,
    1904837,
    60219,
    847302,
    4820193746,
    1023040401025,
    102303532145,
    121042445
]
frame = ""
message = ""
def extractor(frame):
    data = frame.split("|", 2)
    print(data)
    return data


def DecryptPreamble(strings):
    string = strings + " "
    Preamble = []
    counter = 0
    segment = ""
    for i in string:
        if counter <= 2:
            segment = segment + str(i)
            counter += 1
        else:
            counter = 1
            Preamble.append(str(keyruleset.index(int(segment))))
            segment = str(i)
    print(Preamble)
    return Preamble

def GenerateKey(Preamble):
    key = ""
    for i in Preamble:
        key = key + str(arr[int(i)])
    print(key)
    return key

def MakeChunks(preamble, encryptedText):
    chunks = []
    current_index = 0
    for size in preamble:
        chunk = encryptedText[current_index : current_index + int(size)]
        if chunk:
            chunks.append(chunk)
        current_index += int(size)
    return chunks

def recv_until_terminator(sock, terminator="EXIT_SIGNAL"):
    """Rebuilds fragmented data until the terminator is found."""
    buffer = b""
    while not buffer.endswith(terminator.encode()):
        chunk = sock.recv(1024)
        if not chunk:  
            return None
        buffer += chunk
    return buffer.decode('utf-8').strip()

def QueryChunk(sock, chunks, key):
    s = sock
    package = ""
    message = ""
    i = 0
    message_map = {} # Use a dictionary to store letters by their index
    for chunk in chunks:
        package = f"{i}|{chunk}|{key}\n"
        s.sendall(package.encode())
        i += 1
        time.sleep(0.2)
        s.sendall("EXIT_SIGNAL".encode())
        time.sleep(0.2)
        print("Chunk Sent, awaiting validation.")
        while True:
            response = recv_until_terminator(s, "EXIT_SIGNAL")
            if not response:
                break
            if "EXIT_SIGNAL" in response:
                response = re.sub("EXIT_SIGNAL", "", response)
                break
            if response:
                idx, letter = response.split("|")
                message_map[int(idx)] = letter
            final_message = "".join([message_map[i] for i in sorted(message_map.keys())])
    message = final_message
    print(message)
    return message


def run_receiver():
    # We bind to 127.0.0.1 so only the SSH tunnel can reach it
    host, port = '127.0.0.1', 12345

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(1)
        print(f"[*] Receiver: Listening on {host}:{port}...")



        while True:
            conn, addr = s.accept()
            buffer = ""
            with conn:
                print(f"[*] Receiver: Connection from {addr}")
                while True:
                    data = conn.recv(4096)
                    if not data:
                        break
                    if "EXIT_SIGNAL".encode() in data:
                        print("[*] Receiver: Downloaded Encrypted Data.")
                        data = re.sub("EXIT_SIGNAL".encode(), "".encode(), data)
                        buffer += str(data.decode())
                        break
                    buffer += str(data.decode())
                if buffer:
                    print(f"[!] Receiver: Success! Data received: '{buffer}'")
                    a = extractor(str(buffer))
                    preamble = DecryptPreamble(a[0])
                    print("Decrypted preamble! \n" + str(preamble))
                    x = GenerateKey(a[0])
                    if x == str(a[1]):
                        print("Matching Authentication Key Generated.")
                        chunks = MakeChunks(preamble, a[2])
                        message = QueryChunk(conn, chunks, x)
                        print(message)
                        input("Press enter to ")
                    else:
                        print("Key Gen failed.")
                if not data:
                    break
                print(f"[!] Received: {data.decode('utf-8', errors='ignore')}")
if __name__ == "__main__":
    run_receiver()

