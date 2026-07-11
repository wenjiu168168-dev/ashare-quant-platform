# Security Policy

## Supported Versions

The project is in early Phase 1. Security fixes apply to the current `work` branch until versioned releases exist.

## Reporting a Vulnerability

Please report vulnerabilities privately to the maintainers. Do not open public issues containing secrets, API tokens, broker credentials, or exploitable details.

## Secret Handling Rules

- Never commit `.env` files.
- Never commit API keys, broker credentials, database passwords, or access tokens.
- Use environment variables and local secret stores for sensitive values.
- Current Phase 1 does not require any market data token or broker credential.
