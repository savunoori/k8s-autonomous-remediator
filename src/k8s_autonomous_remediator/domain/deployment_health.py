from dataclasses import dataclass
from enum import Enum


class DeploymentHealthStatus(str,Enum):
    HEALTHY= "healthy"
    DEGRADED= "degraded"
    UNAVAILABLE= "unavailable"
    SCALED_DOWN = "scaled_down"
    UNKNOWN = "unknown"

@dataclass(frozen=True, slots=True)
class DeploymentHealth:
    name:str
    namespace:str
    desired_replicas: int
    ready_replicas: int
    available_replicas: int

    @property
    def status(self) -> DeploymentHealthStatus:
        desired = self.desired_replicas
        ready = self.ready_replicas
        available = self.available_replicas

        if any(
            value is None or value < 0
            for value in (desired, ready, available)
        ):
             return DeploymentHealthStatus.UNKNOWN

        if ready > desired or available > ready:
            return DeploymentHealthStatus.UNKNOWN
        
        if desired == 0:
            return DeploymentHealthStatus.SCALED_DOWN
        
        if ready == desired and available == desired:
            return DeploymentHealthStatus.HEALTHY

        if ready == 0:
            return DeploymentHealthStatus.UNAVAILABLE

        return DeploymentHealthStatus.DEGRADED