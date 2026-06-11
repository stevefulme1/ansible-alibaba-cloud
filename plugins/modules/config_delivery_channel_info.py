#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.config_delivery_channel_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: config_delivery_channel_info
short_description: Query Cloud Config delivery channels.
description:
  - Retrieve information about Alibaba Cloud Config delivery channels.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  delivery_channel_id:
    description: Filter by delivery channel ID.
    type: str
"""

EXAMPLES = r"""
- name: Query all delivery channels
  stevefulme1.alibaba_cloud.config_delivery_channel_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou

- name: Query specific delivery channel
  stevefulme1.alibaba_cloud.config_delivery_channel_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    delivery_channel_id: cdc-123
"""

RETURN = r"""
config_delivery_channels:
  description: List of Cloud Config delivery channels.
  returned: success
  type: list
  elements: dict
  sample:
    - delivery_channel_id: cdc-123
      delivery_channel_name: oss-channel
      delivery_channel_type: OSS
      status: 1
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        delivery_channel_id=dict(type="str"),
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

    params = {}
    if module.params.get("delivery_channel_id"):
        params["DeliveryChannelId"] = module.params["delivery_channel_id"]

    try:
        result = client.get(
            "DescribeDeliveryChannels",
            params,
            service_endpoint="config.aliyuncs.com",
            api_version="2020-09-07",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "DeliveryChannels".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, config_delivery_channels=data)


if __name__ == "__main__":
    main()
