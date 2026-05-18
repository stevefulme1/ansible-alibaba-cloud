#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.dms_database_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: dms_database_info
short_description: Query DMS managed databases.
description:
  - Retrieve information about Alibaba Cloud DMS database resources.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  instance_id:
    description: Filter databases by DMS instance ID.
    type: str
  search_key:
    description: Search keyword for databases.
    type: str
"""

EXAMPLES = r"""
- name: List all DMS databases
  stevefulme1.alibaba_cloud.dms_database_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    instance_id: example-value
    search_key: example-value
"""

RETURN = r"""
dms_databases:
  description: List of DMS databases.
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
        instance_id=dict(type="str"),
        search_key=dict(type="str", no_log=False),
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
    try:
        result = client.get(
            "ListDatabases",
            params,
            service_endpoint="dms-enterprise.aliyuncs.com",
            api_version="2018-11-01",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    data = result
    for key in "Databases.Database".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, dms_databases=data)


if __name__ == "__main__":
    main()
