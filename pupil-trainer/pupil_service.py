import zmq
import msgpack
import time
ctx = zmq.Context()

# create a zmq REQ socket to talk to Pupil Service/Capture
req = ctx.socket(zmq.REQ)
req.connect('tcp://localhost:50020')

# convenience functions


def send_recv_notification(n):
    # REQ REP requirese lock step communication with multipart msg (topic,msgpack_encoded dict)
    req.send_multipart(('notify.%s' % n['subject'], msgpack.dumps(n)))
    return req.recv()


def get_pupil_timestamp():
    req.send('t')  # see Pupil Remote Plugin for details
    return float(req.recv())


# set start eye windows
print(send_recv_notification(
    {'subject': 'eye_process.should_start.0', 'eye_id': 0, 'args': {}}))
# n = {'subject': 'eye_process.should_start.1', 'eye_id': 1, 'args': {}}
# print(send_recv_notification(n))
time.sleep(2)


# set calibration method to hmd calibration
# n = {'subject': 'start_plugin', 'name': 'Screen_Marker_Calibration', 'args': {}}
# print(send_recv_notification(n))


time.sleep(2)
print(send_recv_notification({'subject': 'service_process.should_stop'}))
