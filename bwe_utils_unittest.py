import unittest
import random

from packet import Packet
from packet_source import PacketSource
from bwe_utils import loss_ratio, global_loss_ratio, receiving_rate_kbps


class TestBweUtils(unittest.TestCase):

	def assertNear(self, x, y, precision):
		self.assertTrue(abs(x-y) < precision)

	def test_loss_ratio_no_packets(self):
		self.assertEqual(loss_ratio(None, 0.0), 0.0)
		self.assertEqual(loss_ratio(None, 50.0), 0.0)
		self.assertEqual(loss_ratio([], 0.0), 0.0)
		self.assertEqual(loss_ratio([], 50.0), 0.0)

	def test_loss_ratio_single_packet(self):
		# Only id and arrival time matter here
		packet = Packet(1, None, None)
		packet.arrival_time_ms = 10.0
		self.assertEqual(loss_ratio([packet], 0.0), 0.0)
		self.assertEqual(loss_ratio([packet], 50.0), 0.0)

	def test_loss_ratio_gap_packets(self):
		packets = []
		for i in range(10):
			# Only id and arrival time matter here
			packet = Packet(i, None, None)
			packet.arrival_time_ms = 10.0 * i
			packets.append(packet)

		for i in range(20, 30):
			# Only id and arrival time matter here
			packet = Packet(i, None, None)
			packet.arrival_time_ms = 10.0 * i 
			packets.append(packet)

		# Short time windows won't trigger loss computation.
		for t in range(0, 200, 10):
			self.assertEqual(loss_ratio(packets, t), 0.0)

		for i in range(10):
			time_window_ms = 200 + 10*i
			loss = 1.0 - float(11 + i)/(21 + i)
			self.assertEqual(loss_ratio(packets, time_window_ms), loss)

	def test_global_loss_ratio_no_packets(self):
		self.assertEqual(global_loss_ratio(None), 0.0)

	def test_global_loss_ratio_contiguous_packets(self):
		for i in range(10):
			first_id = random.randint(0,100)
			number_packets = random.randint(0,1000)
			packets = [Packet(first_id+i, None, None) for i in range(number_packets)]
			self.assertEqual(global_loss_ratio(packets), 0.0)

	def test_global_loss_ratio_shuffled_packets(self):
		for i in range(10):
			first_id = random.randint(0,100)
			number_packets = random.randint(0,1000)
			packets = [Packet(first_id+i, None, None) for i in range(number_packets)]
			random.shuffle(packets)
			self.assertEqual(global_loss_ratio(packets), 0.0)

	def test_global_loss_ratio_sparsed_packets(self):
		p1 = Packet(1, None, None)
		p2 = Packet(1000, None, None)
		self.assertEqual(global_loss_ratio([p1, p2]), 1.0 - float(2)/1000)

	def test_receiving_rate_kbps_no_packets(self):
		self.assertEqual(receiving_rate_kbps(None, 0.0), 0.0)
		self.assertEqual(receiving_rate_kbps(None, 100.0), 0.0)
		self.assertEqual(receiving_rate_kbps([], 0.0), 0.0)
		self.assertEqual(receiving_rate_kbps([], 100.0), 0.0)

	def test_receiving_rate_kbps_single_packet(self):
		payload_sizes_bytes = [0.0, 500.0, 1200.0] # Empty or non-empty packet.
		for payload_size_bytes in payload_sizes_bytes:
			# id and send_time don't matter here.
			packet = Packet(None, None, payload_size_bytes)
			for i in range(10):
				packet.arrival_time_ms = i
				time_window_ms = random.uniform(100.0, 1000.0)
				self.assertEqual(receiving_rate_kbps([packet], time_window_ms),
					             8.0 * packet.payload_size_bytes / time_window_ms)

	def test_receiving_rate_regular_packets(self):
		for i in range(10):
			bitrate_kbps = random.uniform(150.0, 2500.0)
			packet_size_bytes = random.uniform(1.0, 8000.0)
			delay_ms = random.uniform(10.0, 300.0)
			packet_source = PacketSource(packet_size_bytes)
			packets = []
			for j in range(1000):
				packet = packet_source.create_packet(bitrate_kbps)
				packet.arrival_time_ms = packet.send_time_ms + delay_ms
				packets.append(packet)
			time_window_ms = random.uniform(0.0, 1.0) * packets[-1].arrival_time_ms
			self.assertNear(receiving_rate_kbps(packets, time_window_ms), bitrate_kbps, 0.001)

if __name__ == '__main__':
    unittest.main()
