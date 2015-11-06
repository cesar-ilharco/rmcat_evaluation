import unittest
import random
import matplotlib.pyplot as plot

from packet import Packet
from link_simulator import LinkSimulator


class TestLinkSimulator(unittest.TestCase):

    def assertBetween(self, x, m, M, precision):
        self.assertTrue(x >= m - precision and x <= M + precision)


    def test_send_single_packet(self):
        packet_sizes = [0.0, 1200.0]  # Empty or non-empty packet
        for payload_size_bytes in packet_sizes:
            for i in range(10):
                capacity_kbps = random.uniform(150.0, 2500.0)
                link_simulator = LinkSimulator(capacity_kbps)
                packet = Packet(1, 0.0, payload_size_bytes)
                link_simulator.send_packet(packet)
                travel_time_ms = link_simulator.ONE_WAY_PATH_DELAY_MS + (8 * payload_size_bytes)/capacity_kbps
                self.assertBetween(packet.arrival_time_ms, travel_time_ms, travel_time_ms + link_simulator.MAX_JITTER_MS, 0.001)

    def test_bottleneck_queue_limit(self):
        for i in range(10):
            capacity_kbps = random.uniform(150.0, 2500.0)
            link_simulator = LinkSimulator(capacity_kbps)
            # Package larger than bottleneck queue limit, should be lost.
            payload_size_bytes = (1.1 * link_simulator.BOTTLENECK_QUEUE_SIZE_MS * capacity_kbps) / 8
            packet = Packet(1, 0.0, payload_size_bytes)
            link_simulator.send_packet(packet)
            self.assertIs(packet.arrival_time_ms, None)


    def test_jitter(self):
        capacity_kbps = 1500.0
        payload_size_bytes = 1200.0
        travel_time_ms = (8 * payload_size_bytes) / capacity_kbps
        # Send packets sparsely to maitain an empty queue.
        packet_gap_ms = 5 * travel_time_ms
        link_simulator = LinkSimulator(capacity_kbps)
        jitter_sample_ms = []
        for i in range(500000):
            send_time_ms = i * packet_gap_ms
            packet = Packet(i, send_time_ms, payload_size_bytes)
            link_simulator.send_packet(packet)
            jitter_ms = packet.arrival_time_ms - send_time_ms - travel_time_ms - link_simulator.ONE_WAY_PATH_DELAY_MS
            self.assertBetween(jitter_ms, 0.0, link_simulator.MAX_JITTER_MS, 0.001)
            jitter_sample_ms.append(jitter_ms)

        plot.hist(jitter_sample_ms, bins=50, normed=1)
        plot.title("Jitter sample")
        plot.xlabel("ms", fontsize=14)
        plot.ylabel("Probability density", fontsize=14)
        plot.show()


if __name__ == '__main__':
    unittest.main()