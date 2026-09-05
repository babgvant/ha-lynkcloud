"""Async client for the Discover Energy LYNK Cloud web API."""

from __future__ import annotations

from typing import Any

from aiohttp import ClientError, ClientSession


class LynkCloudError(Exception):
    """Base API error."""


class LynkCloudAuthError(LynkCloudError):
    """Authentication failed."""


class LynkCloudApi:
    """Minimal client for the endpoints used by the web portal."""

    def __init__(self, session: ClientSession, host: str, username: str, password: str) -> None:
        self._session = session
        self._host = host.rstrip("/")
        self._username = username
        self._password = password
        self._token: str | None = None

    async def async_login(self) -> None:
        """Authenticate and cache the bearer token."""
        payload = await self._request(
            "POST",
            "/prod-api/login",
            json={"username": self._username, "password": self._password, "code": "", "uuid": ""},
            authenticated=False,
        )
        token = payload.get("token")
        if not token:
            raise LynkCloudAuthError(payload.get("msg", "Login did not return a token"))
        self._token = str(token)

    async def async_get_tree(self) -> list[dict[str, Any]]:
        """Return every site/device node visible to the account."""
        data = await self._get("/prod-api/customer/lynk/system/getTreeListAll", pageNum=1, pageSize=1000)
        return data if isinstance(data, list) else []

    async def async_get_overview(
        self, ul_id: str, begin_time: int, end_time: int
    ) -> dict[str, Any]:
        """Return current aggregate telemetry for a LYNK device."""
        data = await self._get(
            "/prod-api/customer/lynk/device/overview/getOverviewBase",
            ulId=ul_id,
            beginTime=begin_time,
            endTime=end_time,
        )
        return data if isinstance(data, dict) else {}

    async def async_get_batteries(self, ul_id: str) -> list[dict[str, Any]]:
        """Return current telemetry for all batteries on a LYNK device."""
        data = await self._get(
            "/prod-api/customer/lynk/device/battery/getBatteryList", ulId=ul_id
        )
        return data if isinstance(data, list) else []

    async def _get(self, path: str, **params: Any) -> Any:
        payload = await self._request("GET", path, params=params)
        return payload.get("data")

    async def _request(
        self,
        method: str,
        path: str,
        authenticated: bool = True,
        retry_auth: bool = True,
        **kwargs: Any,
    ) -> dict[str, Any]:
        if authenticated and self._token is None:
            await self.async_login()

        headers = {"Accept-Language": "en-US,en;q=0.9"}
        if authenticated and self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        try:
            async with self._session.request(
                method, f"{self._host}{path}", headers=headers, timeout=30, **kwargs
            ) as response:
                if response.status in (401, 403):
                    if authenticated and retry_auth:
                        self._token = None
                        await self.async_login()
                        return await self._request(
                            method,
                            path,
                            authenticated=True,
                            retry_auth=False,
                            **kwargs,
                        )
                    raise LynkCloudAuthError("LYNK Cloud rejected the credentials")
                response.raise_for_status()
                payload = await response.json(content_type=None)
        except LynkCloudAuthError:
            raise
        except (ClientError, TimeoutError, ValueError) as err:
            raise LynkCloudError(str(err)) from err

        if not isinstance(payload, dict):
            raise LynkCloudError("Unexpected response from LYNK Cloud")
        code = payload.get("code")
        if code not in (None, 0, 200):
            message = str(payload.get("msg", f"API error {code}"))
            if not authenticated or code in (401, 403):
                raise LynkCloudAuthError(message)
            raise LynkCloudError(message)
        return payload
