#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.bastionhost_host_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: bastionhost_host_info
short_description: Query Bastion Host managed hosts.
description:
  - Retrieve information about hosts managed by Alibaba Cloud Bastion Host.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  instance_id:
    description: Bastion Host instance ID.
    type: str
  host_id:
    description: Filter by host ID.
    type: str
  host_name:
    description: Filter by host name.
    type: str
"""

EXAMPLES = r"""
- name: Query all Bastion Host managed hosts
  stevefulme1.alibaba_cloud.bastionhost_host_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    instance_id: bastionhost-123

- name: Query specific host
  stevefulme1.alibaba_cloud.bastionhost_host_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    instance_id: bastionhost-123
    host_id: host-456
"""

RETURN = r"""
bastionhost_hosts:
  description: List of Bastion Host managed hosts.
  returned: success
  type: list
  elements: dict
  sample:
    - host_id: host-123
      host_name: web-server-01
      host_private_address: 192.168.1.100
      os_type: Linux
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        instance_id=dict(type="str"),
        host_id=dict(type="str"),
        host_name=dict(type="str"),
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

    params = {}
    if module.params.get("instance_id"):
        params["InstanceId"] = module.params["instance_id"]
    if module.params.get("host_id"):
        params["HostId"] = module.params["host_id"]
    if module.params.get("host_name"):
        params["HostName"] = module.params["host_name"]

    try:
        result = client.get(
            "ListHosts",
            params,
            service_endpoint="yundun-bastionhost.aliyuncs.com",
            api_version="2019-12-09",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "Hosts".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, bastionhost_hosts=data)


if __name__ == "__main__":
    main()
