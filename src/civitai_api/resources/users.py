"""GET /users and GET /me."""

from __future__ import annotations

from civitai_api._internal.resource import AsyncAPIResource, SyncAPIResource
from civitai_api.types.user import Me, User


class Users(SyncAPIResource):
    """Sync resource for /users endpoints."""

    def retrieve(self, username: str) -> User:
        """Return a user by username.

        :param username: The user's username
        :type username: str
        :return: The requested user
        :rtype: User
        :raises NotFoundError: If no user exists with the given username
        """
        return self._client.get(f"/users/{username}", cast_to=User)

    def me(self) -> Me:
        """Return the currently authenticated user.

        :return: The authenticated user
        :rtype: Me
        :raises AuthenticationError: If no valid credentials are configured
        """
        return self._client.get("/me", cast_to=Me)


class AsyncUsers(AsyncAPIResource):
    """Async resource for /users endpoints."""

    async def retrieve(self, username: str) -> User:
        """Return a user by username.

        :param username: The user's username
        :type username: str
        :return: The requested user
        :rtype: User
        :raises NotFoundError: If no user exists with the given username
        """
        return await self._client.get(f"/users/{username}", cast_to=User)

    async def me(self) -> Me:
        """Return the currently authenticated user.

        :return: The authenticated user
        :rtype: Me
        :raises AuthenticationError: If no valid credentials are configured
        """
        return await self._client.get("/me", cast_to=Me)
