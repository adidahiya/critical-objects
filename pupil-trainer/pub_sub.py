import zmq
import msgpack
from zmq_tools import Msg_Receiver, Msg_Dispatcher, Msg_Requester

host = '127.0.0.1'
port = 63623
# port = 50020
# host = '198.105.254.228'
remote_url = 'tcp://%s:%s' % (host, port)

# context shared across all sockets
ctx = zmq.Context()


def get_pub_sub_urls(requester=ctx.socket(zmq.REQ)):
    requester.connect(remote_url)
    requester.send_string('PUB_PORT')
    pub_port = requester.recv_string()
    pub_url = 'tcp://%s:%s' % (host, pub_port)

    requester.send_string('SUB_PORT')
    sub_port = requester.recv_string()
    sub_url = 'tcp://%s:%s' % (host, sub_port)

    return (pub_url, sub_url)


if __name__ == "__main__":
    requester = Msg_Requester(ctx, remote_url)
    (pub_url, sub_url) = get_pub_sub_urls(requester.socket)
    dispatcher = Msg_Dispatcher(ctx, pub_url)
    receiver = Msg_Receiver(ctx, sub_url, topics=(
        'notify.', 'logging.', 'gaze.'))

    requester.request({'subject': 'meta.should_doc'})

    while True:
        topic, payload = receiver.recv()
        if topic == 'notify.meta.doc':
            continue
            actor = payload.get('actor')
            doc = payload.get('doc')
            print('%s: %s' % (actor, doc))
        elif topic.startswith('gaze'):
            print(payload)
        else:
            print(payload)
