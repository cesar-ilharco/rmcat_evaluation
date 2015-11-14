import argparse

from nada import NadaSender, NadaReceiver
from evaluation_tests import rmcat_evaluation_1, test_constant_capacity


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-ms", "--modified_sender", action="store_true",
                        help="Use argument for modified NADA sender mode")
    parser.add_argument("-mf", "--modified_filter", action="store_true",
                        help="Use argument to use min filter instead of median filter on NADA receiver")
    parser.add_argument("-j", "--jitter", type=int, choices=[0, 1, 2],
                        help="Jitter Intensity: 0=no jitter; 1=gentle jitter; 2=high jitter")
    args = parser.parse_args()
    original_mode = not args.modified_sender
    use_median_filter = not args.modified_filter
    jitter_intensity = args.jitter or 1
    return [original_mode, use_median_filter, jitter_intensity]

if __name__ == '__main__':
    [original_mode, use_median_filter, jitter_intensity] = parse_args()
    nada_sender = NadaSender(original_mode)
    nada_receiver = NadaReceiver(use_median_filter)
    # test_constant_capacity(nada_sender, nada_receiver, 10.0, 1000.0)
    rmcat_evaluation_1(nada_sender, nada_receiver, jitter_intensity)
