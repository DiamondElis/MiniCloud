# MiniCloud IAM Service

Phase 1 implements the MiniCloud IAM and STS control plane: users, groups, roles, policies, access keys, sessions, authorization decisions, and audit logs.

## Run Locally

From `minicloud-control-plane`:

```bash
docker compose -f infra/docker-compose.yml up --build
```

Run migrations from another shell:

```bash
cd apps/iam-service
DATABASE_URL=postgresql+psycopg://minicloud:minicloud@localhost:5432/minicloud_iam alembic upgrade head
```

Run tests:

```bash
cd apps/iam-service
pytest
```

## Example Requests

Create a user:

```bash
curl -X POST http://localhost:8001/iam/users \
  -H 'Content-Type: application/json' \
  -d '{"username":"elhan","email":"elhan@example.com","password":"password"}'
```

Login:

```bash
curl -X POST http://localhost:8001/iam/token \
  -H 'Content-Type: application/json' \
  -d '{"grant_type":"password","username":"elhan","password":"password"}'
```

Whoami:

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8001/iam/whoami
```

Create a policy:

```bash
curl -X POST http://localhost:8001/iam/policies \
  -H 'Content-Type: application/json' \
  -d '{"name":"ec2-run","document":{"Version":"2026-01-01","Statement":[{"Effect":"Allow","Action":["ec2:RunInstance"],"Resource":"*"}]}}'
```

Attach a policy to a user:

```bash
curl -X POST http://localhost:8001/iam/users/<user-id>/policies \
  -H 'Content-Type: application/json' \
  -d '{"policy_id":"<policy-id>"}'
```

Authorize:

```bash
curl -X POST http://localhost:8001/iam/authorize \
  -H 'Content-Type: application/json' \
  -d '{"principal_type":"user","principal_id":"<user-id>","action":"ec2:RunInstance","resource":"instance/i-123"}'
```

Simulate policy:

```bash
curl -X POST http://localhost:8001/iam/simulate-principal-policy \
  -H 'Content-Type: application/json' \
  -d '{"principal_type":"user","principal_id":"<user-id>","action":"ec2:RunInstance","resource":"instance/i-123"}'
```

Create an access key:

```bash
curl -X POST http://localhost:8001/iam/access-keys \
  -H 'Content-Type: application/json' \
  -d '{"principal_type":"user","principal_id":"<user-id>"}'
```

Assume a role:

```bash
curl -X POST http://localhost:8001/sts/assume-role \
  -H "Authorization: Bearer <token>" \
  -H 'Content-Type: application/json' \
  -d '{"role_id":"<role-id>","session_name":"demo-session","duration_seconds":3600}'
```

## Known Limitations

- IAM `Condition` support is intentionally deferred. Statements with `Condition` do not match in v1.
- Role trust policy support is minimal: `null` trusts any authorized caller, `"Principal": "*"` trusts all callers, and typed principal ID lists are supported.
- STS temporary access key IDs/secrets are returned for AWS-style shape, but the session token is the credential used for authenticated MiniCloud API calls in v1.
- Full AWS SigV4, service-specific resource authorization, and service accounts are not implemented yet.

## Next Recommended Task

Add a small admin bootstrap command or CLI that creates the first admin user, admin policy, and access key without manual SQL.

