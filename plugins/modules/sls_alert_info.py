#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.sls_alert_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: sls_alert_info
short_description: Query SLS alert rules.
description:
  - Retrieve information about Alibaba Cloud SLS alert resources.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  project_name:
    description: Log Service project name.
    type: str
  alert_name:
    description: Filter by alert rule name.
    type: str
"""

EXAMPLES = r"""
- name: List all SLS alerts
  stevefulme1.alibaba_cloud.sls_alert_info:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    project_name: example-value
    alert_name: example-value
"""

RETURN = r"""
sls_alerts:
  description: List of SLS alerts.
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
        project_name=dict(type="str"),
        alert_name=dict(type="str"),
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
            "ListAlerts",
            params,
            service_endpoint="sls.{region_id}.aliyuncs.com",
            api_version="2020-12-30",
        )
    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))

    data = result
    for key in "Alerts.Alert".split("."):
        data = data.get(key, {})
    if not isinstance(data, list):
        data = []

    module.exit_json(changed=False, sls_alerts=data)


if __name__ == "__main__":
    main()
