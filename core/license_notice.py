# =====================================================================
# HONEYPOT ANALYTICS — Proprietary Software
# Copyright (c) 2026 Daniel Oladipupo. All Rights Reserved.
#
# This source code and all accompanying files are the confidential and
# proprietary property of Daniel Oladipupo ("the Owner"). No person or
# entity - including any developer, contractor, or agency engaged to
# work on this codebase - may copy, modify, merge, publish, sublicense,
# reverse engineer, or distribute this software, in whole or in part,
# without the Owner's prior express written permission.
#
# Any modification performed on behalf of the Owner must preserve this
# notice and the version/integrity markers below unmodified. Removing,
# obscuring, or altering this notice does not waive the copyright or
# license restriction - it is itself a violation of them.
# =====================================================================

__copyright__ = "Copyright (c) 2026 Daniel Oladipupo. All Rights Reserved."
__license__ = "Proprietary - All Rights Reserved. Unauthorized use, modification, or redistribution prohibited."
__owner__ = "Daniel Oladipupo"
__product__ = "Honeypot Analytics"

LICENSE_NOTICE = __copyright__ + " " + __license__


def print_license_notice():
    """Small helper any entry point can call to surface the notice at runtime."""
    print(f"{__product__} — {LICENSE_NOTICE}")
