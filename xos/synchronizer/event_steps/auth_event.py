
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
import time
import os
import sys
from synchronizers.new_base.eventstep import EventStep
from synchronizers.new_base.modelaccessor import VOLTService, HippieOSSServiceInstance, model_accessor

class SubscriberAuthEventStep(EventStep):
    topics = ["authentication.events"]
    technology = "kafka"

    def __init__(self, *args, **kwargs):
        super(SubscriberAuthEventStep, self).__init__(*args, **kwargs)

    def get_onu_sn(self, event):
        olt_service = VOLTService.objects.first()
        onu_sn = olt_service.get_onu_sn_from_openflow(event["device_id"], event["port_number"])
        if not onu_sn or onu_sn is None:
            self.log.exception("authentication.events: Cannot find onu serial number for this event", kafka_event=event)
            raise Exception("authentication.events: Cannot find onu serial number for this event")

        return onu_sn

    def get_hippie_oss_si_by_sn(self, serial_number):
        try:
            return HippieOSSServiceInstance.objects.get(serial_number=serial_number)
        except IndexError:
            self.log.exception("authentication.events: Cannot find hippie-oss service instance for this event", kafka_event=value)
            raise Exception("authentication.events: Cannot find hippie-oss service instance for this event")


    def activate_subscriber(self, subscriber):
        subscriber.status = 'enabled'
        subscriber.save()

    def disable_subscriber(self, subscriber):
        subscriber.status = 'auth-failed'
        subscriber.save()

    def process_event(self, event):
        value = json.loads(event.value)

        onu_sn = self.get_onu_sn(value)
        si = self.get_hippie_oss_si_by_sn(onu_sn)
        if not si:
            self.log.exception("authentication.events: Cannot find hippie-oss service instance for this event", kafka_event=value)
            raise Exception("authentication.events: Cannot find hippie-oss service instance for this event")

        si.authentication_state = value["authentication_state"];
        si.no_sync = True
        si.save(update_fields=["authentication_state", "no_sync", "updated"], always_update_timestamp=True)
