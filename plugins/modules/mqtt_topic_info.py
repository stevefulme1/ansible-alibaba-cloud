#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.mqtt_topic_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: mqtt_topic_info
short_description: Query MQTT topics.
description:
  - Retrieve information about Alibaba Cloud MQTT topics.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  instance_id:
    description: MQTT instance ID.
    type: str
    required: true
  topic:
    description: Filter by topic name.
    type: str
"""

EXAMPLES = r"""
- name: Query all MQTT topics
  stevefulme1.alibaba_cloud.mqtt_topic_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    instance_id: mqtt-123

- name: Query specific MQTT topic
  stevefulme1.alibaba_cloud.mqtt_topic_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    instance_id: mqtt-123
    topic: sensors/temperature
"""

RETURN = r"""
mqtt_topics:
  description: List of MQTT topics.
  returned: success
  type: list
  elements: dict
  sample:
    - topic: sensors/temperature
      create_time: 1234567890
      relation: 1
      relation_type: GROUP
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        instance_id=dict(type="str", required=True),
        topic=dict(type="str"),
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

    params = {
        "InstanceId": module.params["instance_id"],
    }
    if module.params.get("topic"):
        params["Topic"] = module.params["topic"]

    try:
        result = client.get(
            "ListGroupId",
            params,
            service_endpoint="onsmqtt.{region_id}.aliyuncs.com",
            api_version="2020-04-20",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "Topics.Topic".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, mqtt_topics=data)


if __name__ == "__main__":
    main()
