#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2012-2015 clowwindy
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import absolute_import, division, print_function, \
    with_statement

import sys
import os
import logging
import signal

#print(sys.path) #['/home/red/GITREPO-MARCON/shadowsocks/shadowsocks', '/home/red/GITREPO-MARCON/shadowsocks', '/usr/lib64/python34.zip', '/usr/lib64/python3.4', '/usr/lib64/python3.4/plat-linux', '/usr/lib64/python3.4/lib-dynload', '/home/red/shadowsocks/lib64/python3.4/site-packages', '/home/red/shadowsocks/lib64/python3.4/site-packages/setuptools-39.1.0-py3.4.egg', '/home/red/shadowsocks/lib64/python3.4/site-packages/pip-10.0.1-py3.4.egg', '/home/red/shadowsocks/lib/python3.4/site-packages', '/home/red/shadowsocks/lib/python3.4/site-packages/setuptools-39.1.0-py3.4.egg', '/home/red/shadowsocks/lib/python3.4/site-packages/pip-10.0.1-py3.4.egg']
#print(os.path.dirname(__file__))    #/home/red/GITREPO-MARCON/shadowsocks/shadowsocks
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from shadowsocks import shell, daemon, eventloop, tcprelay, udprelay, asyncdns


@shell.exception_handle(self_=False, exit_code=1)
def main():
    #print(sys.version_info)
    shell.check_python()

    # fix py2exe
    #The hasattr() method returns true if an object has the given named attribute and false if it does not.
    if hasattr(sys, "frozen") and sys.frozen in \
            ("windows_exe", "console_exe"):
        p = os.path.dirname(os.path.abspath(sys.executable))    #/home/red/shadowsocks/bin
        os.chdir(p)

    config = shell.get_config(True)
    daemon.daemon_exec(config)

    logging.info("starting local at %s:%d" %
                 (config['local_address'], config['local_port']))

    dns_resolver = asyncdns.DNSResolver()
    tcp_server = tcprelay.TCPRelay(config, dns_resolver, True)
    udp_server = udprelay.UDPRelay(config, dns_resolver, True)
    loop = eventloop.EventLoop()
    dns_resolver.add_to_loop(loop)
    tcp_server.add_to_loop(loop)
    udp_server.add_to_loop(loop)

    def handler(signum, _):
        logging.warn('received SIGQUIT, doing graceful shutting down..')
        tcp_server.close(next_tick=True)
        udp_server.close(next_tick=True)
    signal.signal(getattr(signal, 'SIGQUIT', signal.SIGTERM), handler)

    def int_handler(signum, _):
        sys.exit(1)
    signal.signal(signal.SIGINT, int_handler)

    daemon.set_user(config.get('user', None))
    loop.run()

if __name__ == '__main__':
    #main()
    pass
