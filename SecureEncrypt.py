#   Python Encryption Method
#   2026 (C) Elijah Martin
#   This script will establish communications over HTTPS and send
#   an encrypted file that will be decrypted by the receiving script.
import time
import random
import string
import socket
import getpass
import paramiko
import re
# Fix for Paramiko 4.0+ compatibility with sshtunnel
if not hasattr(paramiko, 'DSSKey'):
    paramiko.DSSKey = paramiko.RSAKey
from sshtunnel import SSHTunnelForwarder
import os

# Configuration
SSH_HOST = '127.0.0.1'
SSH_USER = getpass.getuser()  # Automatically gets your current OS username
# If you don't use SSH keys, sshtunnel will prompt for your OS password in the console
# SSH_PKEY = "C:/Users/Name/.ssh/id_rsa"
KEY_PATH = os.path.expanduser(r"C:\Users\Elija\OneDrive\Documents\ANOMALYZER AI\key")
REMOTE_SERVICE_PORT = 12345
LOCAL_TUNNEL_PORT = 9000

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

# Command line Interface
print("<-- Data collection -->")
text = input("Enter text to be encrypted: ")
print("The text to be ecnrypted is: " + text)
def waitforuser():
    input("encrypto-matic@" + socket.gethostname() + ": ")

def encrypt(text):
    cryptoarray = []
    cryptotext = ""
    for letter in text:
        a = ''.join(random.choices(string.ascii_letters, k=random.randint(3, 20)))
        cryptoarray.append(a)
        cryptotext = cryptotext + str(a)
    print(cryptoarray)
    return cryptoarray, cryptotext




def GeneratePreamble(array):
    Preamble = ""
    for index in array:
        b = len(str(index))
        print(index + " : " + str(b))
        Preamble = str(Preamble + str(keyruleset[int(b)]))
    print("Generated Key Preamble: " + Preamble)
    waitforuser()
    return Preamble

def GenerateKey(Preamble):
    key = ""
    for i in Preamble:
        key = key + str(arr[int(i)])
    print(key)
    return key

def FormFrame(preamble, key, payload):
    frame = str(preamble + "|" + key + "|" + payload)
    print("Generated frame: " + frame)
    return frame

def send_data(s, port):
        message = str(Frame)
        s.sendall(message.encode())
        print(f"[*] Sender: Encypted Message sent to local tunnel port {port}")
        time.sleep(0.2)
        s.sendall("EXIT_SIGNAL".encode())

def recv_until_terminator(sock, terminator="EXIT_SIGNAL"):
    """Rebuilds fragmented data until the terminator is found."""
    buffer = b""
    while not buffer.endswith(terminator.encode()):
        chunk = sock.recv(1024)
        if not chunk:  # Connection closed unexpectedly
            return None
        buffer += chunk
    return buffer.decode('utf-8').strip()

def ValidateChunks(sock, key, cryptoarray, text):
    charNum = 0
    for i, chunk in enumerate(cryptoarray):
        letter = text[i]
        # 1. Use the helper to get the FULL message
        r = recv_until_terminator(sock, "\n")
        print(r + "READ THE ABOVE")
        if not r: break

        # 2. Split safely
        k = r.split("|", 2)
        if len(k) < 3:
            continue
        print(k)

        chunk_received, key_received = k[1], k[2]

        if chunk_received == str(chunk) and key_received == str(key):
            print(f"[+] Verified chunk {i}. Sending: {letter}")
            # Add \n so the Receiver knows this letter is a complete message
            sock.sendall(f"{charNum}|{letter}".encode('utf-8'))
            time.sleep(0.05) # Small sync for Windows SSH
            sock.sendall("|EXIT_SIGNAL".encode())
            charNum += 1
        else:
            print(f'chunk_received:{chunk} + key_received:{key} \n Chunk or Key Mismatch!')

def run_tunnel(pmb, k, cryptoarray):
    # 1. Explicitly load Ed25519 key to bypass Paramiko 4.0+ DSSKey errors
    if not os.path.exists(KEY_PATH):
        print(f"[!] Error: Key not found at {KEY_PATH}. Generate it first!")
        return

    mypkey = paramiko.Ed25519Key.from_private_key_file(KEY_PATH)

    # 2. Setup and start the tunnel
    with SSHTunnelForwarder(
        (SSH_HOST, 22),
        ssh_username=SSH_USER,
        ssh_pkey=mypkey,
        remote_bind_address=('127.0.0.1', REMOTE_SERVICE_PORT),
        local_bind_address=('127.0.0.1', LOCAL_TUNNEL_PORT)
    ) as tunnel:
        print(f"[*] Tunnel: Active at 127.0.0.1:{tunnel.local_bind_port}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', tunnel.local_bind_port))

            # Use the tunnel
            time.sleep(0.5)
            send_data(s, tunnel.local_bind_port)
            time.sleep(0.2)
            ValidateChunks(s, k, cryptoarray, text)
            input("Transmission complete. Press Enter to tear down the tunnel...")




        print("[*] Tunnel: Closing...")

EncryptionArray, EncryptedText = encrypt(text)
print("Successfully Encrypted text: " + "\n" + EncryptedText)
print("Encrypting the dictionary now...")
x = GeneratePreamble(EncryptionArray)
key = GenerateKey(x)
print("Generated Key from the Preamble... Ready to decrypt!!!")
print("Press enter to open a local connection and send to the receiver....")
# Form a frame so the receiver can separate the Preamble, Key and Payload.
Frame = FormFrame(x, key, EncryptedText)



while True:
    run_tunnel(x, key, EncryptionArray)
    waitforuser()
    pass
