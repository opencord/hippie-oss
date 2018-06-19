
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


from synchronizers.new_base.modelaccessor import RCORDSubscriber, ONUDevice, model_accessor
from synchronizers.new_base.policy import Policy

class OSSServiceInstancePolicy(Policy):
    model_name = "HippieOSSServiceInstance"

    def handle_update(self, si):
        self.logger.debug("MODEL_POLICY: handle_update for HippieOSSServiceInstance %s " % si.id)

        if not hasattr(si, 'valid') or si.valid is "awaiting":
            self.logger.debug("MODEL_POLICY: skipping handle_update for HippieOSSServiceInstance %s as not validated yet" % si.id)
            return
        if si.valid == "invalid":
            self.logger.debug("MODEL_POLICY: disabling ONUDevice [%s] for HippieOSSServiceInstance %s" % (si.serial_number, si.id))
            onu = ONUDevice.objects.get(serial_number=si.serial_number)
            onu.admin_state = "DISABLED"
            onu.save(always_update_timestamp=True)
            return
        if si.valid == "valid":

            # reactivating the ONUDevice
            onu = ONUDevice.objects.get(serial_number=si.serial_number)
            if onu.admin_state == "DISABLED":
                self.logger.debug("MODEL_POLICY: enabling ONUDevice [%s] for HippieOSSServiceInstance %s" % (
                si.serial_number, si.id))
                onu.admin_state = "ENABLED"
                onu.save(always_update_timestamp=True)

            # NOTE this assumes that an ONUDevice has only one Subscriber
            try:
                subscriber = RCORDSubscriber.objects.get(onu_device=si.serial_number)

                # If the OSS returns a c_tag and the subscriber doesn't already have his one
                if si.c_tag and not subscriber.c_tag:
                    self.logger.debug("MODEL_POLICY: updating c_tag for RCORDSubscriber %s and HippieOSSServiceInstance %s" % (subscriber.id, si.id))
                    subscriber.c_tag = si.c_tag
                else:
                    # if we're not changing anything in the subscriber, we don't need to update it
                    return
            except IndexError, e:
                self.logger.debug("MODEL_POLICY: creating RCORDSubscriber for HippieOSSServiceInstance %s" % si.id)

                subscriber = RCORDSubscriber()
                subscriber.onu_device = si.serial_number

                # If the OSS returns a c_tag use that one
                if si.c_tag:
                    subscriber.c_tag = si.c_tag

            subscriber.save()
            return

    def handle_delete(self, si):
        pass
