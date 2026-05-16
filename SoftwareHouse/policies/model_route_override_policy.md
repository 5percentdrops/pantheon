# Model Route Override Policy

Model overrides are allowed only through `model_route.schema.json`.

Allowed issuers:
- Arthur may request an override.
- Magnus may recommend an architecture override.
- Maxwell may recommend escalation to Opus Max.
- Human board must approve budget-increasing or governance-affecting overrides.

Rules:
1. The override must include source agent, target model, reason, expected cost impact, and expiry.
2. The override cannot bypass budget policy.
3. The override cannot change governance, production trading, or secrets policy.
4. The override must be logged in the Paperclip issue transcript.
