#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.ots_instance"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ots_instance
short_description: Manage Table Store instances.
description:
  - Create or delete manage table store instances.
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
  instance_name:
    description: Table Store instance name.
    type: str
  cluster_type:
    description: Instance cluster type.
    type: str
    choices: ['SSD', 'HYBRID']"""

EXAMPLES = r"""
- name: Manage Table Store instances.
  stevefulme1.alibaba_cloud.ots_instance:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
ots_instance:
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
        instance_name=dict(type="str"),
        cluster_type=dict(type="str", choices=["SSD", "HYBRID"]),
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

    params = {}
    if module.params.get("instance_name") is not None:
        params["InstanceName"] = module.params["instance_name"]
    if module.params.get("cluster_type") is not None:
        params["ClusterType"] = module.params["cluster_type"]


    try:
        existing = client.get(
            "ListInstance",
            params,
            service_endpoint="ots.aliyuncs.com",
            api_version="2016-06-20",
        )

        data = existing
        for key in "InstanceInfos.InstanceInfo".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "InsertInstance",
                    params,
                    service_endpoint="ots.aliyuncs.com",
                    api_version="2016-06-20",
                )
                changed = True
                module.exit_json(changed=changed, ots_instance=result)
            else:
                module.exit_json(changed=False, ots_instance=data[0])

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteInstance",
                    params,
                    service_endpoint="ots.aliyuncs.com",
                    api_version="2016-06-20",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
