#!/usr/bin/env python
# tests.py
#
# paster default

"""Paster default tests"""

__docformat__ = "restructuredtext"

# http://docs.python.org/library/unittest.html
import unittest

# https://docs.pylonsproject.org/projects/pyramid/1.0/api/testing.html
from pyramid import testing

# Note: do more with this
class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_my_view(self):
        from ccpweb.views import my_view
        request = testing.DummyRequest()
        info = my_view(request)
        self.assertEqual(info['project'], 'ccpweb')
