import matplotlib.pyplot as plt
from link_simulator import LinkSimulator

def __plot(receiver, times_ms, capacities_kbps):
	def ms_to_s(t):
		return t/1000

	plt.subplot(311)
	plt.plot(map(ms_to_s, receiver.time_ms), receiver.receiving_rates_kbps, label='receiving rate')
	plt.plot(map(ms_to_s, [0.0]+times_ms), capacities_kbps[0:1]+capacities_kbps, label='link capacity', drawstyle='steps')
	plt.ylabel('bitrate (kbps)', fontsize=16)

	plt.subplot(312)
	plt.plot(map(ms_to_s, receiver.time_ms), receiver.delay_signals_ms, label='delay signals')
	plt.ylabel('delay (ms)', fontsize=16)

	plt.subplot(313)
	plt.plot(map(ms_to_s, receiver.time_ms), map(lambda x: 100.0*x, receiver.loss_ratios), label='loss ratio')
	plt.ylabel('packet loss %', fontsize=16)
	plt.xlabel('time (s)', fontsize=16)
	plt.show()


def __test_single_flow(sender, receiver, times_ms, capacities_kbps):

	link_simulator = LinkSimulator(None)
	now_ms = 0.0

	for i in range(len(capacities_kbps)):
		link_simulator.capacity_kbps = capacities_kbps[i]
		end_time_ms = times_ms[i]
		while now_ms < end_time_ms:
			packet = sender.create_packet()
			link_simulator.send_packet(packet)
			if packet.arrival_time_ms is not None:
				receiver.receive_packet(packet)
			feedback = receiver.get_feedback()
			if feedback is not None:
				sender.receive_feedback(feedback)
			now_ms = packet.send_time_ms

	__plot(receiver, times_ms, capacities_kbps)


def rmcat_evaluation_1(sender, receiver):
	capacities_kbps = [1000.0, 2500.0, 600.0, 1000.0]
	times_ms = map(lambda x:1000.0*x, [40, 60, 80, 99])
	__test_single_flow(sender, receiver, times_ms, capacities_kbps)


def test_constant_capacity(sender, receiver, duration_s, capacity_kbps):
	__test_single_flow(sender, receiver, [duration_s * 1000.0], [capacity_kbps])
