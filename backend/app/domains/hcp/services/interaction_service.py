from uuid import UUID
from datetime import date

from app.db.repositories.hcp_interaction_repository import HcpInteractionRepository
from app.domains.hcp.models.interaction import HcpInteraction
from app.domains.hcp.schemas.interaction import HcpInteractionCreate, HcpInteractionUpdate
from app.shared.exceptions import ResourceNotFoundError


class HcpInteractionService:
    def __init__(self, repository: HcpInteractionRepository) -> None:
        self._repository = repository

    def create_interaction(self, payload: HcpInteractionCreate) -> HcpInteraction:
        return self._repository.create(payload)

    def list_interactions(
        self,
        *,
        limit: int,
        offset: int,
        hcp_name: str | None,
        sentiment: str | None,
    ) -> tuple[list[HcpInteraction], int]:
        return self._repository.list(
            limit=limit,
            offset=offset,
            hcp_name=hcp_name,
            sentiment=sentiment,
        )

    def get_interaction(self, interaction_id: UUID) -> HcpInteraction:
        interaction = self._repository.get_by_id(interaction_id)
        if interaction is None:
            raise ResourceNotFoundError("HCP interaction was not found.")
        return interaction

    def update_interaction(
        self,
        interaction_id: UUID,
        payload: HcpInteractionUpdate,
    ) -> HcpInteraction:
        interaction = self.get_interaction(interaction_id)
        return self._repository.update(interaction, payload)

    def search_interactions(
        self,
        *,
        limit: int = 10,
        hcp_name: str | None = None,
        interaction_date: date | None = None,
        product: str | None = None,
        interaction_type: str | None = None,
    ) -> list[HcpInteraction]:
        return self._repository.search(
            limit=limit,
            hcp_name=hcp_name,
            interaction_date=interaction_date,
            product=product,
            interaction_type=interaction_type,
        )

    def delete_interaction(self, interaction_id: UUID) -> None:
        interaction = self.get_interaction(interaction_id)
        self._repository.delete(interaction)
