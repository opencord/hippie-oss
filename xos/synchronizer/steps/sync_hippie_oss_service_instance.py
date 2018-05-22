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

import json
from synchronizers.new_base.SyncInstanceUsingAnsible import SyncStep
from synchronizers.new_base.modelaccessor import HippieOSSServiceInstance

from xosconfig import Config
from multistructlog import create_logger

log = create_logger(Config().get('logging'))

class SyncOSSServiceInstance(SyncStep):
    provides = [HippieOSSServiceInstance]
    observes = HippieOSSServiceInstance

    def validate_in_external_oss(self, serial_number):
        # This is where you may want to call your OSS Database to verify if this ONU can be activated
        return True

    def get_suscriber_c_tag(self, serial_number):
        # If it's up to your OSS to generate c_tags, fetch them here
        # otherwise XOS will generate one for your subscriber
        return None

    def sync_record(self, o):
        log.info("synching HippieOSSServiceInstance", object=str(o), **o.tologdict())

        if not self.validate_in_external_oss(o.serial_number):
            log.error("ONU with serial number %s is not valid in the OSS Database")
            return

        if self.get_suscriber_c_tag(o.serial_number):
            self.c_tag = self.get_suscriber_c_tag(o.serial_number)

        o.valid = True

        # FIXME why without this model_policies won't run the handle_update?
        o.no_sync = True
        o.save(always_update_timestamp=True)

    def delete_record(self, o):
        pass
