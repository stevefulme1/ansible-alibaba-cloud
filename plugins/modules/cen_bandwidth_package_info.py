#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.cen_bandwidth_package_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: cen_bandwidth_package_info
short_description: Query CEN bandwidth packages.
description:
  - Retrieve information about Alibaba Cloud CEN bandwidth packages.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  cen_bandwidth_package_id:
    description: Filter by bandwidth package ID.
    type: str
"""

EXAMPLES = r"""
- name: Query all CEN bandwidth packages
  stevefulme1.alibaba_cloud.cen_bandwidth_package_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou

- name: Query specific CEN bandwidth package
  stevefulme1.alibaba_cloud.cen_bandwidth_package_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    cen_bandwidth_package_id: cbwp-123
"""

RETURN = r"""
cen_bandwidth_packages:
  description: List of CEN bandwidth packages.
  returned: success
  type: list
  elements: dict
  sample:
    - cen_bandwidth_package_id: cbwp-123
      bandwidth: 100
      geographic_region_a_id: China
      geographic_region_b_id: Asia-Pacific
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        cen_bandwidth_package_id=dict(type="str"),
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
    if module.params.get("cen_bandwidth_package_id"):
        params["CenBandwidthPackageId"] = module.params["cen_bandwidth_package_id"]

    try:
        result = client.get(
            "DescribeCenBandwidthPackages",
            params,
            service_endpoint="cbn.aliyuncs.com",
            api_version="2017-09-12",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "CenBandwidthPackages.CenBandwidthPackage".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, cen_bandwidth_packages=data)


if __name__ == "__main__":
    main()
