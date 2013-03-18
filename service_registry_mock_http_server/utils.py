# Copyright 2012 Rackspace Hosting, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import subprocess
import time
import socket
import atexit
from os.path import join as pjoin


# From https://github.com/Kami/python-yubico-client/blob/master/tests/utils.py

def waitForStartUp(process, address, timeout=10):
    # connect to it, with a timeout in case something went wrong
    start = time.time()
    while time.time() < start + timeout:
        try:
            s = socket.create_connection(address)
            s.close()
            break
        except:
            time.sleep(0.1)
    else:
        # see if process is still alive
        process.poll()

        if process and process.returncode is None:
            process.terminate()
        raise RuntimeError("Couldn't connect to server; aborting test")


class ProcessRunner(object):
    def setUp(self, *args, **kwargs):
        pass

    def tearDown(self, *args, **kwargs):
        if self.process:
            self.process.terminate()


class MockAPIServerRunner(ProcessRunner):
    def __init__(self, port=8881):
        self.port = port

    def setUp(self, *args, **kwargs):
        self.cwd = os.getcwd()
        self.process = None
        self.base_dir = pjoin(self.cwd)
        self.pid_fname = pjoin(self.cwd, 'mock_api_server.pid')
        self.log_path = pjoin(self.cwd, 'mock_api_server.log')

        super(MockAPIServerRunner, self).setUp(*args, **kwargs)
        script = pjoin(os.path.dirname(__file__), 'mock_http_server.py')
        fixtures_dir = pjoin(os.path.dirname(__file__), '../fixtures/response')

        with open(self.log_path, 'a+') as log_fp:
            port_arg = '%s --port=%s' % (script, self.port)
            args = [script, port_arg, fixtures_dir]
            print ' '.join(args)
            self.process = subprocess.Popen(args,
                                            shell=False,
                                            cwd=self.base_dir,
                                            stdout=log_fp,
                                            stderr=log_fp)
            waitForStartUp(self.process,
                           ('127.0.0.1', self.port), 10)
        atexit.register(self.tearDown)
