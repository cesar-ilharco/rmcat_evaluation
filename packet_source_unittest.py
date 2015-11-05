import unittest
import random

from packet import Packet
from packet_source import PacketSource


class TestPacketSource(unittest.TestCase):

    def assertNear(self, x, y, precision):
        self.assertTrue(abs(x-y) < precision)

    def test_create_packet_constant_bitrate(self):
        packet_size_bytes = 1200.0
        bitrate_kbps = 1500.0
        packet_source = PacketSource(packet_size_bytes)

        for i in range(1, 11):
            packet = packet_source.create_packet(bitrate_kbps)
            self.assertEqual(i, packet.id)
            self.assertNear(i*8*packet_size_bytes/bitrate_kbps, packet.timestamp_ms, 0.01)

    def test_create_packet_variable_bitrate(self):
        packet_size_bytes = 1200.0
        packet_source = PacketSource(packet_size_bytes)

        time_ms = 0.0
        for i in range(1, 11):
            bitrate_kbps = random.randint(150, 2500)
            packet = packet_source.create_packet(bitrate_kbps)
            time_ms += 8*packet_size_bytes/bitrate_kbps
            self.assertEqual(i, packet.id)
            self.assertNear(time_ms, packet.timestamp_ms, 0.01)


if __name__ == '__main__':
    unittest.main()