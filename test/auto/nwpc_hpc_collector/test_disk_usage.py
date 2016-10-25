import unittest
from unittest import mock
import os
import importlib

from nwpc_hpc_collector import disk_usage


nwp_cmquota_output = """                         Block Limits                                    |     File Limits
Filesystem type             KB      quota      limit   in_doubt    grace |    files   quota    limit in_doubt    grace  Remarks
cma_g1     USR      18768613888 32212254720 32212254720   43603712     none |  2089619       0        0     4683     none uranus
cma_u      USR       110718976  209715200  209715200     343040     none |   124332       0        0       81     none uranus
cma_g2     USR         no limits                  uranus
cma_g3     USR         no limits                  uranus
cma_g4     USR         no limits                  uranus
cma_g5     USR         no limits                  uranus
cma_g6     USR         no limits                  uranus
cma_g7     USR         no limits                  uranus
cmb_g2     USR         no limits                  neptune
cmb_g3     USR            none                                 neptune
cmb_g4     USR         no limits                  neptune
cmb_g5     USR         no limits                  neptune
cmb_g6     USR         no limits                  neptune
cmb_g7     USR         no limits                  neptune
"""
nwp_cmquota_user_name = 'nwp'
nwp_file_systems = [
    {
        'file_system': 'cma_g1',
        'type': 'USR',
        'block_limits': {
            'current': 18768613888,
            'quota': 32212254720,
            'limit': 32212254720,
            'in_doubt': 43603712,
            'grace': 'none'
        },
        'file_limits': {
            'files': 2089619,
            'quota': 0,
            'limit': 0,
            'in_doubt': 4683,
            'grace': 'none',
            'remarks': 'uranus'
        }
    },
    {
        'file_system': 'cma_u',
        'type': 'USR',
        'block_limits': {
            'current': 110718976,
            'quota': 209715200,
            'limit': 209715200,
            'in_doubt': 343040,
            'grace': 'none'
        },
        'file_limits': {
            'files': 124332,
            'quota': 0,
            'limit': 0,
            'in_doubt': 81,
            'grace': 'none',
            'remarks': 'uranus'
        }
    }
]

"""
nwp_qu
                         Block Limits                                    |     File Limits
Filesystem type             KB      quota      limit   in_doubt    grace |    files   quota    limit in_doubt    grace  Remarks
cma_g1     USR      29463581184 42949672960 45097156608   32264448     none |   993867       0        0     1280     none uranus
cma_u      USR        84744960   92434432   92434432     578816     none |    95066       0        0      140     none uranus
cma_g2     USR         no limits                  uranus
cma_g3     USR         no limits                  uranus
cma_g4     USR         no limits                  uranus
cma_g5     USR      10315454592 42212257792 42243715072          0     none |    22192       0        0        0     none uranus
cma_g6     USR      47039924224 53687091200 53697576960   43093632     none |  4707119       0        0     7645     none uranus
cma_g7     USR         no limits                  uranus
cmb_g2     USR         no limits                  neptune
cmb_g3     USR      5471733248 6291456000 6291456000   75669888     none |  1225733       0        0     4437     none neptune
cmb_g4     USR         no limits                  neptune
cmb_g5     USR         no limits                  neptune
cmb_g6     USR         no limits                  neptune
cmb_g7     USR         no limits                  neptune
"""

nwp_qu_file_systems = [

]

"""
wangdp

                         Block Limits                                    |     File Limits
Filesystem type             KB      quota      limit   in_doubt    grace |    files   quota    limit in_doubt    grace  Remarks
cma_g1     USR         no limits                    uranus
cma_u      USR         1223936   10485760   15728640      85248     none |     3329       0        0       20     none uranus
cma_g2     USR         no limits                  uranus
cma_g3     USR       938156416 1048576000 1101004800     491520     none |  1106894       0        0      121     none uranus
cma_g4     USR         no limits                  uranus
cma_g5     USR         no limits                  uranus
cma_g6     USR         no limits                  uranus
cma_g7     USR         no limits                  uranus
cmb_g2     USR         no limits                  neptune
cmb_g3     USR         no limits                  neptune
cmb_g4     USR         no limits                  neptune
cmb_g5     USR         no limits                  neptune
cmb_g6     USR         no limits                  neptune
cmb_g7     USR         no limits                  neptune

"""

wangdp_file_systems = [

]


class TestDiskUsage(unittest.TestCase):

    def setUp(self):
        importlib.reload(disk_usage)

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

    def test_get_cmquota(self):
        nwp_cmquota_command = mock.Mock(return_value=nwp_cmquota_output)
        nwp_get_user_name = mock.Mock(return_value=nwp_cmquota_user_name)

        disk_usage.run_cmquota_command = nwp_cmquota_command
        disk_usage.get_user_name = nwp_get_user_name

        cmquota_result = disk_usage.get_cmquota()

        self.assertEqual(cmquota_result['user'], 'nwp')
        self.assertTrue('file_systems' in cmquota_result)

        filesystems = cmquota_result['file_systems']
        file_system_count = len(nwp_file_systems)
        self.assertEqual(len(filesystems), file_system_count)

        for i in range(0, file_system_count):
            a_file_system = filesystems[i]
            expect_file_system = nwp_file_systems[i]
            self.assertEqual(a_file_system, expect_file_system)