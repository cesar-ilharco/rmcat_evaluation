
from nada import NadaSender, NadaReceiver
from evaluation_tests import rmcat_evaluation_1, test_constant_capacity


if __name__ == '__main__':
    nada_sender = NadaSender()
    nada_receiver = NadaReceiver()
    # test_constant_capacity(nada_sender, nada_receiver)
    rmcat_evaluation_1(nada_sender, nada_receiver)
