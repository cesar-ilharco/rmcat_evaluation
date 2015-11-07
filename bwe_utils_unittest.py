import unittest
import random

from packet import Packet
from bwe_utils import loss_ratio, global_loss_ratio


class TestBweUtils(unittest.TestCase):

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


if __name__ == '__main__':
    unittest.main()