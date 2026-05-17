#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.slb_server_group"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: slb_server_group
short_description: Manage SLB backend server groups.
description:
  - Create, update, or delete Alibaba Cloud slb_server_group resources.
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
  load_balancer_id:
    description: SLB instance ID.
    type: str
    required: true
  vserver_group_name:
    description: Name of the server group.
    type: str
  backend_servers:
    description: List of backend server dicts with ServerId and Port.
    type: list
    elements: dict
  vserver_group_id:
    description: Existing group ID (for delete).
    type: str
"""

EXAMPLES = r"""
- name: Create server group
  stevefulme1.alibaba_cloud.slb_server_group:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    load_balancer_id: lb-xxxxx
    vserver_group_name: web-backends
"""

RETURN = r"""
server_group:
  description: Server group details.
  returned: success
  type: dict
"""

import json

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
        load_balancer_id=dict(type="str", required=True),
        vserver_group_name=dict(type="str"),
        backend_servers=dict(type="list", elements="dict"),
        vserver_group_id=dict(type="str"),
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
    if module.params.get("load_balancer_id") is not None:
        params["LoadBalancerId"] = module.params["load_balancer_id"]
    if module.params.get("vserver_group_name") is not None:
        params["VserverGroupName"] = module.params["vserver_group_name"]
    if module.params.get("backend_servers") is not None:
        params["BackendServers"] = json.dumps(module.params["backend_servers"])
    if module.params.get("vserver_group_id") is not None:
        params["VserverGroupId"] = module.params["vserver_group_id"]

    try:
        # Describe existing resources to check idempotency.
        existing = client.get(
            "DescribeVServerGroups",
            params,
            service_endpoint="slb.aliyuncs.com",
            api_version="2014-05-15",
        )

        data = existing
        for key in "VServerGroups.VServerGroup".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateVServerGroup",
                    params,
                    service_endpoint="slb.aliyuncs.com",
                    api_version="2014-05-15",
                )
                changed = True
                module.exit_json(changed=changed, slb_server_group=result)
            else:
                module.exit_json(
                    changed=False,
                    slb_server_group=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteVServerGroup",
                    params,
                    service_endpoint="slb.aliyuncs.com",
                    api_version="2014-05-15",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
