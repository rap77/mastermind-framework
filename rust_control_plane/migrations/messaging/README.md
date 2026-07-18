# Messaging SQLx Migrations

This directory is the SQLx-managed migration lineage for the messaging domain.
Use sequential versions starting at `001`; never edit a migration after it has
been applied.

The parent `migrations/` directory is legacy evidence executed historically via
manual `psql` commands. It contains duplicate versions and is not a valid SQLx
migration source. New messaging migrations must not import or replay its seed
data.
