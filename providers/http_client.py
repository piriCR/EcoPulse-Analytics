from __future__ import annotations

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen



def get_json(url: str, params: dict[str, object] | None = None, headers: dict[str, str] | None = None, timeout: int = 20) -> dict:
    query = f"{url}?{urlencode(params or {}, doseq=True)}" if params else url
    request = Request(query, headers=headers or {"User-Agent": "EcoCities/1.0"})
    with urlopen(request, timeout=timeout) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)
