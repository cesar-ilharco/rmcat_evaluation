
from nada import NadaSender, NadaReceiver
from evaluation_tests import rmcat_evaluation_1, test_constant_capacity


if __name__ == '__main__':
	original_mode = False
	nada_sender = NadaSender(original_mode)
	nada_receiver = NadaReceiver(original_mode)
	# test_constant_capacity(nada_sender, nada_receiver, 10.0, 1000.0)
	rmcat_evaluation_1(nada_sender, nada_receiver)
