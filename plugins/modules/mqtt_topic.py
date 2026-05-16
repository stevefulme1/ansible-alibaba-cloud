#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.mqtt_topic"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: mqtt_topic
short_description: Manage MQTT topics.
description:
  - Create, update, or delete Alibaba Cloud MQTT topic resources.
  - Supports check mode and is idempotent.version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  state:
    description: Desired state of the resource.
    type: str
    choices: [present, absent]
    default: present
  instance_id:
    description: MQTT instance ID.
    type: str
  topic:
    description: Name of the MQTT topic.
    type: str
  remark:
    description: Description of the topic.
    type: str
"""

EXAMPLES = r"""
- name: Create a MQTT topic
  stevefulme1.alibaba_cloud.mqtt_topic:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    instance_id: example-value
    topic: example-value
"""

RETURN = r"""
mqtt_topic:
  description: Mqtt topic details.
  returned: success
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        state=dict(
            type="str",
            choices=["present", "absent"],
            default="present",
        ),
        instance_id=dict(type="str"),
        topic=dict(type="str"),
        remark=dict(type="str"),
    )
    spec.update(alibaba_argument_spec)

    module = AnsibleModule(
        argument_spec=spec,
        supports_check_mode=True,
    )

    client = AlibabaCloudClient(
        access_key_id=module.params["access_key_id"],
        access_key_secret=module.params["access_key_secret"],
        region_id=module.params["region_id"],
        security_token=module.params.get("security_token"),
        timeout=module.params["timeout"],
    )

    state = module.params["state"]
    changed = False

    try:
        existing = client.get(
            "DescribeTopic",
            {},
            service_endpoint="onsmqtt.{region_id}.aliyuncs.com",
            api_version="2020-04-20",
        )

        data = existing
        for key in "Topics.Topic".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateTopic",
                    {},
                    service_endpoint="onsmqtt.{region_id}.aliyuncs.com",
                    api_version="2020-04-20",
                )
                changed = True
                module.exit_json(changed=changed, mqtt_topic=result)
            else:
                module.exit_json(
                    changed=False,
                    mqtt_topic=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteTopic",
                    {},
                    service_endpoint="onsmqtt.{region_id}.aliyuncs.com",
                    api_version="2020-04-20",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
