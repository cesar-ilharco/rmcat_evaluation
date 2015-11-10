from numpy import median

from packet import Packet
from packet_source import PacketSource
from bwe_utils import loss_ratio, receiving_rate_kbps

class NadaFeedback(object):

	def __init__(self, est_queuing_delay_ms_, loss_ratio_, congestion_signal_ms_, derivative_,
				baseline_delay_ms_, delta_ms_, interval_ms_, receiving_rate_kbps_, exp_smoothed_delay_ms_):
		self.est_queuing_delay_ms = est_queuing_delay_ms_
		self.loss_ratio = loss_ratio_
		self.congestion_signal_ms = congestion_signal_ms_
		self.derivative = derivative_
		self.baseline_delay_ms = baseline_delay_ms_
		self.delta_ms = delta_ms_
		self.interval_ms = interval_ms_
		self.receiving_rate_kbps = receiving_rate_kbps_
		self.exp_smoothed_delay_ms = exp_smoothed_delay_ms_

class NadaSender(object):

	PAYLOAD_SIZE_BYTES = 1200.0
	MIN_BITRATE_KBPS = 50.0
	MAX_BITRATE_KBPS = 2500.0
	QUEUING_DELAY_UPPER_BOUND_MS = 10.0
	MAX_CONGESTION_SIGNAL_MS = 40.0  # Used only in modified mode.

	# NADA modified operation mode is an attempt to improve the original one.
	def __init__(self, original_mode_):
		self.bitrate_kbps = 300.0
		self.packet_source = PacketSource(NadaSender.PAYLOAD_SIZE_BYTES)
		self.original_mode = original_mode_
		if not self.original_mode:
			self.min_est_travel_time_ms = float("inf")

	def create_packet(self):
		return self.packet_source.create_packet(self.bitrate_kbps)

	# Use feedback from receiver to update the sender's bitrate.
	def receive_feedback(self, feedback):
		if self.__should_ramp_up(feedback):
			self.__accelerated_ramp_up(feedback)
		elif not self.original_mode and self.__should_ramp_down(feedback):
			self.__accelerated_ramp_down(feedback)
		else:
			self.__gradual_rate_update(feedback)
		# Bitrate should be kept between MIN and MAX.
		self.bitrate_kbps = max(NadaSender.MIN_BITRATE_KBPS, min(NadaSender.MAX_BITRATE_KBPS, self.bitrate_kbps))


	def __should_ramp_up(self, feedback):
		derivative_upper_bound = 10.0 / feedback.interval_ms
		if self.original_mode:
			return feedback.loss_ratio == 0 and feedback.est_queuing_delay_ms < NadaSender.QUEUING_DELAY_UPPER_BOUND_MS \
					and feedback.derivative < derivative_upper_bound
		else: # Stricter accelerated ramp up.
			extra_delay_ms = self.__estimate_extra_delay_ms()
			return feedback.loss_ratio == 0 and (feedback.exp_smoothed_delay_ms < NadaSender.QUEUING_DELAY_UPPER_BOUND_MS / 3.0 \
					or feedback.exp_smoothed_delay_ms - extra_delay_ms < NadaSender.QUEUING_DELAY_UPPER_BOUND_MS / 3.0) \
					and feedback.derivative < derivative_upper_bound and feedback.receiving_rate_kbps > NadaSender.MIN_BITRATE_KBPS

	def __should_ramp_down(self, feedback):
		return max(feedback.congestion_signal_ms , feedback.exp_smoothed_delay_ms) > NadaSender.MAX_CONGESTION_SIGNAL_MS

	def __accelerated_ramp_up(self, feedback):
		MAX_RAMP_UP_QUEUING_DELAY_MS = 50.0   # Referred as T_th.
		GAMMA_0 = 0.5
		gamma = min(GAMMA_0, MAX_RAMP_UP_QUEUING_DELAY_MS/(feedback.baseline_delay_ms + feedback.interval_ms))
		if not self.original_mode:
			gamma = gamma / 2
		self.bitrate_kbps = (1.0 + gamma) * feedback.receiving_rate_kbps

	def __accelerated_ramp_down(self, feedback):
		GAMMA_0 = 0.9;
		gamma = 2.0 * NadaSender.MAX_CONGESTION_SIGNAL_MS / (feedback.congestion_signal_ms + feedback.exp_smoothed_delay_ms);
		gamma = min(gamma**0.5, GAMMA_0);
		self.bitrate_kbps = gamma * feedback.receiving_rate_kbps;

	def __gradual_rate_update(self, feedback):
		TAU_O_MS = 500.0
		ETA = 2.0
		KAPPA = 1.0
		REFERENCE_DELAY_MS = 10.0   # Referred as x_ref.
		PRIORITY_WEIGHT = 1.0       # Referred as w.
		if self.original_mode:
			x_hat = feedback.congestion_signal_ms + ETA * TAU_O_MS * feedback.derivative
			theta = PRIORITY_WEIGHT * (NadaSender.MAX_BITRATE_KBPS - NadaSender.MIN_BITRATE_KBPS) * REFERENCE_DELAY_MS
			increase_kbps = KAPPA * feedback.delta_ms * (theta - x_hat * (self.bitrate_kbps - NadaSender.MIN_BITRATE_KBPS)) / (TAU_O_MS ** 2)
			self.bitrate_kbps += increase_kbps
		else: # Smoother rate update.
			extra_delay_ms = self.__estimate_extra_delay_ms()
			new_congestion_signal_ms = max(0.0, feedback.congestion_signal_ms - extra_delay_ms)
			x_hat = new_congestion_signal_ms + ETA * TAU_O_MS * feedback.derivative
			theta = PRIORITY_WEIGHT * (NadaSender.MAX_BITRATE_KBPS - NadaSender.MIN_BITRATE_KBPS) * REFERENCE_DELAY_MS
			increase_kbps = KAPPA * feedback.delta_ms * (theta - x_hat * (self.bitrate_kbps - NadaSender.MIN_BITRATE_KBPS)) / (TAU_O_MS ** 2)
			bitrate_reference = 3.0*(self.bitrate_kbps- NadaSender.MIN_BITRATE_KBPS)/(NadaSender.MAX_BITRATE_KBPS - NadaSender.MIN_BITRATE_KBPS)
			smoothing_factor = min(bitrate_reference ** 2.0, 1.0)
			self.bitrate_kbps += increase_kbps * smoothing_factor

	def __estimate_extra_delay_ms(self):
		est_travel_time_ms = 8.0 * NadaSender.PAYLOAD_SIZE_BYTES / self.bitrate_kbps
		self.min_est_travel_time_ms = min(self.min_est_travel_time_ms, est_travel_time_ms)
		return est_travel_time_ms - self.min_est_travel_time_ms

class NadaReceiver(object):

	FEEDBACK_INTERVAL_MS = 100.0
	LOSS_RATIO_TIME_WINDOW_MS = 500.0
	RECEIVING_RATE_TIME_WINDOW_MS = 500.0
	LOSS_PENALTY_MS = 1000.0

	def __init__(self, use_median_filter_):
		self.latest_feedback_ms = 0.0
		self.baseline_delay_ms = float("inf")
		self.packets = []
		# Values are stored to be plotted in the end of a simulation.
		self.time_ms = []
		self.delay_signals_ms = []
		self.median_filtered_delays_ms = []
		self.exp_smoothed_delays_ms = []
		self.est_queuing_delays_ms = []
		self.congestion_signals_ms = []
		self.loss_ratios = []
		self.receiving_rates_kbps = []
		self.use_median_filter = use_median_filter_

	def receive_packet(self, packet):
		self.time_ms.append(packet.arrival_time_ms)
		self.packets.append(packet)
		# Use delay as a signal.
		# 1) Subtract Baseline.
		# 2) Apply Median filter.
		# 3) Apply Exponential Smoothing Filter.
		# 4) Non-linear Estimate queuing delay warping.
		delay_ms = packet.arrival_time_ms - packet.send_time_ms
		self.baseline_delay_ms = min(self.baseline_delay_ms, delay_ms)
		self.delay_signals_ms.append(delay_ms - self.baseline_delay_ms)
		self.median_filtered_delays_ms.append(self.__median_filter())
		self.exp_smoothed_delays_ms.append(self.__exp_smoothing_filter())
		self.est_queuing_delays_ms.append(self.__non_linear_warping())
		self.loss_ratios.append(loss_ratio(self.packets, NadaReceiver.LOSS_RATIO_TIME_WINDOW_MS))
		self.receiving_rates_kbps.append(receiving_rate_kbps(self.packets, NadaReceiver.RECEIVING_RATE_TIME_WINDOW_MS))
		self.congestion_signals_ms.append(self.est_queuing_delays_ms[-1] + NadaReceiver.LOSS_PENALTY_MS * self.loss_ratios[-1])


	def get_feedback(self):
		now_ms = self.time_ms[-1]
		if now_ms - self.latest_feedback_ms < NadaReceiver.FEEDBACK_INTERVAL_MS:
			return None

		delta_ms = now_ms - self.latest_feedback_ms
		self.latest_feedback_ms = now_ms
		derivative = 0.0
		if len(self.congestion_signals_ms) > 1:
			derivative = (self.congestion_signals_ms[-1] - self.congestion_signals_ms[-2]) / delta_ms

		return NadaFeedback(self.est_queuing_delays_ms[-1], self.loss_ratios[-1], self.congestion_signals_ms[-1], derivative,
							self.baseline_delay_ms, delta_ms, NadaReceiver.FEEDBACK_INTERVAL_MS, self.receiving_rates_kbps[-1],
							self.exp_smoothed_delays_ms[-1])

	def __median_filter(self):
		if self.use_median_filter:
			K_MEDIAN = 5   # Filter latest 5 elements
			elements = self.delay_signals_ms[-K_MEDIAN:]
			return median(elements)
		else: # Use min element
			K_MIN = 5
			elements = self.delay_signals_ms[-K_MIN:]
			return min(elements)

	def __exp_smoothing_filter(self):
		ALPHA = 0.9
		if len(self.exp_smoothed_delays_ms) == 0:
			return self.median_filtered_delays_ms[-1]
		return ALPHA * self.exp_smoothed_delays_ms[-1] + (1.0-ALPHA) * self.median_filtered_delays_ms[-1]

	def __non_linear_warping(self):
		MIN_DELAY_MS = 50.0    # Referred as d_th.
		MAX_DELAY_MS = 400.0   # Referred as d_max.
		exp_smoothed_delay_ms = self.exp_smoothed_delays_ms[-1]
		if exp_smoothed_delay_ms <= MIN_DELAY_MS:
			return exp_smoothed_delay_ms
		elif exp_smoothed_delay_ms < MAX_DELAY_MS:
			return MIN_DELAY_MS * ((MAX_DELAY_MS - exp_smoothed_delay_ms)/(MAX_DELAY_MS - MIN_DELAY_MS)) ** 4
		else:
			return 0.0

