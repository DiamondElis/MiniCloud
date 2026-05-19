import httpx


class IamClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def whoami(self, token: str) -> dict:
        response = httpx.get(f"{self.base_url}/iam/whoami", headers={"Authorization": f"Bearer {token}"}, timeout=5)
        response.raise_for_status()
        return response.json()

    def authorize(self, token: str, principal_type: str, principal_id: str, action: str, resource: str) -> bool:
        response = httpx.post(
            f"{self.base_url}/iam/authorize",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "principal_type": principal_type,
                "principal_id": principal_id,
                "action": action,
                "resource": resource,
            },
            timeout=5,
        )
        response.raise_for_status()
        return response.json().get("decision") == "Allow"

