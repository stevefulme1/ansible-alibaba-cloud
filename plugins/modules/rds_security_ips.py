#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.rds_security_ips"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: rds_security_ips
short_description: Manage RDS IP whitelist.
description:
  - Configure the IP whitelist for an Alibaba Cloud RDS instance.
  - Supports check mode and is idempotent.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  db_instance_id:
    description: RDS instance ID.
    type: str
  security_ips:
    description: Comma-separated list of allowed IP addresses.
    type: str
  whitelist_network_type:
    description: Network type.
    type: str
    choices: ['Classic', 'VPC', 'MIX']
"""

EXAMPLES = r"""
- name: Manage RDS IP whitelist
  stevefulme1.alibaba_cloud.rds_security_ips:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
rds_security_ips:
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
        db_instance_id=dict(type="str"),
        security_ips=dict(type="str"),
        whitelist_network_type=dict(type="str", choices=["Classic", "VPC", "MIX"]),
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
            "DescribeDBInstanceIPArrayList",
            {},
            service_endpoint="rds.aliyuncs.com",
            api_version="2014-08-15",
        )

        data = existing
        for key in "Items.DBInstanceIPArray".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "ModifySecurityIps",
                    {},
                    service_endpoint="rds.aliyuncs.com",
                    api_version="2014-08-15",
                )
                changed = True
                module.exit_json(
                    changed=changed,
                    rds_security_ips=result,
                )
            else:
                module.exit_json(
                    changed=False,
                    rds_security_ips=data[0],
                )

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
