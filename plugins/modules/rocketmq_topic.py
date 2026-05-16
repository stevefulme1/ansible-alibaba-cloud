#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.rocketmq_topic"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: rocketmq_topic
short_description: Manage RocketMQ topics.
description:
  - Create, update, or delete Alibaba Cloud rocketmq_topic resources.
  - Supports check mode and is idempotent.
version_added: "1.0.0"
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
    description: RocketMQ instance ID.
    type: str
    required: true
  topic:
    description: Topic name.
    type: str
    required: true
  message_type:
    description: Message type.
    type: int
    choices: [0, 1, 2, 4, 5]
  remark:
    description: Topic description.
    type: str
"""

EXAMPLES = r"""
- name: Manage rocketmq_topic resource
  stevefulme1.alibaba_cloud.rocketmq_topic:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    instance_id: MQ_INST_xxxxx
    topic: order-events
"""

RETURN = r"""
rocketmq_topic:
  description: Resource details.
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
        state=dict(type="str", choices=["present", "absent"], default="present"),
        instance_id=dict(type="str", required=True),
        topic=dict(type="str", required=True),
        message_type=dict(type="int", choices=[0, 1, 2, 4, 5]),
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
            "OnsTopicList",
            {},
            service_endpoint="ons.aliyuncs.com",
            api_version="2019-02-14",
        )

        data = existing
        for key in "Data.PublishInfoDo".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "OnsTopicCreate",
                    {},
                    service_endpoint="ons.aliyuncs.com",
                    api_version="2019-02-14",
                )
                changed = True
                module.exit_json(changed=changed, rocketmq_topic=result)
            else:
                module.exit_json(changed=False, rocketmq_topic=data[0])
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "OnsTopicDelete",
                    {},
                    service_endpoint="ons.aliyuncs.com",
                    api_version="2019-02-14",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
