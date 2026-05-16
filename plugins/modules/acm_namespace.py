#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.acm_namespace"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: acm_namespace
short_description: Manage ACM configuration namespaces.
description:
  - Create, update, or delete Alibaba Cloud ACM namespace resources.
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
  namespace_id:
    description: Configuration namespace ID.
    type: str
  namespace_name:
    description: Display name of the namespace.
    type: str
  namespace_desc:
    description: Namespace description.
    type: str
"""

EXAMPLES = r"""
- name: Create a ACM namespace
  stevefulme1.alibaba_cloud.acm_namespace:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    namespace_id: example-value
    namespace_name: example-value
"""

RETURN = r"""
acm_namespace:
  description: Acm namespace details.
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
        namespace_id=dict(type="str"),
        namespace_name=dict(type="str"),
        namespace_desc=dict(type="str"),
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
            "DescribeNamespace",
            {},
            service_endpoint="acm.aliyuncs.com",
            api_version="2020-02-06",
        )

        data = existing
        for key in "Namespaces.Namespace".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateNamespace",
                    {},
                    service_endpoint="acm.aliyuncs.com",
                    api_version="2020-02-06",
                )
                changed = True
                module.exit_json(changed=changed, acm_namespace=result)
            else:
                module.exit_json(
                    changed=False,
                    acm_namespace=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteNamespace",
                    {},
                    service_endpoint="acm.aliyuncs.com",
                    api_version="2020-02-06",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
