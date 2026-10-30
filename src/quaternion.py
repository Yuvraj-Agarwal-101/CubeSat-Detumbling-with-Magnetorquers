"""Public compatibility imports for the attitude utility module."""

from .physics.quaternion import (
    conjugate, inverse, multiply, normalize, quaternion_derivative, rotation_matrix,
)

__all__ = ["conjugate", "inverse", "multiply", "normalize", "quaternion_derivative", "rotation_matrix"]
