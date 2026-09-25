import time
import json
import flet as ft


class Cache:
    _data: dict = {}
    _expires: dict = {}

    @classmethod
    def set(cls, key: str, value, ttl: int = 30):
        cls._data[key] = value
        cls._expires[key] = time.time() + ttl

    @classmethod
    def get(cls, key: str):
        if key in cls._data and cls._expires.get(key, 0) > time.time():
            return cls._data[key]
        cls._data.pop(key, None)
        cls._expires.pop(key, None)
        return None

    @classmethod
    def invalidate(cls, key: str = None):
        if key:
            cls._data.pop(key, None)
            cls._expires.pop(key, None)
        else:
            cls._data.clear()
            cls._expires.clear()


class AuthState:
    token: str | None = None
    user: dict | None = None

    async def load(self, page):
        sp = ft.SharedPreferences()
        raw = await sp.get("wellness_auth")
        if isinstance(raw, str):
            data = json.loads(raw)
            self.token = data["token"]
            self.user = data["user"]

    async def save(self, page):
        sp = ft.SharedPreferences()
        await sp.set(
            "wellness_auth",
            json.dumps({"token": self.token, "user": self.user}),
        )

    async def clear(self, page):
        sp = ft.SharedPreferences()
        self.token = None
        self.user = None
        Cache.invalidate()
        await sp.remove("wellness_auth")


auth = AuthState()