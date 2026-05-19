#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.rds_parameter_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: rds_parameter_info
short_description: Query rds parameter resources.
description:
  - Retrieve information about Alibaba Cloud rds parameter resources.
  - This is a read-only module that does not modify any resources.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  db_instance_id:
    description: Filter by db instance id.
    type: str
  limit:
    description:
      - Maximum number of results to return.
    type: int
    default: 100
  offset:
    description:
      - Number of results to skip for pagination.
    type: int
    default: 0
"""

EXAMPLES = r"""
- name: List all rds parameter resources
  stevefulme1.alibaba_cloud.rds_parameter_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    db_instance_id: example-value
"""

RETURN = r"""
rds_parameters:
  description: List of rds parameter resources.
  returned: success
  type: list
  elements: dict
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
        limit=dict(type="int", default=100),
        offset=dict(type="int", default=0),
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
    if module.params.get("db_instance_id"):
        params["DBInstanceId"] = module.params["db_instance_id"]

    try:
        result = client.get(
            "DescribeParameters",
            params,
            service_endpoint="rds.aliyuncs.com",
            api_version="2014-08-15",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    data = result
    data = data.get("RunningParameters", {})
    data = data.get("DBInstanceParameter", {})
    if not isinstance(data, list):
        data = [data] if data else []

    module.exit_json(changed=False, rds_parameters=data)


if __name__ == "__main__":
    main()
