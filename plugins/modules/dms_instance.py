#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.dms_instance"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: dms_instance
short_description: Register database instances in DMS.
description:
  - Create, update, or delete Alibaba Cloud DMS instance resources.
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
  instance_source:
    description: Source type, e.g. C(RDS) or C(ECS_OWN).
    type: str
  database_type:
    description: Database engine, e.g. C(MySQL), C(PostgreSQL).
    type: str
  host:
    description: Database host address.
    type: str
  port:
    description: Database port.
    type: int
  sid:
    description: Service identifier or database name.
    type: str
  instance_id:
    description: ID of an existing DMS instance.
    type: str
"""

EXAMPLES = r"""
- name: Create a DMS instance
  stevefulme1.alibaba_cloud.dms_instance:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    instance_source: example-value
    database_type: example-value
"""

RETURN = r"""
dms_instance:
  description: Dms instance details.
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
        instance_source=dict(type="str"),
        database_type=dict(type="str"),
        host=dict(type="str"),
        port=dict(type="int"),
        sid=dict(type="str"),
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

    state = module.params["state"]
    changed = False

    try:
        existing = client.get(
            "DescribeInstance",
            {},
            service_endpoint="dms-enterprise.aliyuncs.com",
            api_version="2018-11-01",
        )

        data = existing
        for key in "Instances.Instance".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "RegisterInstance",
                    {},
                    service_endpoint="dms-enterprise.aliyuncs.com",
                    api_version="2018-11-01",
                )
                changed = True
                module.exit_json(changed=changed, dms_instance=result)
            else:
                module.exit_json(
                    changed=False,
                    dms_instance=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteInstance",
                    {},
                    service_endpoint="dms-enterprise.aliyuncs.com",
                    api_version="2018-11-01",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
