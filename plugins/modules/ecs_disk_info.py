#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.ecs_disk_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ecs_disk_info
short_description: List disks.
description:
  - Retrieve information about Alibaba Cloud ecs_disk resources.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  instance_id:
    description: Filter by attached instance.
    type: str
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
- name: List disks
  stevefulme1.alibaba_cloud.ecs_disk_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
"""

RETURN = r"""
disks:
  description: List of disks.
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
        instance_id=dict(type="str"),
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
    if module.params.get("instance_id") is not None:
        params["InstanceId"] = module.params["instance_id"]
    try:
        result = client.get(
            "DescribeDisks",
            params,
            service_endpoint="ecs.aliyuncs.com",
            api_version="2014-05-26",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "Disks.Disk".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, ecs_disks=data)


if __name__ == "__main__":
    main()
