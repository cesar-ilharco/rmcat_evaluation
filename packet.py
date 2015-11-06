class Packet(object):

	def __init__(self, _id, _send_time_ms):
		self.id = _id
		self.send_time_ms = _send_time_ms
		self.arrival_time_ms = None
