import random

from packet import Packet

class LinkSimulator(object):

	def __init__(self, capacity_kbps_, jitter_intensity):
		self.ONE_WAY_PATH_DELAY_MS = 50.0
		self.BOTTLENECK_QUEUE_SIZE_MS = 300.0
		self.capacity_kbps = capacity_kbps_
		# Last timestamp independent for Choke and Jitter filters, as on the Chrome repository C++ simulation framework.
		self.__last_choke_time_ms = 0.0
		self.__last_jitter_time_ms = 0.0
		if jitter_intensity == 0:   # No jitter
			self.MAX_JITTER_MS      = 0.0
			self.JITTER_SIGMA_MS    = 0.0
		elif jitter_intensity == 1: # Gentle jitter
			self.MAX_JITTER_MS      = 15.0
			self.JITTER_SIGMA_MS    = 5.0
		else:                       # Default RMCAT jitter
			self.MAX_JITTER_MS      = 30.0
			self.JITTER_SIGMA_MS    = 15.0
		

	def send_packet(self, packet):
		packet.arrival_time_ms = packet.send_time_ms
		self.__add_path_delay(packet)
		self.__add_sending_time(packet)
		# Packet might have been lost.
		if packet.arrival_time_ms is not None:
			self.__add_jitter(packet)


	# Equivalent to bwe_simulation_framework DelayFilter.
	def __add_path_delay(self, packet):
		packet.arrival_time_ms += self.ONE_WAY_PATH_DELAY_MS

	# Equivalent to bwe_simulation_framework ChokeFilter.
	def __add_sending_time(self, packet):
		travel_time_ms = (8 * packet.payload_size_bytes) / self.capacity_kbps
		updated_arrival_time_ms = max(self.__last_choke_time_ms, packet.arrival_time_ms) + travel_time_ms
		if updated_arrival_time_ms - packet.arrival_time_ms < self.BOTTLENECK_QUEUE_SIZE_MS:
			packet.arrival_time_ms = updated_arrival_time_ms
			self.__last_choke_time_ms = updated_arrival_time_ms
		else:  # Packet is lost if queue is overflowed.
			packet.arrival_time_ms = None

	# Equivalent to bwe_simulation_framework JitterFilter.
	def __add_jitter(self, packet):
		# Random from positive truncated gaussian distribution.
		jitter_ms = min(abs(random.gauss(0.0, self.JITTER_SIGMA_MS)), self.MAX_JITTER_MS)
		updated_arrival_time_ms = max(packet.arrival_time_ms + jitter_ms, self.__last_jitter_time_ms)
		packet.arrival_time_ms = updated_arrival_time_ms
		self.__last_jitter_time_ms = updated_arrival_time_ms










