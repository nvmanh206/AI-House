# Clone-and-run Docker

1. Preserve the existing installation's credentials in ignored root `.env`, without printing values or deleting volumes.
2. Replace host `.local` mounts with named Docker volumes; make Gemini key optional. Persist generated JWT, migrate both databases, register official sources and import versioned public tariff data on startup, without creating demo users or readings.
3. Provide tracked pgAdmin server configuration, configurable loopback ports, first-user local admin setup and reliable launch scripts/documentation.
4. Exclude secrets, generated outputs and agent tooling from Git and image contexts. Audit the tracked/exported source; preserve project code and documentation.
5. Export a clean source snapshot and start it under an isolated Compose project with fresh volumes/alternate ports and no env files or Gemini key. Verify registration, onboarding, readings, billing, knowledge schema and restart persistence. Retest the current installation and record evidence.

No commit/push is requested. Gemini needs a personal key; absent key must remain a clear service error. Keep current volumes and business data intact.
