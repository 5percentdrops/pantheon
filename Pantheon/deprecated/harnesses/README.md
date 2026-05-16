# Deprecated harness declarations

Files here describe harnesses no active agent uses. They are kept for audit and historical reference. Re-activating requires:

1. Adding an agent record with `harness: <name>` in `Pantheon/paperclip/organization.import.json`
2. Moving the harness yaml back to `Pantheon/harnesses/`
3. Updating `validate_v8_2_control_plane.py` if needed
