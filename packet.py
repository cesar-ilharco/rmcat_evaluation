class Packet(object):

	def __init__(self, _id, _send_time_ms, _payload_size_bytes):
		self.id = _id
		self.send_time_ms = _send_time_ms
		self.arrival_time_ms = None
		self.payload_size_bytes = _payload_size_bytes
