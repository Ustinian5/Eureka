# Security Policy

## Reporting Security Issues

Do not open a public issue for secrets, credential leaks, or browser extension security problems. Report them privately to the project maintainer.

## Secret Handling

- API keys must be stored in local environment variables or `.env`.
- `.env` is ignored by git.
- `.env.example` must contain placeholders only.
- The browser extension must not collect cookies, passwords, payment data, or browsing history.

## Supported Version

This repository currently supports the latest `main` branch only.
