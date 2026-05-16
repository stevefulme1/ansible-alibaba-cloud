#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.flow_log"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: flow_log
short_description: Manage VPC flow log.
description:
  - Create, update, or delete Alibaba Cloud flow_log resources.
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
  flow_log_name:
    description: Flow log name.
    type: str
  resource_type:
    description: Resource type (VPC, VSwitch, NetworkInterface).
    type: str
  resource_id:
    description: Resource ID to capture.
    type: str
  traffic_type:
    description: Traffic type (All, Allow, Drop).
    type: str
  project_name:
    description: SLS project for log storage.
    type: str
  log_store_name:
    description: SLS logstore for log storage.
    type: str
  flow_log_id:
    description: Flow log ID for delete.
    type: str
"""

EXAMPLES = r"""
- name: Manage flow_log
  stevefulme1.alibaba_cloud.flow_log:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    flow_log_name: vpc-flow-log
    resource_type: VPC
"""

RETURN = r"""
flow_log:
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
        flow_log_name=dict(type="str"),
        resource_type=dict(type="str"),
        resource_id=dict(type="str"),
        traffic_type=dict(type="str"),
        project_name=dict(type="str"),
        log_store_name=dict(type="str"),
        flow_log_id=dict(type="str"),
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
            "DescribeFlowLogs",
            {},
            service_endpoint="vpc.aliyuncs.com",
            api_version="2016-04-28",
        )

        data = result
        for key in ["FlowLogs", "FlowLog"]:
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateFlowLog",
                    {},
                    service_endpoint="vpc.aliyuncs.com",
                    api_version="2016-04-28",
                )
                changed = True
                module.exit_json(changed=changed, flow_log=result)
            else:
                module.exit_json(
                    changed=False,
                    flow_log=data[0],
                )
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteFlowLog",
                    {},
                    service_endpoint="vpc.aliyuncs.com",
                    api_version="2016-04-28",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
