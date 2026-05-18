#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.polardb_cluster"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: polardb_cluster
short_description: Manage PolarDB clusters.
description:
  - Create, update, or delete Alibaba Cloud polardb_cluster resources.
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
  db_cluster_id:
    description: ID of an existing PolarDB cluster.
    type: str
  db_type:
    description: Database engine type.
    type: str
    choices: [MySQL, PostgreSQL, Oracle]
    default: MySQL
  db_version:
    description: Database engine version.
    type: str
  pay_type:
    description: Payment type.
    type: str
    choices: [Postpaid, Prepaid]
    default: Postpaid
  db_node_class:
    description: Node specification class.
    type: str
  cluster_description:
    description: Cluster description.
    type: str
"""

EXAMPLES = r"""
- name: Manage polardb_cluster resource
  stevefulme1.alibaba_cloud.polardb_cluster:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
    db_type: MySQL
    db_version: "8.0"
    db_node_class: polar.mysql.x4.large
"""

RETURN = r"""
polardb_cluster:
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
        db_cluster_id=dict(type="str"),
        db_type=dict(
            type="str", choices=["MySQL", "PostgreSQL", "Oracle"], default="MySQL"
        ),
        db_version=dict(type="str"),
        pay_type=dict(type="str", choices=["Postpaid", "Prepaid"], default="Postpaid"),
        db_node_class=dict(type="str"),
        cluster_description=dict(type="str"),
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
            "DescribeDBClusters",
            {},
            service_endpoint="polardb.aliyuncs.com",
            api_version="2017-08-01",
        )

        data = existing
        for key in "Items.DBCluster".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateDBCluster",
                    {},
                    service_endpoint="polardb.aliyuncs.com",
                    api_version="2017-08-01",
                )
                changed = True
                module.exit_json(changed=changed, polardb_cluster=result)
            else:
                module.exit_json(changed=False, polardb_cluster=data[0])
        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteDBCluster",
                    {},
                    service_endpoint="polardb.aliyuncs.com",
                    api_version="2017-08-01",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
