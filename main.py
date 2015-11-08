import matplotlib.pyplot as plt

from nada import NadaSender, NadaReceiver
from link_simulator import LinkSimulator


def test_constant_capacity(sender, receiver):
	CAPACITY_KBPS = 1500.0
	RUNNING_TIME_MS = 10 * 1000.0
	link_simulator = LinkSimulator(CAPACITY_KBPS)

	now_ms = 0.0
	while now_ms < RUNNING_TIME_MS:
		packet = sender.create_packet()
		link_simulator.send_packet(packet)
		if packet.arrival_time_ms is not None:
			receiver.receive_packet(packet)
		feedback = receiver.get_feedback()
		if feedback is not None:
			sender.receive_feedback(feedback)
		now_ms = packet.send_time_ms

	plt.figure(1)
	plt.subplot(211)
	plt.plot(receiver.time_ms, [CAPACITY_KBPS] * len(receiver.time_ms), label="link capacity")
	plt.plot(receiver.time_ms, receiver.receiving_rates_kbps, label="receiving rate")
	plt.show()


if __name__ == '__main__':
    nada_sender = NadaSender()
    nada_receiver = NadaReceiver()
    test_constant_capacity(nada_sender, nada_receiver)
