"""
config = DockerInfrastructureConfig()
return DockerHealthChecker(config)


# ============================================================================
# Export all classes and functions
# ============================================================================

__all__ = [
    # Configuration""
"DockerInfrastructureConfig",

    # Service discovery""
"ServiceDiscovery",

    # Health checking""
"DockerHealthChecker",

    # Factory functions""
"create_docker_config",""
"create_service_discovery",""
"create_health_checker",
]
"""
