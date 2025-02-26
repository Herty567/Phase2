import socket
import struct
import random

PACKET_SIZE = 1024
SERVER_ADDRESS = ('localhost', 10000)

def compute_checksum(data: bytes) -> int:
    checksum = 0
    for byte in data:
        checksum = (checksum + byte) % 256
    return checksum

def make_ack(seq_num: int) -> bytes:
    assert seq_num in (0, 1), "ACK must be 0 or 1"
    return struct.pack('B', seq_num)

def parse_packet(packet: bytes):
    seq_num, checksum = struct.unpack('BB', packet[:2])
    data = packet[2:]
    assert seq_num in (0, 1), "Sequence number must be 0 or 1"
    return seq_num, checksum, data

def is_corrupt(packet: bytes) -> bool:
    seq_num, checksum, data = parse_packet(packet)
    return checksum != compute_checksum(data)

def receiver(save_path: str, error_rate_data=0.0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SERVER_ADDRESS)
    print(f"Receiver is running on {SERVER_ADDRESS}...")

    expected_seq = 0
    with open(save_path, 'wb') as f:
        while True:
            packet, addr = sock.recvfrom(PACKET_SIZE + 2)

            if random.random() < error_rate_data:
                print("Simulating data corruption...")
                packet = packet[:2] + bytes([packet[2] ^ 0xFF]) + packet[3:]

            if not is_corrupt(packet):
                seq_num, _, data = parse_packet(packet)

                if len(data) == 0 and seq_num == expected_seq:  # EOF
                    print("EOF received. File transfer complete.")
                    sock.sendto(make_ack(seq_num), addr)
                    break

                if seq_num == expected_seq:
                    print(f"Received packet {seq_num} ({len(data)} bytes), writing data...")
                    f.write(data)
                    expected_seq = 1 - expected_seq
                    sock.sendto(make_ack(seq_num), addr)
                    print(f"ACK for packet {seq_num} sent.")
                else:
                    print(f"Out-of-order packet {seq_num}, sending ACK for {1 - expected_seq}...")
                    sock.sendto(make_ack(1 - expected_seq), addr)
            else:
                print(f"Corrupted packet detected, sending ACK for {1 - expected_seq}...")
                sock.sendto(make_ack(1 - expected_seq), addr)

    sock.close()
    print("Receiver socket closed successfully.")

if __name__ == "__main__":
    receiver('received_tiger.jpg', error_rate_data=0.0)  # Change to simulate data Errors