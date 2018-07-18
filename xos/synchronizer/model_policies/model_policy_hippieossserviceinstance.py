
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

    def handle_create(self, si):
        self.logger.debug("MODEL_POLICY: handle_create for HippieOSSServiceInstance %s " % si.id)
        self.handle_update(si)

    def update_and_save_subscriber(self, subscriber, si):
        if si.authentication_state == "STARTED":
            subscriber.status = "awaiting-auth"
        elif si.authentication_state == "REQUESTED":
            subscriber.status = "awaiting-auth"
        elif si.authentication_state == "APPROVED":
            subscriber.status = "enabled"
        elif si.authentication_state == "DENIED":
            subscriber.status = "auth-failed"

        # If the OSS returns a c_tag use that one
        if si.c_tag:
            subscriber.c_tag = si.c_tag

        subscriber.save(always_update_timestamp=False)

    def create_subscriber(self, si):
        subscriber = RCORDSubscriber()
        subscriber.onu_device = si.serial_number
        subscriber.status == "awaiting-auth"
        
        return subscriber

    def handle_update(self, si):
        self.logger.debug("MODEL_POLICY: handle_update for HippieOSSServiceInstance %s, valid=%s " % (si.id, si.valid))

        # Check to make sure the object has been synced. This is to cover a race condition where the model_policy
        # runs, is interrupted by the sync step, the sync step completes, and then the model policy ends up saving
        # a policed_timestamp that is later the updated timestamp set by the sync_step.
        if (si.backend_code!=1):
            raise Exception("MODEL_POLICY: HippieOSSServiceInstance %s has not been synced yet" % si.id)

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
            try:
                onu = ONUDevice.objects.get(serial_number=si.serial_number)
            except IndexError:
                raise Exception("MODEL_POLICY: cannot find ONUDevice [%s] for HippieOSSServiceInstance %s" % (si.serial_number, si.id))
            if onu.admin_state == "DISABLED":
                self.logger.debug("MODEL_POLICY: enabling ONUDevice [%s] for HippieOSSServiceInstance %s" % (si.serial_number, si.id))
                onu.admin_state = "ENABLED"
                onu.save(always_update_timestamp=True)

            # handling the subscriber status

            subscriber = None
            try:
                subscriber = RCORDSubscriber.objects.get(onu_device=si.serial_number)
            except IndexError:
                # we just want to find out if it exists or not
                pass

            # if subscriber does not exist
            self.logger.debug("MODEL_POLICY: handling subscriber", onu_device=si.serial_number, create_on_discovery=si.owner.leaf_model.create_on_discovery)
            if not subscriber:
                # and create_on_discovery is false
                if not si.owner.leaf_model.create_on_discovery:
                    # do not create the subscriber, unless it has been approved
                    if si.authentication_state == "APPROVED":
                        self.logger.debug("MODEL_POLICY: creating subscriber as authentication_sate=APPROVED")
                        subscriber = self.create_subscriber(si)
                        self.update_and_save_subscriber(subscriber, si)
                else:
                    self.logger.debug("MODEL_POLICY: creating subscriber")
                    subscriber = self.create_subscriber(si)
                    self.update_and_save_subscriber(subscriber, si)
            # if the subscriber is there
            elif subscriber:
                # and create_on_discovery is false
                if not si.owner.leaf_model.create_on_discovery:
                    # and in status pre-provisioned, do nothing
                    if subscriber.status == "pre-provisioned":
                        self.logger.debug("MODEL_POLICY: not updating subscriber status as original status is 'pre-provisioned'")
                        return
                    # else update the status
                    else:
                        self.logger.debug("MODEL_POLICY: updating subscriber status as original status is not 'pre-provisioned'")
                        self.update_and_save_subscriber(subscriber, si)
                # if create_on_discovery is true
                else:
                    self.logger.debug("MODEL_POLICY: updating subscriber status")
                    self.update_and_save_subscriber(subscriber, si)

    def handle_delete(self, si):
        pass
