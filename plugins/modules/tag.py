#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.tag"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: tag
short_description: Manage resource tags.
description:
  - Create or delete manage resource tags.
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
  resource_type:
    description: Resource type to tag.
    type: str
    required: true
  resource_ids:
    description: List of resource IDs to tag.
    type: list
    elements: str
  tags:
    description: Dictionary of tag key-value pairs.
    type: dict"""

EXAMPLES = r"""
- name: Manage resource tags.
  stevefulme1.alibaba_cloud.tag:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
tag:
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
        resource_type=dict(type="str", required=True),
        resource_ids=dict(type="list", elements="str"),
        tags=dict(type="dict"),
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
            "ListTagResources",
            {},
            service_endpoint="tag.aliyuncs.com",
            api_version="2018-08-28",
        )

        data = existing
        for key in "TagResources.TagResource".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "TagResources",
                    {},
                    service_endpoint="tag.aliyuncs.com",
                    api_version="2018-08-28",
                )
                changed = True
                module.exit_json(changed=changed, tag=result)
            else:
                module.exit_json(changed=False, tag=data[0])

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "UntagResources",
                    {},
                    service_endpoint="tag.aliyuncs.com",
                    api_version="2018-08-28",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
