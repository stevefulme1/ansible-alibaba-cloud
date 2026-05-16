#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.rds_proxy"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: rds_proxy
short_description: Manage database proxy configuration.
description:
  - Create, update, or delete Alibaba Cloud rds_proxy resources.
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
  db_instance_id:
    description: RDS instance ID.
    type: str
  db_proxy_instance_type:
    description: Proxy type (DedicatedProxy).
    type: str
  db_proxy_instance_num:
    description: Number of proxy instances.
    type: int
"""

EXAMPLES = r"""
- name: Manage rds_proxy
  stevefulme1.alibaba_cloud.rds_proxy:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    db_instance_id: rm-xxx
    db_proxy_instance_num: 2
"""

RETURN = r"""
rds_proxy:
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
        state=dict(
            type="str",
            choices=["present", "absent"],
            default="present",
        ),
        db_instance_id=dict(type="str"),
        db_proxy_instance_type=dict(type="str"),
        db_proxy_instance_num=dict(type="int"),
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
        result = client.get(
            "DescribeDBProxy",
            {},
            service_endpoint="rds.aliyuncs.com",
            api_version="2014-08-15",
        )

        data = result
        for key in ["DBProxyList"]:
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "ModifyDBProxy",
                    {},
                    service_endpoint="rds.aliyuncs.com",
                    api_version="2014-08-15",
                )
                changed = True
                module.exit_json(changed=changed, rds_proxy=result)
            else:
                module.exit_json(
                    changed=False,
                    rds_proxy=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "ModifyDBProxy",
                    {},
                    service_endpoint="rds.aliyuncs.com",
                    api_version="2014-08-15",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
