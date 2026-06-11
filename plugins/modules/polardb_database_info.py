#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.polardb_database_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: polardb_database_info
short_description: Query PolarDB databases.
description:
  - Retrieve information about Alibaba Cloud PolarDB databases.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  db_cluster_id:
    description: PolarDB cluster ID.
    type: str
    required: true
  db_name:
    description: Filter by database name.
    type: str
"""

EXAMPLES = r"""
- name: Query all PolarDB databases in a cluster
  stevefulme1.alibaba_cloud.polardb_database_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    db_cluster_id: pc-xxxxx

- name: Query specific PolarDB database
  stevefulme1.alibaba_cloud.polardb_database_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    db_cluster_id: pc-xxxxx
    db_name: app_production
"""

RETURN = r"""
polardb_databases:
  description: List of PolarDB databases.
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
        db_cluster_id=dict(type="str", required=True),
        db_name=dict(type="str"),
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

    params = {
        "DBClusterId": module.params["db_cluster_id"],
    }
    if module.params.get("db_name"):
        params["DBName"] = module.params["db_name"]

    try:
        result = client.get(
            "DescribeDatabases",
            params,
            service_endpoint="polardb.aliyuncs.com",
            api_version="2017-08-01",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "Databases.Database".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, polardb_databases=data)


if __name__ == "__main__":
    main()
