from packet import Packet

"""
Packets are not initialized directly in the Simulation Framework.
They will be created by the PacketSource class.
"""

class PacketSource(object):

    def __init__(self, packet_size_bytes):
        self.PACKET_SIZE_BYTES = packet_size_bytes
        self.__latest_id = 0
        self.__latest_timestamp_ms = 0.0

    def create_packet(self, bitrate_kbps):
        self.__latest_id += 1
        self.__latest_timestamp_ms += (8 * self.PACKET_SIZE_BYTES) / bitrate_kbps
        return Packet(self.__latest_id, self.__latest_timestamp_ms, self.PACKET_SIZE_BYTES)
