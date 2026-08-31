"""Exceptions raised by the router communication subsystem."""


class RouterCommsError(Exception):
    """Base exception for router communication errors."""


class RouterNotFoundError(RouterCommsError):
    """Raised when no suitable router can be discovered."""


class DiscoveryError(RouterCommsError):
    """Raised when router discovery fails."""


class InitialCommunicationError(RouterCommsError):
    """Raised when initial router communication fails."""


class AuthenticationError(RouterCommsError):
    """Raised when router authentication fails."""


class SSHConnectionError(RouterCommsError):
    """Raised when an SSH connection cannot be established."""


class SSHCommandError(RouterCommsError):
    """Raised when an SSH command cannot be executed successfully."""


class SSHKeyError(RouterCommsError):
    """Raised when SSH key setup or management fails."""


class HostKeyError(RouterCommsError):
    """Raised when the router host key cannot be verified."""


class RouterProbeError(RouterCommsError):
    """Raised when the read-only router probe fails."""