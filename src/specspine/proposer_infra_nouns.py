from __future__ import annotations

from ._nouns_build_deploy import TARGET_NOUNS_BUILD_DEPLOY
from ._nouns_identity_org import TARGET_NOUNS_IDENTITY_ORG
from ._nouns_data_network import TARGET_NOUNS_DATA_NETWORK

__all__ = [
    "TARGET_NOUNS_INFRA",
]

TARGET_NOUNS_INFRA = (
    *TARGET_NOUNS_BUILD_DEPLOY,
    *TARGET_NOUNS_IDENTITY_ORG,
    *TARGET_NOUNS_DATA_NETWORK,
)
