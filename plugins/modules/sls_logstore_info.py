#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.sls_logstore_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: sls_logstore_info
short_description: Query Log Service logstores.
description:
  - Retrieve information about Alibaba Cloud Log Service logstores.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  project_name:
    description: Log Service project name.
    type: str
    required: true
  logstore_name:
    description: Filter by logstore name.
    type: str
"""

EXAMPLES = r"""
- name: Query all logstores in a project
  stevefulme1.alibaba_cloud.sls_logstore_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    project_name: my-sls-project

- name: Query specific logstore
  stevefulme1.alibaba_cloud.sls_logstore_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    project_name: my-sls-project
    logstore_name: app-logs
"""

RETURN = r"""
sls_logstores:
  description: List of Log Service logstores.
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
        project_name=dict(type="str", required=True),
        logstore_name=dict(type="str"),
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
        "ProjectName": module.params["project_name"],
    }
    if module.params.get("logstore_name"):
        params["LogstoreName"] = module.params["logstore_name"]

    try:
        result = client.get(
            "GetLogStore",
            params,
            service_endpoint="sls.aliyuncs.com",
            api_version="2020-12-30",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    # Navigate dotted list_key to extract the list.
    data = result
    for key in "logstore".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, sls_logstores=data)


if __name__ == "__main__":
    main()
