
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


from synchronizers.new_base.modelaccessor import RCORDSubscriber, model_accessor
from synchronizers.new_base.policy import Policy

class OSSServiceInstancePolicy(Policy):
    model_name = "HippieOSSServiceInstance"

    def handle_update(self, si):
        self.logger.debug("MODEL_POLICY: handle_update for HippieOSSServiceInstance %s " % si.id)
        if not si.valid:
            # NOTE we don't do anything if the ONU has not been activated
            self.logger.debug("MODEL_POLICY: skipping handle_update for HippieOSSServiceInstance %s as valid is %s" % (si.id, si.valid))
            pass
        else:
            self.logger.debug("MODEL_POLICY: creating RCORDSubscriber for HippieOSSServiceInstance %s as valid is %s" % (si.id, si.valid))
            subscriber = RCORDSubscriber()
            subscriber.onu_device = si.serial_number
            subscriber.uni_port_id = si.uni_port_id

            # If the OSS returns a c_tag use that one
            if si.c_tag:
                subscriber.c_tag = si.c_tag

            subscriber.save()

    def handle_delete(self, si):
        pass
