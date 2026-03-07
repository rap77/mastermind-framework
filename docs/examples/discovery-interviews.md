# Discovery Interview Examples

Collection of discovery interview examples using `/mm:discovery` command for reference.

## Example 1: E-commerce App

**Input:**
```bash
/mm:discovery "Quiero una app para vender productos online"
```

**Process:**
- Brain #8 detected ambiguity (brief too short, missing specifics)
- Asked about: industry, target users, platform, business model
- 12 questions across 4 categories (Users, Platform, Features, Business)
- Routed to Brains #1 (Product), #2 (UX), #4 (Frontend), #5 (Backend)

**Output Summary:**
```markdown
# Discovery Interview Summary

**Session ID:** session-a1b2c3d4
**Date:** 2026-03-07
**Context:** e-commerce_app

**Questions Asked:** 12

**Categories Covered:**
- **Users & Personas** (Brain #2)
- **Platform & Tech Stack** (Brain #4)
- **Key Features** (Brain #1)
- **Business Logic** (Brain #5)

**Key Findings:**
- Industry: Retail fashion (B2C)
- Users: End customers 18-35, mobile-first
- Platform: Mobile app (iOS/Android) + web admin
- Business model: Direct sales, inventory management
- Key features: Product catalog, cart, checkout, order tracking

**Domain Recommendations:**
- Brain #1 suggests: Start with core checkout flow before social features
- Brain #4 recommends: React Native for cross-platform mobile
- Brain #5 advises: Consider existing e-commerce platforms before building custom

**Next Steps:**
1. Create wireframes with Brain #3 (UI Design)
2. Define tech stack with Brain #4 (Frontend) + Brain #5 (Backend)
3. Plan authentication with Brain #5 (Backend)
```

---

## Example 2: B2B SaaS Dashboard

**Input:**
```bash
/mm:discovery "Dashboard para analytics de negocios"
```

**Process:**
- Brief was clearer but still missing key details
- Asked about: data sources, users, analytics needs, visualization types
- 15 questions across 5 categories
- Routed to Brains #1 (Product), #2 (UX), #3 (UI), #5 (Backend)

**Output Summary:**
```markdown
# Discovery Interview Summary

**Session ID:** session-e5f6g7h8
**Date:** 2026-03-07
**Context:** b2b_analytics_dashboard

**Questions Asked:** 15

**Categories Covered:**
- **Users & Roles** (Brain #2)
- **Data Sources** (Brain #5)
- **Visualization** (Brain #3)
- **Key Features** (Brain #1)
- **Analytics Requirements** (Brain #7)

**Key Findings:**
- Users: Business analysts, executives (role-based access)
- Data sources: PostgreSQL, Google Analytics, Stripe (API integration)
- Platform: Web dashboard only
- Business model: B2B SaaS (subscription tiers)
- Key features: Custom reports, real-time data, export options

**Technical Requirements:**
- Backend: API integrations with 3rd party services
- Frontend: Real-time charts (WebSocket/Server-Sent Events)
- Data: ETL pipeline for scheduled updates

**Domain Recommendations:**
- Brain #3 suggests: Use chart library with good accessibility (Chart.js, D3)
- Brain #5 advises: Implement caching layer for expensive queries
- Brain #7 recommends: Track usage metrics for feature prioritization

**Next Steps:**
1. Define data schema with Brain #5 (Backend)
2. Design dashboard layout with Brain #3 (UI Design)
3. Plan API integrations with Brain #5 (Backend)
```

---

## Example 3: OAuth Integration (Technical Spec)

**Input:**
```bash
/mm:discovery "Necesitamos integrar OAuth con Google y Microsoft para login"
```

**Process:**
- Brief was technically specific
- Interview focused on technical requirements
- 8 questions, mostly technical depth
- Heavy routing to Brain #5 (Backend) for security expertise

**Output Summary:**
```markdown
# Discovery Interview Summary

**Session ID:** session-i9j0k1l2
**Date:** 2026-03-07
**Context:** oauth_integration

**Questions Asked:** 8

**Categories Covered:**
- **Security Requirements** (Brain #5)
- **Platform** (Brain #4, #5)
- **User Experience** (Brain #2)

**Key Findings:**
- OAuth providers: Google Identity, Microsoft Identity Platform
- Platform: Mobile app (iOS/Android) + web
- Use case: User registration/login (replace email/password)

**Technical Specification:**

**Security Considerations** (from Brain #5):
- OAuth 2.0 + PKCE extension for mobile apps
- JWT token handling with refresh mechanism
- Secure token storage: Keychain (iOS), Keystore (Android)
- Token revocation on logout
- Rate limiting to prevent abuse

**API Endpoints Needed:**
- POST /auth/google
- POST /auth/microsoft
- POST /auth/refresh
- POST /auth/revoke
- GET /auth/me (validate current session)

**Recommended Libraries:**
- Python (backend): authlib, requests-oauthlib
- Node.js (backend): passport.js, passport-google-oauth20
- iOS: AppAuth (recommended by Google)
- Android: AppAuth-SDK

**Domain Recommendations:**
- Brain #5 advises: Implement refresh token rotation for security
- Brain #2 suggests: Consider "Sign in with Apple" for iOS users

**Next Steps:**
1. Create technical spec document
2. Set up OAuth apps in Google/Microsoft consoles
3. Implement backend endpoints
```

---

## Example 4: Gap Detection (New Expertise Needed)

**Input:**
```bash
/mm:discovery "Necesito implementar SEO y content marketing en mi sitio"
```

**Process:**
- Interview proceeded normally
- Brain #8 detected that current brains don't cover SEO/Marketing
- Generated recommendation for new brain creation
- 10 questions asked before gap detection triggered

**Output Summary:**
```markdown
# Discovery Interview Summary

**Session ID:** session-m3n4o5p6
**Date:** 2026-03-07
**Context:** seo_content_marketing

**Questions Asked:** 10

**Requirements Identified:**
- On-page SEO optimization
- Blog/CMS functionality
- Social media integration
- Analytics tracking

**⚠️ Knowledge Gap Detected:**

Current MasterMind brains (#1-7) focus on software development.
SEO and Content Marketing require **domain expertise not currently available**.

**Gap Details:**
- On-page SEO (meta tags, structured data, sitemaps)
- Technical SEO (page speed, mobile-friendly, crawlability)
- Content strategy (keyword research, content calendar)
- Social media marketing (platforms, scheduling, analytics)

**Recommendation:**

Consider creating **Brain #9: Growth Marketing** with expertise in:
- SEO (on-page, technical, off-page)
- Content strategy and marketing
- Social media marketing
- Analytics and attribution

**Suggested Experts:**
- Rand Fishkin (SEOmoz/Moz)
- Brian Dean (Backlinko)
- Ann Handley (Content Marketing Institute)
- Neil Patel (Crazy Egg, KISSmetrics)

**Available Alternatives:**
- Brain #7 (Growth/Data) can help with analytics setup
- Brain #1 (Product Strategy) can help prioritize SEO features
- Brain #3 (UI Design) can help with SEO-friendly page structure

**Next Steps:**
1. For immediate needs: Use Brain #7 for analytics tracking
2. For long-term: Consider creating Brain #9 or finding SEO specialist
```

---

## Usage Patterns

### When to Use /mm:discovery

| Scenario | Command | Expected Result |
|----------|---------|-----------------|
| **Client onboarding** | `/mm:discovery "cliente necesita X"` | Structured brief for team |
| **Feature request** | `/mm:discovery "agregar feature Y"` | Clarified requirements |
| **Vague idea** | `/mm:discovery "quiero una app"` | Specific direction |
| **Tech spec** | `/mm:discovery "integrar API Z"` | Technical specification |
| **Gap detection** | `/mm:discovery "necesito expertise X"` | New brain recommendation |

### Tips for Best Results

1. **Be honest about uncertainty** — Discovery works best with vague input
2. **Answer all questions** — Even "I don't know" helps the process
3. **Review the Q&A document** — It captures everything discussed
4. **Check gaps detected** — May reveal missing expertise
5. **Share with team** — Output formats designed for collaboration

### Output Files

After each interview, three output files are created:

```
logs/interviews/
├── hot/2026-03/
│   └── INTERVIEW-2026-03-07-001.yaml    # YAML format (logging)
└── json/2026-03/
    └── INTERVIEW-2026-03-07-001.json    # JSON format (machine-readable)
```

The Markdown summary is displayed directly in the Claude Code response.
