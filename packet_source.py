from packet import Packet

class PacketSource():

	def __init__(self, _packet_size_bytes):
		self.latest_timestamp_ms = 0.0
		self.packet_size_bytes = _packet_size_bytes
		self.latest_id = 0

	def create_packet(self, bitrate_kbps):
		self.latest_id += 1
		self.latest_timestamp_ms += (8 * self.packet_size_bytes) / bitrate_kbps
		return Packet(self.latest_id, self.latest_timestamp_ms)



