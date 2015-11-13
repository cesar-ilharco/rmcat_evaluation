# rmcat_evaluation
RMCAT Simulation Framework in Python

RTP Media Congestion Avoidance Techniques (rmcat) is part of IETF.
https://datatracker.ietf.org/wg/rmcat/documents/

A RMCAT simulation framework is implemented in C++ in the Chromium WebRTC repository. https://chromium.googlesource.com/?format=HTML

OBJECTIVES:  This repository provides a Python simulation framework that is easy to read and modify, without needing to build the whole Chromium repository.

ABOUT: This framework simulates: A sender that creates packets, with a pace determined by the sending bitrate and the packet size. Packets are submitted to: Delay filter: adds latency - minimum one way path delay. Choke filter: adds travel time. Packet can be lost if delay > bottleneck queuing size. Jitter filter: adds noise to the arrival time. (Those filters simulate effect of the packet traveling through the channel link). A receiver then gets the packets with updated timestamps.

NADA congestion control algorithm is implemented, according to: https://tools.ietf.org/html/draft-ietf-rmcat-nada-00 (Work in progress)

The modifications to NADA algorithm that were implemented on: https://chromium.googlesource.com/external/webrtc/+/master/webrtc/modules/remote_bitrate_estimator/test/estimators/nada.cc were also implemented in this repository.
