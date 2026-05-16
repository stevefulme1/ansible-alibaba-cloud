#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Shared documentation fragment for Alibaba Cloud modules."""

from __future__ import annotations


class ModuleDocFragment:
    """Documentation fragment for Alibaba Cloud connection parameters."""

    DOCUMENTATION = r"""
options:
  access_key_id:
    description:
      - Alibaba Cloud access key ID.
      - Can also be set via the C(ALIBABA_CLOUD_ACCESS_KEY_ID)
        environment variable.
    type: str
    required: true
  access_key_secret:
    description:
      - Alibaba Cloud access key secret.
      - Can also be set via the C(ALIBABA_CLOUD_ACCESS_KEY_SECRET)
        environment variable.
    type: str
    required: true
  region_id:
    description:
      - The Alibaba Cloud region to operate in,
        for example C(cn-hangzhou) or C(us-east-1).
      - Can also be set via the C(ALIBABA_CLOUD_REGION)
        environment variable.
    type: str
    required: true
  security_token:
    description:
      - Security token for STS-based temporary credentials.
      - Can also be set via the C(ALIBABA_CLOUD_SECURITY_TOKEN)
        environment variable.
    type: str
  timeout:
    description:
      - HTTP request timeout in seconds.
    type: int
    default: 60
"""
