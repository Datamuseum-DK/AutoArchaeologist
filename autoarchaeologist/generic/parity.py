#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

PARITY = bytes([bin(x).count('1') & 1 for x in range(256)])
