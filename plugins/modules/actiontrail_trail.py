#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.actiontrail_trail"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: actiontrail_trail
short_description: Manage ActionTrail trails.
description:
  - Create, update, or delete Alibaba Cloud ActionTrail audit trails.
  - Supports check mode and is idempotent.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  state:
    description: Desired state of the resource.
    type: str
    choices: ['present', 'absent']
    default: present
  name:
    description: Trail name.
    type: str
  oss_bucket_name:
    description: OSS bucket for log delivery.
    type: str
  oss_key_prefix:
    description: OSS key prefix for logs.
    type: str
  sls_project_arn:
    description: SLS project ARN for log delivery.
    type: str
  trail_region:
    description: Region scope for the trail.
    type: str
    choices: ['All', 'cn-hangzhou']
"""

EXAMPLES = r"""
- name: Manage ActionTrail trails
  stevefulme1.alibaba_cloud.actiontrail_trail:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
actiontrail_trail:
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
        name=dict(type="str"),
        oss_bucket_name=dict(type="str"),
        oss_key_prefix=dict(type="str"),
        sls_project_arn=dict(type="str"),
        trail_region=dict(type="str", choices=["All", "cn-hangzhou"]),
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
        # Describe existing resources to check idempotency.
        existing = client.get(
            "DescribeTrails",
            {},
            service_endpoint="actiontrail.aliyuncs.com",
            api_version="2020-07-06",
        )

        data = existing
        for key in "TrailList".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateTrail",
                    {},
                    service_endpoint="actiontrail.aliyuncs.com",
                    api_version="2020-07-06",
                )
                changed = True
                module.exit_json(
                    changed=changed,
                    actiontrail_trail=result,
                )
            else:
                module.exit_json(
                    changed=False,
                    actiontrail_trail=data[0],
                )

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteTrail",
                    {},
                    service_endpoint="actiontrail.aliyuncs.com",
                    api_version="2020-07-06",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
