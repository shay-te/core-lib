"""Shared hypothesis settings used across all property-based test files."""
from hypothesis import HealthCheck, settings


SETTINGS = settings(
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much],
    deadline=None,
)
