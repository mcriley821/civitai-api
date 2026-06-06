"""GET /models and GET /models/{id}."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from civitai_api._internal.resource import AsyncAPIResource, SyncAPIResource
from civitai_api.types.model import Model

if TYPE_CHECKING:
    from civitai_api._internal.pagination import AsyncPage, SyncPage
    from civitai_api.types.enums import BaseModel, CommercialUse, ModelSort, ModelType, Period


class Models(SyncAPIResource):
    """Sync resource for /models endpoints."""

    def list(
        self,
        *,
        limit: int | None = 5,
        page: int | None = None,
        query: str | None = None,
        tag: str | list[str] | None = None,
        username: str | None = None,
        types: ModelType | list[ModelType] | None = None,
        sort: ModelSort | None = None,
        period: Period | None = None,
        rating: int | None = None,
        favorites: bool | None = None,
        hidden: bool | None = None,
        primary_file_only: bool | None = None,
        allow_no_credit: bool | None = None,
        allow_derivatives: bool | None = None,
        allow_different_license: bool | None = None,
        allow_commercial_use: CommercialUse | list[CommercialUse] | None = None,
        nsfw: bool | None = None,
        poi: bool | None = None,
        base_models: BaseModel | list[BaseModel] | None = None,
        cursor: str | None = None,
    ) -> SyncPage[Model]:
        """Return a paginated list of models.

        :param limit: Maximum number of results per page, defaults to 5
        :type limit: int, optional
        :param page: Page number to fetch, defaults to None
        :type page: int, optional
        :param query: Search query string, defaults to None
        :type query: str, optional
        :param tag: Filter by tag name(s), defaults to None
        :type tag: str or list[str], optional
        :param username: Filter by creator username, defaults to None
        :type username: str, optional
        :param types: Filter by model type(s), defaults to None
        :type types: ModelType or list[ModelType], optional
        :param sort: Sort order, defaults to None
        :type sort: ModelSort, optional
        :param period: Time period for sort metric, defaults to None
        :type period: Period, optional
        :param rating: Minimum model rating, defaults to None
        :type rating: int, optional
        :param favorites: Return only favorited models (requires auth), defaults to None
        :type favorites: bool, optional
        :param hidden: Return only hidden models (requires auth), defaults to None
        :type hidden: bool, optional
        :param primary_file_only: Return only models with a primary file, defaults to None
        :type primary_file_only: bool, optional
        :param allow_no_credit: Filter by allowNoCredit license flag, defaults to None
        :type allow_no_credit: bool, optional
        :param allow_derivatives: Filter by allowDerivatives license flag, defaults to None
        :type allow_derivatives: bool, optional
        :param allow_different_license: Filter by allowDifferentLicense flag, defaults to None
        :type allow_different_license: bool, optional
        :param allow_commercial_use: Filter by commercial use permission(s), defaults to None
        :type allow_commercial_use: CommercialUse or list[CommercialUse], optional
        :param nsfw: Include (True) or exclude (False) NSFW models, defaults to None
        :type nsfw: bool, optional
        :param poi: Filter by person-of-interest flag, defaults to None
        :type poi: bool, optional
        :param base_models: Filter by base model architecture(s), defaults to None
        :type base_models: BaseModel or list[BaseModel], optional
        :param cursor: Pagination cursor from a previous response, defaults to None
        :type cursor: str, optional
        :return: First page of matching models
        :rtype: SyncPage[Model]
        """
        params: dict[str, Any] = {
            "limit": limit,
            "page": page,
            "query": query,
            "tag": tag,
            "username": username,
            "types": types,
            "sort": sort,
            "period": period,
            "rating": rating,
            "favorites": favorites,
            "hidden": hidden,
            "primaryFileOnly": primary_file_only,
            "allowNoCredit": allow_no_credit,
            "allowDerivatives": allow_derivatives,
            "allowDifferentLicense": allow_different_license,
            "allowCommercialUse": allow_commercial_use,
            "nsfw": nsfw,
            "poi": poi,
            "baseModels": base_models,
            "cursor": cursor,
        }
        return self._client.get_page("/models", params=params, item_type=Model)

    def retrieve(self, model_id: int) -> Model:
        """Return a single model by ID.

        :param model_id: Numeric model ID
        :type model_id: int
        :return: The requested model
        :rtype: Model
        :raises NotFoundError: If no model exists with the given ID
        """
        return self._client.get(f"/models/{model_id}", cast_to=Model)


class AsyncModels(AsyncAPIResource):
    """Async resource for /models endpoints."""

    async def list(
        self,
        *,
        limit: int | None = None,
        page: int | None = None,
        query: str | None = None,
        tag: str | list[str] | None = None,
        username: str | None = None,
        types: ModelType | list[ModelType] | None = None,
        sort: ModelSort | None = None,
        period: Period | None = None,
        rating: int | None = None,
        favorites: bool | None = None,
        hidden: bool | None = None,
        primary_file_only: bool | None = None,
        allow_no_credit: bool | None = None,
        allow_derivatives: bool | None = None,
        allow_different_license: bool | None = None,
        allow_commercial_use: CommercialUse | list[CommercialUse] | None = None,
        nsfw: bool | None = None,
        poi: bool | None = None,
        base_models: BaseModel | list[BaseModel] | None = None,
        cursor: str | None = None,
    ) -> AsyncPage[Model]:
        """Return a paginated list of models.

        :param limit: Maximum number of results per page, defaults to None
        :type limit: int, optional
        :param page: Page number to fetch, defaults to None
        :type page: int, optional
        :param query: Search query string, defaults to None
        :type query: str, optional
        :param tag: Filter by tag name(s), defaults to None
        :type tag: str or list[str], optional
        :param username: Filter by creator username, defaults to None
        :type username: str, optional
        :param types: Filter by model type(s), defaults to None
        :type types: ModelType or list[ModelType], optional
        :param sort: Sort order, defaults to None
        :type sort: ModelSort, optional
        :param period: Time period for sort metric, defaults to None
        :type period: Period, optional
        :param rating: Minimum model rating, defaults to None
        :type rating: int, optional
        :param favorites: Return only favorited models (requires auth), defaults to None
        :type favorites: bool, optional
        :param hidden: Return only hidden models (requires auth), defaults to None
        :type hidden: bool, optional
        :param primary_file_only: Return only models with a primary file, defaults to None
        :type primary_file_only: bool, optional
        :param allow_no_credit: Filter by allowNoCredit license flag, defaults to None
        :type allow_no_credit: bool, optional
        :param allow_derivatives: Filter by allowDerivatives license flag, defaults to None
        :type allow_derivatives: bool, optional
        :param allow_different_license: Filter by allowDifferentLicense flag, defaults to None
        :type allow_different_license: bool, optional
        :param allow_commercial_use: Filter by commercial use permission(s), defaults to None
        :type allow_commercial_use: CommercialUse or list[CommercialUse], optional
        :param nsfw: Include (True) or exclude (False) NSFW models, defaults to None
        :type nsfw: bool, optional
        :param poi: Filter by person-of-interest flag, defaults to None
        :type poi: bool, optional
        :param base_models: Filter by base model architecture(s), defaults to None
        :type base_models: BaseModel or list[BaseModel], optional
        :param cursor: Pagination cursor from a previous response, defaults to None
        :type cursor: str, optional
        :return: First page of matching models
        :rtype: AsyncPage[Model]
        """
        params: dict[str, Any] = {
            "limit": limit,
            "page": page,
            "query": query,
            "tag": tag,
            "username": username,
            "types": types,
            "sort": sort,
            "period": period,
            "rating": rating,
            "favorites": favorites,
            "hidden": hidden,
            "primaryFileOnly": primary_file_only,
            "allowNoCredit": allow_no_credit,
            "allowDerivatives": allow_derivatives,
            "allowDifferentLicense": allow_different_license,
            "allowCommercialUse": allow_commercial_use,
            "nsfw": nsfw,
            "poi": poi,
            "baseModels": base_models,
            "cursor": cursor,
        }
        return await self._client.get_page("/models", params=params, item_type=Model)

    async def retrieve(self, model_id: int) -> Model:
        """Return a single model by ID.

        :param model_id: Numeric model ID
        :type model_id: int
        :return: The requested model
        :rtype: Model
        :raises NotFoundError: If no model exists with the given ID
        """
        return await self._client.get(f"/models/{model_id}", cast_to=Model)
