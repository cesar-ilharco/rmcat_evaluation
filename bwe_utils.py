"""
Those methods can potentially be used by other congestion control algorithms.
Hence they are put separately here in this file.
"""

def loss_ratio(packets, time_window_ms):
    """
    Receives as an argument an array of packets, sorted by arrival_time, increasingly.
    Computes the loss ratio in the previous time_window_ms.
    """
    if packets is None or len(packets) == 0:
        return 0.0
    num_packets = len(packets)
    time_limit_ms = packets[-1].arrival_time_ms - time_window_ms
    packets_received = 0
    newest_id = 0
    oldest_id = float("inf")
    for i in range(num_packets-1, -1, -1):
        if packets[i].arrival_time_ms < time_limit_ms:
            break
        packets_received += 1
        oldest_id = min(oldest_id, packets[i].id)
        newest_id = max(newest_id, packets[i].id)

    return 1.0 - float(packets_received)/(newest_id - oldest_id + 1)

def global_loss_ratio(packets):
    if packets is None or len(packets) == 0:
        return 0.0
    packets_received = len(packets)
    newest_id = max([p.id for p in packets])
    oldest_id = min([p.id for p in packets])
    return 1.0 - float(packets_received)/(newest_id - oldest_id + 1)

def receiving_rate_kbps(packets, time_window_ms):
    """
    Receives as an argument an array of packets, sorted by arrival_time, increasingly.
    Computes the receiving rate, in kbps, in the previous time_window_ms.
    """
    if packets is None or len(packets) == 0:
        return 0.0
    newest_packet_ms = packets[-1].arrival_time_ms
    time_limit_ms = newest_packet_ms - time_window_ms
    bytes_counter = 0.0
    packets_counter = 0

    # Count until the first packet out of the time limit.
    for i in range(1, len(packets)+1):
        oldest_packet_ms = packets[-i].arrival_time_ms
        bytes_counter += packets[-i].payload_size_bytes
        packets_counter += 1
        if oldest_packet_ms < time_limit_ms:
            break

    if packets_counter == 1:
        return (8.0 * bytes_counter) / time_window_ms

    return ((packets_counter - 1) * 8.0 * bytes_counter) \
           /(packets_counter * (newest_packet_ms - oldest_packet_ms))

def average_bitrate_kbps(packets):
    """
    Computes the average bitrate throughout the whole simulation.
    """
    if packets is None or len(packets) == 0:
        return 0.0

    if len(packets) == 1:
        return 8.0 * packets[0].payload_size_bytes / packets[0].arrival_time_ms

    total_received_bits = 8.0 * sum([packet.payload_size_bytes for packet in packets])
    time_span_ms = packets[-1].arrival_time_ms - packets[0].arrival_time_ms

    # If n packets were received, we are counting only n-1 time gaps between them.
    correction_factor = float(len(packets) - 1)/len(packets)

    return (total_received_bits / time_span_ms) * correction_factor

def average_delay_ms(packets):
    """
    Computes the average delay throughout the whole simulation.
    """
    if packets is None or len(packets) == 0:
        return 0.0

    sum_delays_ms = sum([packet.arrival_time_ms - packet.send_time_ms for packet in packets])
    return sum_delays_ms / len(packets)
