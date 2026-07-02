from __future__ import annotations

from abc import ABC, abstractmethod

from .models import VehicleState


class OBDAdapter(ABC):
    """Minimal interface for an OBD-II data source."""

    @abstractmethod
    def connect(self) -> None:
        """Open the adapter connection."""

    @abstractmethod
    def disconnect(self) -> None:
        """Close the adapter connection."""

    @abstractmethod
    def read_state(self) -> VehicleState:
        """Read a snapshot of vehicle telemetry."""

    def read_dtc(self) -> list[str]:
        """Read diagnostic trouble codes if supported."""
        return []

    def clear_dtc(self) -> None:
        """Clear diagnostic trouble codes if supported."""
        raise NotImplementedError("Clearing DTCs is not implemented for this adapter")
