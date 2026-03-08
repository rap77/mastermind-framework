# E2E Testing Manual - Brain #8 Discovery

**Date:** 2026-03-07
**PRP:** PRP-016
**Status:** Ready for Manual Testing

## Instructions

These tests require manual execution with interactive user input. Each test should be executed in Claude Code using the `/mm:discovery` command.

---

## Test Case 1: Vague Brief → Clarified Requirements

### Input
```bash
/mm:discovery "quiero una app moderna"
```

### Expected Flow
1. [ ] Ambiguity detection triggered ("moderna" is vague)
2. [ ] Brain #8 generates interview plan with 4-5 categories
3. [ ] Interview asks about:
   - ¿Qué tipo de app? (delivery, retail, social...)
   - ¿Quiénes son los usuarios?
   - ¿Qué plataformas? (web, mobile...)
   - ¿Qué significa "moderna" para vos?
4. [ ] After 10-15 questions, generates clarified brief

### Expected Output Format
```markdown
# Clarified Requirements

**Original:** "quiero una app moderna"

**Clarified:**
- **Industry:** [Specific industry detected]
- **Users:** [Specific user personas]
- **Platform:** [Specific platform(s)]
- **"Modern" means:** [Specific design/tech/features]

**Recommendations:**
- Brain #X suggests [Specific actionable recommendations]
```

### Validation Checklist
- [ ] Brief is significantly clearer than input
- [ ] All categories have at least 1 Q&A
- [ ] Output includes JSON + YAML + Markdown
- [ ] Duration < 5 minutes
- [ ] Files created in `logs/interviews/`

### Notes
-

---

## Test Case 2: Client Onboarding → Technical Spec

### Input
```bash
/mm:discovery "Cliente de agencia de marketing necesita app para gestionar campañas publicitarias"
```

### Expected Flow
1. [ ] Context detected: "client_onboarding"
2. [ ] Brain #8 generates plan focused on business requirements
3. [ ] Interview covers:
   - Users (marketing managers, clients)
   - Features (campaign creation, analytics, approvals)
   - Platforms (web dashboard + mobile)
   - Integrations (Facebook Ads, Google Ads)
   - Budget (client pricing model)
4. [ ] Recommendations from brains #1, #4, #5

### Expected Output Format
```markdown
# Discovery Interview Summary

**Session ID:** [UUID]
**Context:** client_onboarding

**Key Findings:**
- B2B SaaS for marketing agencies
- Web dashboard for managers + Mobile for field staff
- Must integrate with major ad platforms
- Real-time collaboration critical

**Technical Recommendations** (from Brain #5):
- OAuth for ad platform authentication
- WebSocket for real-time updates
- Background jobs for campaign processing
```

### Validation Checklist
- [ ] Output is specific enough to start development
- [ ] Brain #5 recommendations are technical and actionable
- [ ] Integrations mentioned (Facebook Ads, etc.)
- [ ] Duration < 5 minutes
- [ ] Files created in `logs/interviews/`

### Notes
-

---

## Test Case 3: Gap Detection → Brain Recommendation

### Input
```bash
/mm:discovery "Necesito implementar SEO técnico y content marketing en mi sitio web"
```

### Expected Flow
1. [ ] Interview proceeds normally
2. [ ] Brain #8 detects SEO expertise not in brains #1-7
3. [ ] Generates recommendation for new brain

### Expected Output Format
```markdown
# Discovery Results

**Requirements:**
- On-page SEO optimization
- Content management system
- Blog functionality

**⚠️ Knowledge Gap Detected:**

Current brains (#1-7) focus on software development.
SEO and Content Marketing require expertise not available.

**Recommendation:**

Consider creating **Brain #9: Growth Marketing** with experts:
- Rand Fishkin (SEOmoz)
- Brian Dean (Backlinko)
- Ann Handley (Content Marketing Institute)

**Available Alternatives:**
- Brain #7 (Growth/Data) can help with analytics
- Brain #1 (Product Strategy) can help prioritize SEO features
```

### Validation Checklist
- [ ] Gap is detected correctly
- [ ] Suggested experts are relevant
- [ ] Alternatives (brains #1, #7) are mentioned
- [ ] Output is actionable (can create PRP for new brain)
- [ ] Duration < 5 minutes
- [ ] Files created in `logs/interviews/`

### Notes
-

---

## Test Case 4: Performance Testing (Large Interview)

### Input
```bash
/mm:discovery "Necesito construir un sistema completo de e-commerce B2B con inventario, payments, shipping, y analytics"
```

### Expected Results
- [ ] Generate 15-20 questions
- [ ] Total duration < 5 minutes
- [ ] No timeouts or crashes

### Performance Metrics

| Step | Target | Actual |
|------|--------|--------|
| Interview plan generation | < 30s | ___ |
| Per question (avg) | < 15s | ___ |
| Total interview time | < 5min | ___ |
| Document generation | < 10s | ___ |

### Validation Checklist
- [ ] All categories completed
- [ ] No state loss between questions
- [ ] Complete output generated
- [ ] Files created in `logs/interviews/`

### Notes
-

---

## Bug Report Template

If any test fails, use this template:

```markdown
### Bug #XXX: [Title]

**Test Case:** [1, 2, 3, or 4]

**Description:**
[Brief description]

**Steps to Reproduce:**
1.
2.
3.

**Expected:** [What should happen]
**Actual:** [What actually happened]

**Severity:** [Critical/High/Medium/Low]

**Session ID:** [From interview output]
```

---

## Test Execution Log

| Date | Test Case | Result | Notes |
|------|-----------|--------|-------|
| 2026-03-07 | - | Pending | Ready for execution |
