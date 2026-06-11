#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.alidns_gtm_instance_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: alidns_gtm_instance_info
short_description: Query Global Traffic Manager instances.
description:
  - Retrieve information about Alibaba Cloud Global Traffic Manager instances.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  instance_id:
    description: Filter by GTM instance ID.
    type: str
"""

EXAMPLES = r"""
- name: Query all GTM instances
  stevefulme1.alibaba_cloud.alidns_gtm_instance_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou

- name: Query specific GTM instance
  stevefulme1.alibaba_cloud.alidns_gtm_instance_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    instance_id: gtm-instance-id
"""

RETURN = r"""
alidns_gtm_instances:
  description: List of GTM instances.
  returned: success
  type: list
  elements: dict
  sample:
    - instance_id: gtm-123
      instance_name: my-gtm
      package_edition: standard
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

    try:
        result = client.get(
            "DescribeDnsGtmInstances",
            params,
            service_endpoint="alidns.aliyuncs.com",
            api_version="2015-01-09",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "GtmInstances".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, alidns_gtm_instances=data)


if __name__ == "__main__":
    main()
