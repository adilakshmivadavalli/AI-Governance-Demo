import os
import time

import requests

from agent.keycloak_auth import get_demo_token

AGENT_URL = os.environ.get("AGENT_URL", "http://agent:8000")


def wait_until_ready(timeout_seconds: int = 1200) -> None:
    """The agent only starts serving once MLflow registration + the real
    promotion gate (real LLM calls) have finished, and Keycloak needs ~1 min
    to import the realm — so on a fresh `docker compose up` this can take a
    few minutes. Polls instead of failing on the first try."""
    deadline = time.time() + timeout_seconds
    last = ""
    while time.time() < deadline:
        try:
            requests.get(f"{AGENT_URL}/health", timeout=5).raise_for_status()
            get_demo_token()
            return
        except Exception as e:  # noqa: BLE001
            msg = f"{type(e).__name__}"
            if msg != last:
                print(f"[wait] agent/keycloak not ready yet ({msg}) — still starting, retrying every 10s...")
                last = msg
            time.sleep(10)
    raise SystemExit("agent did not become ready in time — check `docker compose logs agent`")


def chat(as_user: str = "student", as_password: str = "student123", **payload) -> dict:
    """`role` is NOT a request field — it's derived server-side from which
    Keycloak account you log in as (see agent/main.py:require_human_identity).
    `as_user='instructor'` logs in as the account holding the 'admin' realm
    role instead of the default 'student' ('demo-agent' role)."""
    token = get_demo_token(username=as_user, password=as_password)
    resp = requests.post(f"{AGENT_URL}/chat", json=payload, headers={"Authorization": f"Bearer {token}"}, timeout=180)
    if resp.status_code >= 400:
        raise RuntimeError(f"/chat returned HTTP {resp.status_code}: {resp.text[:600]}")
    return resp.json()


def non_production_version() -> str:
    """Whichever registered model version did NOT win the promotion gate."""
    versions = requests.get(f"{AGENT_URL}/model-versions", timeout=10).json()
    v = next((v["version"] for v in versions if v["stage"] != "Production"), None)
    if v is None:
        raise SystemExit("every registered version is in Production — nothing to demo for Scenario E")
    return v


def print_result(result: dict) -> None:
    print(f"blocked={result['blocked']} blocked_at_layer={result['blocked_at_layer']} role={result.get('role')}")
    print(f"answer={result['answer']!r}")
    print("layer_results:")
    for layer in result["layer_results"]:
        print(f"  {layer['layer']:16s} pass={layer['pass']!s:5s} {layer['reason']}")
