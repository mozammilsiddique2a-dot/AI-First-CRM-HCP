from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.db.repositories.hcp_interaction_repository import HcpInteractionRepository
from app.domains.hcp.services.interaction_service import HcpInteractionService

DbSession = Annotated[Session, Depends(get_db_session)]


def get_hcp_interaction_repository(
    db: DbSession,
) -> HcpInteractionRepository:
    return HcpInteractionRepository(db)


HcpInteractionRepositoryDep = Annotated[
    HcpInteractionRepository,
    Depends(get_hcp_interaction_repository),
]


def get_hcp_interaction_service(
    repository: HcpInteractionRepositoryDep,
) -> HcpInteractionService:
    return HcpInteractionService(repository)


HcpInteractionServiceDep = Annotated[
    HcpInteractionService,
    Depends(get_hcp_interaction_service),
]
