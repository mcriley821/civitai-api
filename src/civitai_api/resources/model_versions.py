"""GET /model-versions/{id} and hash lookup endpoints."""

from __future__ import annotations

from pydantic import TypeAdapter

from civitai_api._internal.resource import AsyncAPIResource, SyncAPIResource
from civitai_api.types.model import ModelVersion


class ModelVersions(SyncAPIResource):
    """Sync resource for /model-versions endpoints."""

    def retrieve(self, version_id: int) -> ModelVersion:
        """Return a single model version by ID.

        :param version_id: Numeric model version ID
        :type version_id: int
        :return: The requested model version
        :rtype: ModelVersion
        :raises NotFoundError: If no version exists with the given ID
        """
        return self._client.get(f"/model-versions/{version_id}", cast_to=ModelVersion)

    def by_hash(self, hash_value: str) -> ModelVersion:
        """Return the model version whose primary file matches a given hash.

        :param hash_value: File hash (any algorithm — SHA256, AutoV2, CRC32, etc.)
        :type hash_value: str
        :return: The matching model version
        :rtype: ModelVersion
        :raises NotFoundError: If no version file matches the hash
        """
        return self._client.get(f"/model-versions/by-hash/{hash_value}", cast_to=ModelVersion)

    def by_hash_batch(self, hashes: list[str]) -> list[ModelVersion]:
        """Return model versions whose primary files match the given hashes.

        :param hashes: List of file hashes to look up
        :type hashes: list[str]
        :return: Model versions matching the provided hashes
        :rtype: list[ModelVersion]
        """
        result = self._client.post(
            "/model-versions/by-hash",
            json_body=hashes,
            cast_to=list[ModelVersion],
        )
        return TypeAdapter(list[ModelVersion]).validate_python(result)


class AsyncModelVersions(AsyncAPIResource):
    """Async resource for /model-versions endpoints."""

    async def retrieve(self, version_id: int) -> ModelVersion:
        """Return a single model version by ID.

        :param version_id: Numeric model version ID
        :type version_id: int
        :return: The requested model version
        :rtype: ModelVersion
        :raises NotFoundError: If no version exists with the given ID
        """
        return await self._client.get(f"/model-versions/{version_id}", cast_to=ModelVersion)

    async def by_hash(self, hash_value: str) -> ModelVersion:
        """Return the model version whose primary file matches a given hash.

        :param hash_value: File hash (any algorithm — SHA256, AutoV2, CRC32, etc.)
        :type hash_value: str
        :return: The matching model version
        :rtype: ModelVersion
        :raises NotFoundError: If no version file matches the hash
        """
        return await self._client.get(f"/model-versions/by-hash/{hash_value}", cast_to=ModelVersion)

    async def by_hash_batch(self, hashes: list[str]) -> list[ModelVersion]:
        """Return model versions whose primary files match the given hashes.

        :param hashes: List of file hashes to look up
        :type hashes: list[str]
        :return: Model versions matching the provided hashes
        :rtype: list[ModelVersion]
        """
        result = await self._client.post(
            "/model-versions/by-hash",
            json_body=hashes,
            cast_to=list[ModelVersion],
        )
        return TypeAdapter(list[ModelVersion]).validate_python(result)
