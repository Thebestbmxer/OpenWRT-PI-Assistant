#!/usr/bin/env python3
"""Physical router discovery and bootstrap test.

This tool discovers a router on the local network and verifies that
initial SSH authentication succeeds. It does not execute commands or
modify the router.
"""

from openwrt_controller.router_comms.discovery.bootstrap import (
    RouterBootstrap,
    )
from openwrt_controller.router_comms.discovery.router_discovery import (
    RouterDiscovery,
    )
from openwrt_controller.router_comms.exceptions import (
    AuthenticationError,
    InitialCommunicationError,
    )

def main() -> int:
    print("OpenWrt Pi Controller - Router Bootstrap Test")
    print()
    print("Scanning local networks for SSH-accessible devices...")
    print()

    discovery = RouterDiscovery()

    try:
        candidate = discovery.discover()
    except Exception as exc:
        print("Discovery: FAIL")
        print(f"Reason: {exc}")
        return 1

    print("Discovery: PASS")
    print()
    print("Router candidate:")
    print(f"  Address:  {candidate.address}")
    print(f"  SSH port: {candidate.ssh_port}")
    print()
    print("Attempting bootstrap authentication...")
    print()

    bootstrap = RouterBootstrap(candidate)

    try:
        client, credentials = bootstrap.connect()
    except AuthenticationError as exc:
        print("Bootstrap: FAIL")
        print(f"Reason: {exc}")
        return 1
    except InitialCommunicationError as exc:
        print("Bootstrap: FAIL")
        print(f"Reason: {exc}")
        return 1

    try:
        print("Bootstrap: PASS")
        print()
        print("Credentials accepted:")
        print(f"  Username: {credentials.username}")
        print(f"  Password: {'<blank>' if credentials.password == '' else '<configured>'}")
    finally:
        client.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())