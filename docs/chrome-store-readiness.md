# Chrome Web Store Readiness Checklist

This checklist maps Eureka to Chrome Web Store expectations.

## Safety and Privacy

- Uses Manifest V3.
- Uses `activeTab` and `scripting` for user-triggered page reads.
- Does not declare `<all_urls>` host access.
- Does not read cookies, passwords, browsing history, or credentials.
- Provides a privacy policy in `docs/privacy-policy.md`.
- Sends page content only to the user-configured backend.

## Functionality

- Provides useful functionality: context-aware page research and report generation.
- Displays Agent Trace so behavior is transparent.
- Provides settings page for endpoint and defaults.
- Shows backend connection errors clearly.

## Store Assets

- Provides 16, 32, 48, and 128 pixel icons.
- Provides store listing copy in `docs/store-listing.md`.
- Provides a packaging script: `scripts/package_extension.ps1`.

## Technical

- No inline JavaScript.
- Uses extension pages CSP.
- Uses external scripts only.
- Provides tests for manifest, options page, icons, and popup controls.
