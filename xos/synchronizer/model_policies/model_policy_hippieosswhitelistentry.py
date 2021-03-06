
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


from synchronizers.new_base.modelaccessor import HippieOSSServiceInstance, HippieOSSWhiteListEntry, model_accessor
from synchronizers.new_base.policy import Policy

class OSSWhiteListEntryPolicy(Policy):
    model_name = "HippieOSSWhiteListEntry"

    def handle_create(self, whitelist):
        self.handle_update(whitelist)

    def handle_update(self, whitelist):
        self.logger.debug("MODEL_POLICY: handle_update for HippieOSSWhiteListEntry", whitelist=whitelist)

        sis = HippieOSSServiceInstance.objects.filter(serial_number = whitelist.serial_number,
                                                   owner_id = whitelist.owner.id)

        for si in sis:
            if si.valid != "valid":
                self.logger.debug("MODEL_POLICY: activating HippieOSSServiceInstance because of change in the whitelist", si=si)
                si.valid = "valid"
                si.save(update_fields=["valid", "no_sync", "updated"], always_update_timestamp=True)

        whitelist.backend_need_delete_policy=True
        whitelist.save(update_fields=["backend_need_delete_policy"])

    def handle_delete(self, whitelist):
        self.logger.debug("MODEL_POLICY: handle_delete for HippieOSSWhiteListEntry", whitelist=whitelist)

        # BUG: Sometimes the delete policy is not called, because the reaper deletes

        assert(whitelist.owner)

        sis = HippieOSSServiceInstance.objects.filter(serial_number = whitelist.serial_number,
                                                   owner_id = whitelist.owner.id)

        for si in sis:
            if si.valid != "invalid":
                self.logger.debug(
                    "MODEL_POLICY: disabling HippieOSSServiceInstance because of change in the whitelist", si=si)
                si.valid = "invalid"
                si.save(update_fields=["valid", "no_sync", "updated"], always_update_timestamp=True)

        whitelist.backend_need_reap=True
        whitelist.save(update_fields=["backend_need_reap"])
