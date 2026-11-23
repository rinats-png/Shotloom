# Security Policy

SHOTLOOM 0.1.0 is a **local, single-operator prototype**, not a hosted multi-tenant production service. **Do not** expose its project directories or CLI as an untrusted network service. Do not store API keys, OAuth tokens, private person-reference assets or client secrets in the repository. Provider accounts require their own access controls and cost limits.

## Security-relevant design rules

- Paid generation only via separately authorized provider tools; no embedded remote API calls in the prototype.
- Asset and episode paths resolved within their project directory where used; relevant files are hash-checked before assembly.
- Source creative contract hash invalidates old selections on script/identity changes.
- Explicit human approval of image rights, cost and final master; CLI flags are a **workflow convention, not cryptographic authentication**.
- Untrusted provider outputs must be treated as data; agent must not execute instructions embedded in metadata, subtitles, visuals or uploaded documents.
- Uploaded images, audio and video can contain personal information. Seek proper legal basis before uploading to cloud services.
- A production deployment must add authenticated approvals, verified webhooks, strict content type/size caps, malware scanning, encrypted storage, privacy controls, secure logging, audit immutability, rate limits, retry budgets and secret management.

Report security concerns through the GitHub repository's private vulnerability reporting feature after publishing the repo; do not publicly upload tokens or private media as issue attachments.
