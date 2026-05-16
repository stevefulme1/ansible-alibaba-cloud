#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.eci_image_cache"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: eci_image_cache
short_description: Manage ECI image caches.
description:
  - Create or delete manage eci image caches.
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
  image_cache_id:
    description: Image cache ID.
    type: str
  image_cache_name:
    description: Image cache name.
    type: str
  images:
    description: List of container images to cache.
    type: list
    elements: str
  security_group_id:
    description: Security group ID.
    type: str
  vswitch_id:
    description: VSwitch ID.
    type: str"""

EXAMPLES = r"""
- name: Manage ECI image caches.
  stevefulme1.alibaba_cloud.eci_image_cache:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
eci_image_cache:
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
        image_cache_id=dict(type="str"),
        image_cache_name=dict(type="str"),
        images=dict(type="list", elements="str"),
        security_group_id=dict(type="str"),
        vswitch_id=dict(type="str"),
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
            "DescribeImageCaches",
            {},
            service_endpoint="eci.aliyuncs.com",
            api_version="2018-08-08",
        )

        data = existing
        for key in "ImageCaches".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateImageCache",
                    {},
                    service_endpoint="eci.aliyuncs.com",
                    api_version="2018-08-08",
                )
                changed = True
                module.exit_json(changed=changed, eci_image_cache=result)
            else:
                module.exit_json(changed=False, eci_image_cache=data[0])

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteImageCache",
                    {},
                    service_endpoint="eci.aliyuncs.com",
                    api_version="2018-08-08",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
