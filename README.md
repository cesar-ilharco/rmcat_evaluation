# rmcat_evaluation
RMCAT Simulation Framework in Python

RTP Media Congestion Avoidance Techniques (RMCAT) is part of IETF.
https://datatracker.ietf.org/wg/rmcat/documents/

A RMCAT simulation framework is implemented in C++ in the Chromium WebRTC repository. https://chromium.googlesource.com/?format=HTML

------------------------------------------------------------------------------------------------------
OBJECTIVES:  This repository provides a python RMCAT simulation framework that is easy to read, modify and run. With this framework you can test a congestion control algorithm without building the Chromium repository. While this repository is by no means intended to replace the Chromium WebRTC simulation framework, it can facilitate testing for new congestion control algorithms and modifications of the existing ones.

------------------------------------------------------------------------------------------------------
ABOUT: This framework simulates: 
A Packet Creator that creates packets, with a pace determined by the sending bitrate and the packet size. 
A Link Simulator: The arrival time for a packet is computed based on its send time, its payload size, the one way path delay (minimum end-to-end trip time), the link capacity and a randomized jitter, modeled as a truncated right sided Gaussian distribution. Moreover, a limited bottleneck queuing size will trigger packet loss whenever the queuing time goes above the limit.

Network-Assisted Dynamic Adaptation (NADA) is a congestion control algorithm for real-time media applications. It is implemented in this repository according to: https://tools.ietf.org/html/draft-zhu-rmcat-nada-06 (Work in progress)

A modified operation mode is implemented as an attempt to improve its performance.

NADA was also implemented in the Chromium WebRTC simulation framework:
https://chromium.googlesource.com/external/webrtc/+/master/webrtc/modules/remote_bitrate_estimator/test/estimators/nada.h

------------------------------------------------------------------------------------------------------
HOW TO USE:
Calling main.py will execute the RMCAT Evaluation test 5.1, available on:
https://tools.ietf.org/html/draft-ietf-rmcat-eval-test-02#section-5.1

The following optional parameters are accepted:
--modified_sender / -ms    for modified sender operation mode.
--modified_filter / -mf    to use min filter on NADA receiver.
--jitter_intensity / -j v  with v in {0, 1, 2}

Compatible with python 2.7 and 3.5

e.g. python3 main.py -ms -mf -j 1
