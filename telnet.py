#!/usr/bin/env python3

import pexpect
import sys
import time
import socket
import subprocess
import os

username = "root"
password = "xmhdipc"


def alloc_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    addr = s.getsockname()
    s.close()
    return addr[1]


class Telnet:
    prompt = "[#$] "

    def __init__(self, ipaddr, debug=False, proxy=None, proxy_type=None):
        if proxy and proxy_type == "ssh":
            port = str(alloc_port())
            self.ssh_proxy = subprocess.Popen(
                ["ssh", "-N", "-L", "127.0.0.1:" + port + ":" + ipaddr + ":23", proxy,]
            )
            time.sleep(5)
            ipaddr = "127.0.0.1 " + port
        else:
            self.ssh_proxy = None

        self.conn = pexpect.spawn("telnet " + ipaddr, timeout=10)
        self.debug = debug
        if debug:
            self.conn.logfile = sys.stdout.buffer

    def close(self):
        if self.ssh_proxy:
            self.ssh_proxy.terminate()
            self.ssh_proxy = None

    def login(self):
        self.conn.expect(":")
        self.conn.sendline(username)
        self.conn.expect(":")
        self.conn.sendline(password)
        i = self.conn.expect(["Login incorrect", Telnet.prompt])
        if i == 0:
            if self.debug:
                print("Login incorrect")
            return False
        elif i == 1:
            if self.debug:
                print("Authentication Sucess")
            self.conn.sendline("PS1='# '")
            self.conn.expect(Telnet.prompt)
        return True

    def ls(self):
        self.conn.sendline("ls")
        self.conn.expect(Telnet.prompt)
        print(self.conn.before)

    def upload_uget(self):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "uget.sh")) as f:
            lines = f.readlines()
            for i in lines:
                self.conn.send(i)
                self.conn.expect(Telnet.prompt)

    def file_exists(self, filename):
        self.conn.sendline("test -f " + filename + "; echo $?")
        self.conn.expect("[01]")
        res = self.conn.after
        self.conn.expect(Telnet.prompt)
        return res == b"0"

    def run_command(self, cmdline):
        self.conn.sendline(cmdline)
        self.conn.expect(Telnet.prompt, timeout=60)
        s = self.conn.before.decode("utf-8")
        return s[s.find("\n") + 1 : -1]
