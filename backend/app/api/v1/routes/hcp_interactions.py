from uuid import UUID

from fastapi import APIRouter, Query, Response, status

from app.api.deps import HcpInteractionServiceDep
from app.domains.hcp.schemas.interaction import (
    HcpInteractionCreate,
    HcpInteractionListResponse,
    HcpInteractionResponse,
    HcpInteractionUpdate,
    InteractionSentiment,
)

router = APIRouter()


@router.post(
    "",
    response_model=HcpInteractionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_hcp_interaction(
    payload: HcpInteractionCreate,
    service: HcpInteractionServiceDep,
) -> HcpInteractionResponse:
    return service.create_interaction(payload)


@router.get("", response_model=HcpInteractionListResponse)
def list_hcp_interactions(
    service: HcpInteractionServiceDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    hcp_name: str | None = Query(default=None, min_length=1, max_length=255),
    sentiment: InteractionSentiment | None = Query(default=None),
) -> HcpInteractionListResponse:
    items, total = service.list_interactions(
        limit=limit,
        offset=offset,
        hcp_name=hcp_name,
        sentiment=sentiment.value if sentiment else None,
    )
    return HcpInteractionListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{interaction_id}", response_model=HcpInteractionResponse)
def get_hcp_interaction(
    interaction_id: UUID,
    service: HcpInteractionServiceDep,
) -> HcpInteractionResponse:
    return service.get_interaction(interaction_id)


@router.patch("/{interaction_id}", response_model=HcpInteractionResponse)
def update_hcp_interaction(
    interaction_id: UUID,
    payload: HcpInteractionUpdate,
    service: HcpInteractionServiceDep,
) -> HcpInteractionResponse:
    return service.update_interaction(interaction_id, payload)


@router.delete("/{interaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hcp_interaction(
    interaction_id: UUID,
    service: HcpInteractionServiceDep,
) -> Response:
    service.delete_interaction(interaction_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

