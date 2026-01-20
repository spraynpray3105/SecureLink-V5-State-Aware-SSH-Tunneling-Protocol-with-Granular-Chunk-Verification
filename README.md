# SecureLink-SSH: Active-Verification Tunneling Protocol
### State-Aware Data Transmission over Ed25519 SSH 

**SecureLink-SSH** is a custom Application-Layer security protocol built in Python 3.13. While standard SSH provides an encrypted pipe, this method adds a second layer of **Active Verification**. Instead of simply sending a file, it breaks data into randomized cryptographic chunks and requires a bi-directional handshake to reconstruct the message.

If the tunnel is intercepted or the handshake is out of sync, the data remains a chaotic string of random ASCII.

---

## The Protocol Logic
This method is "Verify then Reveal," ensuring that the receiver must prove they have the correct data before the sender reveals the plaintext.

1. **The Preamble**: Generates a unique key based on the mathematical lengths of randomized noise.
2. **The Frame**: Wraps the Preamble, Authentication Key, and Payload into a single structural unit for transmission.
3. **The Reverse Query**: The Receiver doesn't just decrypt; it sends individual chunks back to the Sender via the SSH bridge to verify authenticity.
4. **Validation**: The Sender verifies the chunk and the session key, and only then releases the specific character associated with that chunk.

---

## Tech Stack (2026 Standards)
*   **Python 3.13+**
*   **[Paramiko 4.0+](https://www.paramiko.org)**: Utilizing Ed25519 for modern, high-speed elliptic curve handshakes.
*   **[SSHTunnelForwarder](https://pypi.org)**: Handling the encrypted TCP bridge.
*   **Windows OpenSSH Server**: Fully compatible with the native Windows `sshd` service.

---

## Installation & Setup

### 1. Prerequisites
Ensure your local SSH server is active. In PowerShell (Admin):
```powershell
Start-Service sshd
```
2. Dependencies
Install the required libraries:
```
bash
pip install sshtunnel paramiko
```
4. Generate Your Keys
This protocol uses Ed25519 for maximum security. Generate your pair:
bash
ssh-keygen -t ed25519 -f ./key
Use code with caution.

Add the content of key.pub to your ~/.ssh/authorized_keys file.
--- Usage ---
Step 1: Start the Receiver
The receiver sits in a state of "Zero-Trust," waiting for a valid SSH bridge.
```bash
python SecureDecrypt.py
```

Step 2: Start the Sender
Enter your secret message. The sender will generate the Preamble, establish the tunnel, and begin the multi-stage handshake.
```bash
python SecureEncrypt.py
```

### Troubleshooting & 2026 Fixes
This project includes several specific patches for modern Python environments:
Paramiko 4.0 Compatibility: Includes a monkeypatch for the AttributeError: DSSKey caused by the removal of legacy DSA support in late 2025.
Windows SSH Stabilization: Implements mandatory delays to allow the Windows sshd service to allocate local loopback resources before transmission begins.
Socket Management: Built-in checks for WinError 10038 to ensure sockets are managed correctly within nested context managers.

### Disclaimer
This is an experimental cryptographic protocol created for educational purposes in security research. While it utilizes the robust Ed25519 SSH standard, the custom "query-back" logic is intended for learning about stateful protocol design and should be vetted further before use in production-critical environments.

### Author
Elijah Martin
January 2026
Study in high-verification data obfuscation.
"Never trust the pipe. Always verify the data."
{content: }
