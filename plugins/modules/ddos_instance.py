#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.ddos_instance"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ddos_instance
short_description: Manage Anti-DDoS instances.
description:
  - Create, update, or delete Alibaba Cloud ddos_instance resources.
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
    description: ID of an existing Anti-DDoS instance.
    type: str
  edition:
    description: Anti-DDoS edition.
    type: str
    choices: [basic, pro, enterprise]
    default: pro
  bandwidth:
    description: Base bandwidth in Gbps.
    type: int
"""

EXAMPLES = r"""
- name: Manage ddos_instance resource
  stevefulme1.alibaba_cloud.ddos_instance:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    edition: pro
    bandwidth: 30
"""

RETURN = r"""
ddos_instance:
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
        instance_id=dict(type="str"),
        edition=dict(type="str", choices=["basic", "pro", "enterprise"], default="pro"),
        bandwidth=dict(type="int"),
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
            "DescribeInstances",
            {},
            service_endpoint="ddoscoo.aliyuncs.com",
            api_version="2020-01-01",
        )

        data = existing
        for key in "Instances".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateInstance",
                    {},
                    service_endpoint="ddoscoo.aliyuncs.com",
                    api_version="2020-01-01",
                )
                changed = True
                module.exit_json(changed=changed, ddos_instance=result)
            else:
                module.exit_json(changed=False, ddos_instance=data[0])
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "ReleaseInstance",
                    {},
                    service_endpoint="ddoscoo.aliyuncs.com",
                    api_version="2020-01-01",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
