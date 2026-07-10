from __future__ import annotations

import logging
from datetime import date
from uuid import UUID

from sqlalchemy import Select, cast, func, or_, select
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.orm import Session

from app.domains.hcp.models.interaction import HcpInteraction
from app.domains.hcp.schemas.interaction import HcpInteractionCreate, HcpInteractionUpdate

logger = logging.getLogger(__name__)


class HcpInteractionRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, payload: HcpInteractionCreate) -> HcpInteraction:
        interaction = HcpInteraction(**payload.model_dump())
        self._db.add(interaction)
        self._db.commit()
        self._db.refresh(interaction)
        return interaction

    def list(
        self,
        *,
        limit: int,
        offset: int,
        hcp_name: str | None = None,
        sentiment: str | None = None,
    ) -> tuple[list[HcpInteraction], int]:
        query = self._base_filtered_query(hcp_name=hcp_name, sentiment=sentiment)
        count_query = select(func.count()).select_from(query.subquery())
        total = self._db.scalar(count_query) or 0

        items = self._db.scalars(
            query.order_by(HcpInteraction.created_at.desc()).limit(limit).offset(offset)
        ).all()
        return list(items), total

    def get_by_id(self, interaction_id: UUID) -> HcpInteraction | None:
        return self._db.get(HcpInteraction, interaction_id)

    def search(
        self,
        *,
        limit: int,
        hcp_name: str | None = None,
        interaction_date: date | None = None,
        product: str | None = None,
        interaction_type: str | None = None,
    ) -> list[HcpInteraction]:
        query = select(HcpInteraction)

        if hcp_name:
            query = query.where(HcpInteraction.hcp_name.ilike(f"%{hcp_name}%"))

        if interaction_date:
            query = query.where(HcpInteraction.interaction_date == interaction_date)

        if interaction_type:
            query = query.where(HcpInteraction.interaction_type == interaction_type)

        if product:
            product_pattern = f"%{product}%"
            query = query.where(
                or_(
                    HcpInteraction.topics_discussed.ilike(product_pattern),
                    HcpInteraction.summary.ilike(product_pattern),
                    HcpInteraction.outcomes.ilike(product_pattern),
                    cast(HcpInteraction.materials_shared, TEXT).ilike(product_pattern),
                    cast(HcpInteraction.samples_distributed, TEXT).ilike(product_pattern),
                )
            )

        return list(
            self._db.scalars(query.order_by(HcpInteraction.created_at.desc()).limit(limit)).all()
        )

    def update(
        self,
        interaction: HcpInteraction,
        payload: HcpInteractionUpdate,
    ) -> HcpInteraction:
        update_data = payload.model_dump(exclude_unset=True)
        logger.info(
            "Updating HCP interaction id=%s with update_data=%s",
            interaction.id,
            update_data,
        )

        for field, value in update_data.items():
            setattr(interaction, field, value)

        self._db.add(interaction)
        logger.info("Committing HCP interaction update id=%s", interaction.id)
        self._db.commit()
        logger.info("Refreshing HCP interaction after update id=%s", interaction.id)
        self._db.refresh(interaction)
        return interaction

    def delete(self, interaction: HcpInteraction) -> None:
        self._db.delete(interaction)
        self._db.commit()

    @staticmethod
    def _base_filtered_query(
        *,
        hcp_name: str | None,
        sentiment: str | None,
    ) -> Select[tuple[HcpInteraction]]:
        query = select(HcpInteraction)

        if hcp_name:
            query = query.where(HcpInteraction.hcp_name.ilike(f"%{hcp_name}%"))

        if sentiment:
            query = query.where(HcpInteraction.sentiment == sentiment)

        return query
