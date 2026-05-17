#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.fc_trigger_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: fc_trigger_info
short_description: Query Function Compute triggers.
description:
  - Retrieve information about Alibaba Cloud fc_trigger resources.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  service_name:
    description: Filter by parent service name.
    type: str
    required: true
  function_name:
    description: Filter by parent function name.
    type: str
    required: true
  limit:
    description:
      - Maximum number of results to return.
    type: int
    default: 100
  offset:
    description:
      - Number of results to skip for pagination.
    type: int
    default: 0
"""

EXAMPLES = r"""
- name: Query fc_trigger resources
  stevefulme1.alibaba_cloud.fc_trigger_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
"""

RETURN = r"""
fc_triggers:
  description: List of resources.
  returned: success
  type: list
  elements: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        limit=dict(type="int", default=100),
        offset=dict(type="int", default=0),
        service_name=dict(type="str", required=True),
        function_name=dict(type="str", required=True),
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
    try:
        result = client.get(
            "ListTriggers",
            params,
            service_endpoint="fc.aliyuncs.com",
            api_version="2021-04-06",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    data = result
    for key in "triggers".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, fc_triggers=data)


if __name__ == "__main__":
    main()
