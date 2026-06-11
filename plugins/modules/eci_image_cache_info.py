#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.eci_image_cache_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: eci_image_cache_info
short_description: Query ECI image caches.
description:
  - Retrieve information about Alibaba Cloud Elastic Container Instance image caches.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  image_cache_id:
    description: Filter by image cache ID.
    type: str
  image_cache_name:
    description: Filter by image cache name.
    type: str
"""

EXAMPLES = r"""
- name: Query all ECI image caches
  stevefulme1.alibaba_cloud.eci_image_cache_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou

- name: Query specific ECI image cache
  stevefulme1.alibaba_cloud.eci_image_cache_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    image_cache_id: imc-123
"""

RETURN = r"""
eci_image_caches:
  description: List of ECI image caches.
  returned: success
  type: list
  elements: dict
  sample:
    - image_cache_id: imc-123
      image_cache_name: nginx-cache
      images:
        - nginx:latest
      snapshot_id: s-123
      status: Ready
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.alibaba_cloud.plugins.module_utils.alibaba_cloud import (
    AlibabaCloudClient,
    AlibabaCloudError,
    alibaba_argument_spec,
)


def main():
    spec = dict(
        image_cache_id=dict(type="str"),
        image_cache_name=dict(type="str"),
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
    if module.params.get("image_cache_id"):
        params["ImageCacheId"] = module.params["image_cache_id"]
    if module.params.get("image_cache_name"):
        params["ImageCacheName"] = module.params["image_cache_name"]

    try:
        result = client.get(
            "DescribeImageCaches",
            params,
            service_endpoint="eci.aliyuncs.com",
            api_version="2018-08-08",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "ImageCaches".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, eci_image_caches=data)


if __name__ == "__main__":
    main()
