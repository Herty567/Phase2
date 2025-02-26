import socket
import struct
import time
import random
import os

PACKET_SIZE = 1024
SERVER_ADDRESS = ('localhost', 10000)
TIMEOUT = 1.0

def compute_checksum(data: bytes) -> int:
    checksum = 0
    for byte in data:
        checksum = (checksum + byte) % 256
    return checksum

def make_packet(seq_num: int, data: bytes) -> bytes:
    assert seq_num in (0, 1), "Sequence number must be 0 or 1"
    checksum = compute_checksum(data)
    return struct.pack('BB', seq_num, checksum) + data

def parse_ack(ack_packet: bytes) -> int:
    seq_num = struct.unpack('B', ack_packet)[0]
    return seq_num  # No assertion; handle invalid values in sender logic

def sender(file_path: str, error_rate_ack=0.0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)

    seq_num = 0
    total_packets = 0
    file_size = os.path.getsize(file_path)

    print(f"Starting file transfer: {file_path} ({file_size} bytes)")
    start_time = time.time()

    with open(file_path, 'rb') as f:
        while True:
            data = f.read(PACKET_SIZE)
            packet = make_packet(seq_num, data)
            sock.sendto(packet, SERVER_ADDRESS)
            total_packets += 1
            print(f"Sent packet {seq_num} ({len(data)} bytes)")

            if not data:  # EOF
                print("EOF packet sent.")
                break

            while True:
                try:
                    ack_packet, _ = sock.recvfrom(1024)
                    if random.random() < error_rate_ack:
                        print("Simulating ACK corruption...")
                        # Toggle to the opposite valid seq_num (0 -> 1, 1 -> 0)
                        original_ack = parse_ack(ack_packet)
                        corrupted_ack = 1 - original_ack if original_ack in (0, 1) else 0
                        ack_packet = bytes([corrupted_ack])

                    ack_seq_num = parse_ack(ack_packet)
                    if ack_seq_num == seq_num:
                        print(f"ACK {ack_seq_num} received correctly.")
                        seq_num = 1 - seq_num
                        break
                    else:
                        print(f"Unexpected ACK {ack_seq_num}, resending packet {seq_num}...")
                        sock.sendto(packet, SERVER_ADDRESS)
                        total_packets += 1

                except socket.timeout:
                    print(f"Timeout! Resending packet {seq_num}...")
                    sock.sendto(packet, SERVER_ADDRESS)
                    total_packets += 1

    sock.close()
    end_time = time.time()
    print(f"File transfer complete: {total_packets} packets sent.")
    print(f"Total time: {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    sender('tiger.jpg', error_rate_ack=0.0)  # Change to simulate ACK error