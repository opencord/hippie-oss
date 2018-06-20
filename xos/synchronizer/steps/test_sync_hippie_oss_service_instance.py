# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

import functools
from mock import patch, call, Mock, PropertyMock
import requests_mock
import multistructlog
from multistructlog import create_logger

import os, sys

# Hack to load synchronizer framework
test_path=os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
xos_dir=os.path.join(test_path, "../../..")
if not os.path.exists(os.path.join(test_path, "new_base")):
    xos_dir=os.path.join(test_path, "../../../../../../orchestration/xos/xos")
    services_dir = os.path.join(xos_dir, "../../xos_services")
sys.path.append(xos_dir)
sys.path.append(os.path.join(xos_dir, 'synchronizers', 'new_base'))
# END Hack to load synchronizer framework

# generate model from xproto
def get_models_fn(service_name, xproto_name):
    name = os.path.join(service_name, "xos", xproto_name)
    if os.path.exists(os.path.join(services_dir, name)):
        return name
    else:
        name = os.path.join(service_name, "xos", "synchronizer", "models", xproto_name)
        if os.path.exists(os.path.join(services_dir, name)):
            return name
    raise Exception("Unable to find service=%s xproto=%s" % (service_name, xproto_name))
# END generate model from xproto

class TestSyncHippieOssServiceInstance(unittest.TestCase):

    def setUp(self):

        self.sys_path_save = sys.path
        sys.path.append(xos_dir)
        sys.path.append(os.path.join(xos_dir, 'synchronizers', 'new_base'))

        # Setting up the config module
        from xosconfig import Config
        config = os.path.join(test_path, "../test_config.yaml")
        Config.clear()
        Config.init(config, "synchronizer-config-schema.yaml")
        # END Setting up the config module

        from synchronizers.new_base.mock_modelaccessor_build import build_mock_modelaccessor
        build_mock_modelaccessor(xos_dir, services_dir, [
            get_models_fn("hippie-oss", "hippie-oss.xproto"),
            get_models_fn("olt-service", "volt.xproto"),
            get_models_fn("../profiles/rcord", "rcord.xproto")
        ])
        import synchronizers.new_base.modelaccessor

        from sync_hippie_oss_service_instance import SyncOSSServiceInstance, model_accessor

        # import all class names to globals
        for (k, v) in model_accessor.all_model_classes.items():
            globals()[k] = v


        self.sync_step = SyncOSSServiceInstance

        self.oss = Mock()
        self.oss.name = "oss"
        self.oss.blacklist = ""

        # create a mock VRouterStaticRoute instance
        self.o = Mock()
        self.o.serial_number = "BRCM1234"
        self.o.uni_port_id = 16
        self.o.of_dpid = "of:109299321"
        self.o.owner.leaf_model = self.oss
        self.o.tologdict.return_value = {}

    def tearDown(self):
        self.o = None
        sys.path = self.sys_path_save

    def test_sync_valid(self):

        self.sync_step().sync_record(self.o)

        self.assertEqual(self.o.valid, "valid")
        self.assertTrue(self.o.no_sync)
        self.o.save.assert_called()

    def test_sync_rejected(self):
        self.oss.blacklist = "BRCM5678, BRCM1234"

        self.sync_step().sync_record(self.o)

        self.assertEqual(self.o.valid, "invalid")
        self.assertTrue(self.o.no_sync)
        self.o.save.assert_called()