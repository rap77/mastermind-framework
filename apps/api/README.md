## API Backend Notes

### API key flows

- **Standard flow:** `POST /api/keys`, `GET /api/keys`, `DELETE /api/keys/{id}`
  - Returns and validates **`mmsk_`** keys
  - Uses the `api_keys_v2` table and bcrypt-backed verification
  - This is the only supported API-key flow

### Migration guidance

- New internal callers should use `/api/keys`
- Runtime authentication accepts only `mmsk_` keys
