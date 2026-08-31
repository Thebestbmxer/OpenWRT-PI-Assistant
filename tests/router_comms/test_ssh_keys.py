"""Tests for controller SSH key management."""

from pathlib import Path

import paramiko
import pytest

from router_controller.router_comms.ssh.keys import (
    SSHKeyManager,
    SSHKeyPair,
)


def test_generates_rsa_key_pair(tmp_path: Path):
    manager = SSHKeyManager(tmp_path)

    key_pair = manager.generate_key_pair()

    assert isinstance(key_pair, SSHKeyPair)
    assert key_pair.private_key_path == tmp_path / "controller"
    assert key_pair.public_key_path == tmp_path / "controller.pub"

    assert key_pair.private_key_path.exists()
    assert key_pair.public_key_path.exists()

    assert key_pair.public_key.startswith("ssh-rsa ")


def test_private_key_has_restrictive_permissions(tmp_path: Path):
    manager = SSHKeyManager(tmp_path)

    key_pair = manager.generate_key_pair()

    mode = key_pair.private_key_path.stat().st_mode & 0o777

    assert mode == 0o600


def test_public_key_has_readable_permissions(tmp_path: Path):
    manager = SSHKeyManager(tmp_path)

    key_pair = manager.generate_key_pair()

    mode = key_pair.public_key_path.stat().st_mode & 0o777

    assert mode == 0o644


def test_generated_private_key_can_be_loaded_by_paramiko(
    tmp_path: Path,
):
    manager = SSHKeyManager(tmp_path)

    key_pair = manager.generate_key_pair()

    key = paramiko.RSAKey.from_private_key_file(
        str(key_pair.private_key_path)
    )

    assert key.get_name() == "ssh-rsa"
    assert key.get_base64() in key_pair.public_key


def test_public_key_matches_private_key(tmp_path: Path):
    manager = SSHKeyManager(tmp_path)

    key_pair = manager.generate_key_pair()

    loaded = manager.load_key_pair()

    assert loaded == key_pair


def test_existing_key_pair_is_not_overwritten(tmp_path: Path):
    manager = SSHKeyManager(tmp_path)

    original = manager.generate_key_pair()

    with pytest.raises(FileExistsError):
        manager.generate_key_pair()

    loaded = manager.load_key_pair()

    assert loaded == original


def test_load_fails_when_public_key_does_not_match(
    tmp_path: Path,
):
    manager = SSHKeyManager(tmp_path)

    manager.generate_key_pair()

    (tmp_path / "controller.pub").write_text(
        "ssh-rsa invalid-key\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="does not match"):
        manager.load_key_pair()