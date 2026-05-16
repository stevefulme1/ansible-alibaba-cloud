#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.privatelink_endpoint"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: privatelink_endpoint
short_description: Manage PrivateLink VPC endpoints.
description:
  - Create, update, or delete Alibaba Cloud privatelink_endpoint resources.
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
  endpoint_name:
    description: Name of the VPC endpoint.
    type: str
  endpoint_id:
    description: ID of an existing endpoint.
    type: str
  service_id:
    description: Endpoint service ID to connect to.
    type: str
  vpc_id:
    description: VPC ID for the endpoint.
    type: str
"""

EXAMPLES = r"""
- name: Manage privatelink_endpoint resource
  stevefulme1.alibaba_cloud.privatelink_endpoint:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    endpoint_name: my-privatelink
    service_id: epsrv-xxxxx
    vpc_id: vpc-xxxxx
"""

RETURN = r"""
privatelink_endpoint:
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
        endpoint_name=dict(type="str"),
        endpoint_id=dict(type="str"),
        service_id=dict(type="str"),
        vpc_id=dict(type="str"),
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
            "ListVpcEndpoints",
            {},
            service_endpoint="privatelink.aliyuncs.com",
            api_version="2020-04-15",
        )

        data = existing
        for key in "Endpoints".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateVpcEndpoint",
                    {},
                    service_endpoint="privatelink.aliyuncs.com",
                    api_version="2020-04-15",
                )
                changed = True
                module.exit_json(changed=changed, privatelink_endpoint=result)
            else:
                module.exit_json(changed=False, privatelink_endpoint=data[0])
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteVpcEndpoints",
                    {},
                    service_endpoint="privatelink.aliyuncs.com",
                    api_version="2020-04-15",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
