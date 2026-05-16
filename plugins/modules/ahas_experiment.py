#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module: stevefulme1.alibaba_cloud.ahas_experiment"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ahas_experiment
short_description: Manage AHAS chaos engineering experiments.
description:
  - Create or delete manage ahas chaos engineering experiments.
  - Supports check mode and is idempotent.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.alibaba_cloud.alibaba_cloud
options:
  state:
    description: Desired state of the resource.
    type: str
    choices: ['present', 'absent']
    default: present
  experiment_id:
    description: Experiment ID.
    type: str
  experiment_name:
    description: Name of the experiment.
    type: str
  definition:
    description: JSON experiment definition.
    type: str"""

EXAMPLES = r"""
- name: Manage AHAS chaos engineering experiments.
  stevefulme1.alibaba_cloud.ahas_experiment:
    access_key_id: "{{ ak }}"
    access_key_secret: "{{ sk }}"
    region_id: cn-hangzhou
    state: present
"""

RETURN = r"""
ahas_experiment:
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
        experiment_id=dict(type="str"),
        experiment_name=dict(type="str"),
        definition=dict(type="str"),
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
            "ListExperiments",
            {},
            service_endpoint="ahas.aliyuncs.com",
            api_version="2019-09-01",
        )

        data = existing
        for key in "Experiments".split("."):
            data = data.get(key, {})
        if not isinstance(data, list):
            data = []

        if state == "present":
            if not data:
                if module.check_mode:
                    module.exit_json(changed=True)
                result = client.get(
                    "CreateExperiment",
                    {},
                    service_endpoint="ahas.aliyuncs.com",
                    api_version="2019-09-01",
                )
                changed = True
                module.exit_json(changed=changed, ahas_experiment=result)
            else:
                module.exit_json(changed=False, ahas_experiment=data[0])

        else:
            if data:
                if module.check_mode:
                    module.exit_json(changed=True)
                client.get(
                    "DeleteExperiment",
                    {},
                    service_endpoint="ahas.aliyuncs.com",
                    api_version="2019-09-01",
                )
                changed = True
            module.exit_json(changed=changed)

    except AlibabaCloudError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
