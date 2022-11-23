import os
import shutil
from typing import Union

import zmq.auth


def generate_certificates(base_dir: Union[str, os.PathLike]) -> None:
    '''Generate client and server CURVE certificate files'''
    keys_dir = os.path.join(base_dir, os.path.normpath('app/data/server'))
    if not os.path.exists(keys_dir):
        os.makedirs(keys_dir)
    # create new keys in certificates dir
    server_public_file, server_secret_file = zmq.auth.create_certificates(
        keys_dir, "server"
    )


if __name__ == '__main__':
    if zmq.zmq_version_info() < (4, 0):
        raise RuntimeError(
            "Security is not supported in libzmq version < 4.0. libzmq version {}".format(
                zmq.zmq_version()
            )
        )

    generate_certificates(os.path.dirname(__file__))