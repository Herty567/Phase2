# Phase2
Team members: Jacob Alicea, Josiah Concepcion, Jamie Oliphant, Tim Saari

Name of files: receiver.py, sender.py, and tiger.jpg

The purpose of the receiver file is to listen for incomping packets from the sender file. Will validate packets
checks for correct sequence of numbers to make sure there's no dupiclates. Will validate packets and write 
data to a new file 'received_file.jpg'.

The purpose of the sender file is to read the 'tiger.jpg' in 1024 byte chunks and create packets. Then it will
send the packets to the receiver after sequencing them.

The purpose of the tiger.jpg is a 1.1 MB jpeg file to send through the transfer protocol. Its meant to test if
the protocol works and can show if there was any packet loss or corruption.

To set up this code you would need to copy the sender, receiver, and tiger file to PyCharm. If you want to
simulat an ACK bit error you edit code at the bottom of the sender file and if you want a data packet error 
you can the number at the bottom of the receiver file. Run the receiver first and then run the sender file. 
This should make the receiver ready to receive packets and the sender send the packets and reasssenble the 
file using RDT 2.2 protocol.
