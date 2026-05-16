#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.acm_configuration"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: acm_configuration
short_description: Manage ACM application configurations.
description:
  - Create, update, or delete Alibaba Cloud ACM configuration resources.
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
  namespace_id:
    description: Configuration namespace ID.
    type: str
  data_id:
    description: Configuration data ID.
    type: str
  group:
    description: Configuration group name.
    type: str
  content:
    description: Configuration content body.
    type: str
  config_type:
    description: Content type, e.g. C(text), C(json), C(yaml).
    type: str
"""

EXAMPLES = r"""
- name: Create a ACM configuration
  stevefulme1.alibaba_cloud.acm_configuration:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    namespace_id: example-value
    data_id: example-value
"""

RETURN = r"""
acm_configuration:
  description: Acm configuration details.
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
        data_id=dict(type="str"),
        group=dict(type="str"),
        content=dict(type="str"),
        config_type=dict(type="str"),
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
            "DescribeConfig",
            {},
            service_endpoint="acm.aliyuncs.com",
            api_version="2020-02-06",
        )

        data = existing
        for key in "Configurations.Configuration".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "PublishConfig",
                    {},
                    service_endpoint="acm.aliyuncs.com",
                    api_version="2020-02-06",
                )
                changed = True
                module.exit_json(changed=changed, acm_configuration=result)
            else:
                module.exit_json(
                    changed=False,
                    acm_configuration=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteConfig",
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
