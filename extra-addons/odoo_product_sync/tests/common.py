# -*- coding: utf-8 -*-

"""
Helpers usable in the tests
"""

import xmlrpc
import logging

import mock
import odoo

from os.path import dirname, join
from contextlib import contextmanager
from odoo import models
from odoo.addons.component.tests.common import SavepointComponentCase


class MockResponseImage(object):

    def __init__(self, resp_data, code=200, msg='OK'):
        self.resp_data = resp_data
        self.code = code
        self.msg = msg
        self.headers = {'content-type': 'image/jpeg'}

    def read(self):
        return self.resp_data

    def getcode(self):
        return self.code


@contextmanager
def mock_urlopen_image():
    with mock.patch('urllib2.urlopen') as urlopen:
        urlopen.return_value = MockResponseImage('')
        yield
