# Eureka Privacy Policy

Eureka is a local-first research copilot browser extension.

## Data Collected

Eureka reads the active tab page text, title, and URL only after the user clicks the research button. This data is sent to the backend endpoint configured by the user, which defaults to `http://127.0.0.1:8000`.

Eureka does not collect passwords, cookies, browsing history, payment data, or account credentials.

## Data Storage

The extension stores only user settings through Chrome storage:

- backend endpoint
- default model provider
- default report template

The local backend may save generated reports in a local SQLite database on the user's machine.

## Third Parties

If the user configures a real model provider, the local backend may send page text and user questions to that provider's API. Users control which provider and API key are used.

## Contact

This project is a course project. Users can inspect all source code in the repository before installing.
