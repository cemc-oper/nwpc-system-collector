import unittest
from unittest import mock
import os

from nwpc_hpc_collector import disk_usage


class TestGetUserName(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_user_name(self):
        nwp_user = "nwp_qu"
        os.environ['USER'] = nwp_user
        user = disk_usage.get_user_name()
        self.assertEqual(user, 'nwp_qu')

        del os.environ['USER']
        whoami_user = disk_usage.get_user_name()
        self.assertEqual(whoami_user, 'wangdp')

    def test_run_cmquota_command(self):
        output = disk_usage.run_cmquota_command()
        self.assertFalse(len(output) == 0)