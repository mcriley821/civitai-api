"""GET /images."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from civitai_api._internal.resource import AsyncAPIResource, SyncAPIResource
from civitai_api.types.image import Image

if TYPE_CHECKING:
    from civitai_api._internal.pagination import AsyncPage, SyncPage
    from civitai_api.types.enums import ImageSort, NsfwLevel, Period


class Images(SyncAPIResource):
    """Sync resource for /images endpoints."""

    def list(
        self,
        *,
        limit: int | None = None,
        post_id: int | None = None,
        model_id: int | None = None,
        model_version_id: int | None = None,
        username: str | None = None,
        nsfw: NsfwLevel | bool | None = None,
        sort: ImageSort | None = None,
        period: Period | None = None,
        page: int | None = None,
        cursor: str | None = None,
    ) -> SyncPage[Image]:
        """Return a paginated list of images.

        :param limit: Maximum number of results per page, defaults to None
        :type limit: int, optional
        :param post_id: Filter to images from a specific post, defaults to None
        :type post_id: int, optional
        :param model_id: Filter to images associated with a model, defaults to None
        :type model_id: int, optional
        :param model_version_id: Filter to images for a specific model version, defaults to None
        :type model_version_id: int, optional
        :param username: Filter to images uploaded by a specific user, defaults to None
        :type username: str, optional
        :param nsfw: NSFW level filter or boolean toggle, defaults to None
        :type nsfw: NsfwLevel or bool, optional
        :param sort: Sort order, defaults to None
        :type sort: ImageSort, optional
        :param period: Time period for sort metric, defaults to None
        :type period: Period, optional
        :param page: Page number to fetch, defaults to None
        :type page: int, optional
        :param cursor: Pagination cursor from a previous response, defaults to None
        :type cursor: str, optional
        :return: First page of matching images
        :rtype: SyncPage[Image]
        """
        params: dict[str, Any] = {
            "limit": limit,
            "postId": post_id,
            "modelId": model_id,
            "modelVersionId": model_version_id,
            "username": username,
            "nsfw": nsfw,
            "sort": sort,
            "period": period,
            "page": page,
            "cursor": cursor,
        }
        return self._client.get_page("/images", params=params, item_type=Image)


class AsyncImages(AsyncAPIResource):
    """Async resource for /images endpoints."""

    async def list(
        self,
        *,
        limit: int | None = None,
        post_id: int | None = None,
        model_id: int | None = None,
        model_version_id: int | None = None,
        username: str | None = None,
        nsfw: NsfwLevel | bool | None = None,
        sort: ImageSort | None = None,
        period: Period | None = None,
        page: int | None = None,
        cursor: str | None = None,
    ) -> AsyncPage[Image]:
        """Return a paginated list of images.

        :param limit: Maximum number of results per page, defaults to None
        :type limit: int, optional
        :param post_id: Filter to images from a specific post, defaults to None
        :type post_id: int, optional
        :param model_id: Filter to images associated with a model, defaults to None
        :type model_id: int, optional
        :param model_version_id: Filter to images for a specific model version, defaults to None
        :type model_version_id: int, optional
        :param username: Filter to images uploaded by a specific user, defaults to None
        :type username: str, optional
        :param nsfw: NSFW level filter or boolean toggle, defaults to None
        :type nsfw: NsfwLevel or bool, optional
        :param sort: Sort order, defaults to None
        :type sort: ImageSort, optional
        :param period: Time period for sort metric, defaults to None
        :type period: Period, optional
        :param page: Page number to fetch, defaults to None
        :type page: int, optional
        :param cursor: Pagination cursor from a previous response, defaults to None
        :type cursor: str, optional
        :return: First page of matching images
        :rtype: AsyncPage[Image]
        """
        params: dict[str, Any] = {
            "limit": limit,
            "postId": post_id,
            "modelId": model_id,
            "modelVersionId": model_version_id,
            "username": username,
            "nsfw": nsfw,
            "sort": sort,
            "period": period,
            "page": page,
            "cursor": cursor,
        }
        return await self._client.get_page("/images", params=params, item_type=Image)
