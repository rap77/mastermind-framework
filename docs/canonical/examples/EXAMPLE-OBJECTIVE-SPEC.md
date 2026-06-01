# Objective Spec: Google OAuth Login

<!-- mm:objective-spec | slug: google-oauth-login | intent: feature | status: draft -->

## 1. Objective Identity

- **Slug:** google-oauth-login
- **Name:** Google OAuth Login
- **Intent:** feature
- **Project:** prosell-sass
- **Status:** draft

## 2. Summary

Add Google OAuth as the primary authentication method so users can sign in without managing a password.

## 3. Why It Matters

- **Product reason:** Reduces signup friction — the #1 drop-off point in the current onboarding flow.
- **Technical reason:** Removes the need to store and manage hashed passwords; delegates identity to Google.
- **User impact:** One-click login; no "forgot password" support needed for the MVP.

## 4. Scope

### In scope

- Google OAuth 2.0 flow (authorization code)
- Session management via JWT stored in httpOnly cookie
- User creation on first login (auto-provision)
- Protected route guard on frontend

### Out of scope

- Other OAuth providers (GitHub, Microsoft)
- Email/password fallback
- MFA

## 5. Acceptance Criteria

- [ ] User can click "Sign in with Google" and land on the dashboard
- [ ] On first login, a user record is created in the DB
- [ ] On subsequent logins, the existing record is reused
- [ ] Session expires after 24h and redirects to login
- [ ] Protected routes return 401 if no valid session

## 6. MVP Relevance

- **Included in MVP:** yes
- **Reason:** Authentication is a blocker for every other user-facing feature.

## 7. Dependencies

- **Depends on:** project-state-mvp (user table must exist)
- **Unlocks:** dashboard-realtime, any feature that requires an authenticated user

## 8. Technical Context

- **Affected modules:** `apps/api/routes/auth.py`, `apps/web/app/login/page.tsx`, user schema
- **Approach:** Use `authlib` on the FastAPI side; `next-auth` or custom redirect flow on the Next.js side
- **Known constraints:** Running on WSL2 — localhost OAuth redirect must be configured in Google Cloud Console

## 9. Evidence

- `docs/PRD/00-PRD-prosell.md` — authentication section
- `CLAUDE.md` — stack constraints (FastAPI + Next.js)
- `apps/api/routes/` — existing route structure
