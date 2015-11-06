class Packet(object):

	def __init__(self, id_, send_time_ms_, payload_size_bytes_):
		self.id = id_
		self.send_time_ms = send_time_ms_
		self.arrival_time_ms = None
		self.payload_size_bytes = payload_size_bytes_
