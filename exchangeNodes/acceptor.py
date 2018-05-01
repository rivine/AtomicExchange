
from concurrent import futures
import time

import grpc

import atomicswap_pb2
import atomicswap_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class AtomicSwap(atomicswap_pb2_grpc.AtomicSwapServicer):

    def AcceptInitiate(self, request, context):
        return atomicswap_pb2.AcceptorSmartContractCreated(hash='2427128964')


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    atomicswap_pb2_grpc.add_AtomicSwapServicer_to_server(AtomicSwap(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
