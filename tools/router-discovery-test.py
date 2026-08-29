#!/usr/bin/env python3
"""Physical router discovery test.

This tool performs a read-only discovery scan from the Raspberry Pi.
It does not authenticate with or modify any router.
"""

from openwrt_controller.router_comms.discovery.router_discovery import (
    RouterDiscovery,
)


def main() -> int:
    print("OpenWrt Pi Controller - Router Discovery Test")
    print()
    print("Scanning local networks for SSH-accessible devices...")
    print()

    discovery = RouterDiscovery()

    try:
        candidate = discovery.discover()
    except Exception as exc:
        print(f"Discovery: FAIL")
        print(f"Reason: {exc}")
        return 1

    print("Discovery: PASS")
    print()
    print("Router candidate:")
    print(f"  Address:  {candidate.address}")
    print(f"  SSH port: {candidate.ssh_port}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
