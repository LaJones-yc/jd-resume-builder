---
name: jd-resume-builder
description: Create truthful, JD-tailored, bilingual one-page resumes from an evolving experience library and user-provided evidence. Use whenever a user wants to build, revise, tailor, translate, or export a resume; uploads an old resume, paper, slide deck, report, or code repository for resume extraction; asks what information is still missing; or needs matching Chinese and English Markdown/PDF versions. Guide the user interactively, preserve source evidence, never invent facts, and render polished full-page A4 PDFs.
---

# JD Resume Builder

Build resumes as an evidence-backed conversation, not a one-shot rewrite. Maintain an evolving experience library, tailor from verified facts, ask focused questions when evidence is incomplete, and keep Chinese and English outputs aligned.

## Non-negotiable principle

Never invent an organization, role, date, responsibility, tool, metric, award, causal claim, user result, or level of ownership. A plausible claim is still unverified. Label uncertain material and ask the user to confirm it before using it in a final resume.

When the user identifies a resume as their latest carefully curated version, treat it as the canonical baseline for wording, ordering, factual scope, and personal voice. Preserve its language unless a targeted change produces a clear JD-matching or one-page-layout benefit. Do not casually replace user-optimized phrasing with generic resume language; record useful new variants in the experience library instead of erasing the baseline.

## Conversation workflow

### 1. Establish the workspace

Ask whether the user already has an experience library and where it should be maintained. If not, ask where to create it, suggesting a user-controlled default such as `resume-workspace/experience-library.json`, then initialize it with `scripts/experience_library.py init`. Never silently store personal data inside the installed Skill directory: the library belongs to the user, evolves across applications, and must survive Skill upgrades.

Ask whether an uploaded resume should be treated as the canonical baseline. Before rendering, ask where Markdown and PDF outputs should be saved; suggest `resume-workspace/output/<company>-<role>/` when the user has no preference.

### 2. Gather evidence

Invite any combination of:

- Existing Chinese or English resumes, especially PDF files
- Project descriptions, papers, theses, reports, slide decks, portfolios, or product documents
- Code repositories, READMEs, commit history, issues, demos, or analytics screenshots
- Awards, certificates, transcripts, performance reviews, or notes
- Direct answers describing work that is not documented elsewhere

Read `references/source-ingestion.md` before processing source materials. For PDFs, extract text with `scripts/extract_pdf_text.py`, then visually inspect important pages when layout affects interpretation.

### 3. Build and enrich the experience library

Read `references/experience-library.md`. Create one record per experience and keep:

- Stable experience ID and type
- Organization/project, role, location, dates
- Verified facts and exact metrics
- Tools, methods, responsibilities, outputs, and impact
- Source references and short evidence excerpts
- Open questions and confidence status
- Candidate Chinese and English bullets

After each new source, summarize what was learned and ask only the highest-value missing questions. Let the user decide whether one complex project should be one entry, several subprojects, or a research/project combination.

### 4. Obtain and analyze the JD

Ask for the full JD only after enough source material exists, unless the user already supplied it. Read `references/jd-tailoring.md` and identify:

- Core responsibilities and must-have capabilities
- Domain, tools, methods, and business vocabulary
- Evidence the employer is likely to value
- Gaps that require clarification rather than invention

Treat the experience library as the source of truth. Select, reorder, and rephrase verified evidence; do not bend facts to match keywords.

Create a JD keyword coverage ledger. Add important terminology naturally to canonical statements only where direct or transferable verified evidence supports it. Never claim an unsupported tool, responsibility, domain, or result for ATS coverage, and never keyword-stuff.

### 5. Propose a tailoring plan

Before writing the final resume, show a concise plan:

- Recommended sections and whether research/projects should merge
- Experiences to include, omit, or de-emphasize
- Evidence supporting each major JD requirement
- Questions blocking stronger bullets
- Any content that may need user confirmation

Invite feedback when the choice or decomposition of an experience is genuinely subjective.

Order sections dynamically by JD relevance and evidence strength rather than using one universal sequence. A data-analysis role may benefit from placing highly relevant projects before research, while a research role may benefit from the reverse. If research contains only one entry, normally merge it with projects unless the research identity itself is strategically important.

Within a project, research, or merged project/research section, order entries by recency using the actual end date and then start date, newest first. Depart from reverse chronology only when the user explicitly requests another order. Use JD relevance to select entries and order sections, not to silently scramble chronology within a section.

Apply a strict content budget. The experience library may be extensive, but a one-page resume should normally contain no more than 8-9 combined internship, research, and project entries. This is an upper bound rather than a target. Prefer fewer, deeper, JD-relevant entries; with two strong internships and two research entries, usually select only 1-3 projects. Keep lower-value coursework in the library as role-specific backup instead of crowding the resume.

### 6. Draft paired Markdown resumes

Read `references/markdown-format.md`. Generate Chinese and English Markdown with the same sections, entries, dates, factual claims, metrics, tools, and bullet order. Translation can be idiomatic; evidence cannot drift.

Prefer detailed achievement bullets with this logic where evidence permits:

`context/problem -> action/ownership -> method/tool -> output/result`

Do not mechanically force every bullet into the same sentence shape. Use 2-4 bullets for important experiences and fewer for secondary entries.

Keep bullet styling consistent within comparable sections. Do not give one experience label-style prefixes such as `Data Collection:` or `Modeling:` when neighboring experiences use direct achievement statements. Use such prefixes only when the user explicitly requests them or applies them consistently across the section.

### 7. Validate and render

Run:

```powershell
python scripts/validate_bilingual.py resume-en.md resume-zh.md
python scripts/render_resume.py resume-en.md resume-en.pdf
python scripts/render_resume.py resume-zh.md resume-zh.pdf
```

The renderer searches for the largest safe layout that remains exactly one A4 page, reducing excessive bottom whitespace while enforcing a minimum readable size. If content still does not fit, prioritize or shorten content rather than hiding overflow.

Render both PDFs to PNG and inspect them. Verify glyphs, hierarchy, alignment, clipping, whitespace balance, and full-page density before delivery.

Treat visual review as an editing loop, not a final glance. Inspect for orphan bullets, isolated punctuation, Latin words or phrases split across lines, unexpectedly early wrapping, accidental blank lines, uneven entry spacing, awkward portrait clearance, and excessive bottom whitespace. When an issue comes from content length or line composition, revise the Markdown wording or structure and render again; do not rely only on shrinking fonts or changing coordinates. Repeat until both languages have no visible layout anomalies.

Name final PDFs `姓名-公司-岗位-中文简历.pdf` and `姓名-公司-岗位-英文简历.pdf`, using the user's preferred display name and company/role spelling. Replace characters invalid in the target operating system rather than changing factual wording. Markdown filenames may mirror the PDFs.

### 8. Feedback loop

Present the Markdown drafts and PDFs, then ask for corrections to facts, emphasis, wording, structure, or visual density. Apply feedback to both outputs and, when it changes the source of truth, update the experience library. Finish only when the user approves or explicitly ends the task.

At handoff, remind the user to read every selected experience and be ready to explain its context, personal contribution, method, trade-offs, metrics, and result. Flag newly restored or substantially rewritten bullets for special review before an interview.

## Resource routing

- Read `references/source-ingestion.md` when the user provides a resume, paper, deck, report, or repository.
- Read `references/experience-library.md` when creating or changing the library.
- Read `references/jd-tailoring.md` when a JD is available.
- Read `references/markdown-format.md` before drafting the resume files.
- Use bundled scripts for deterministic extraction, storage, validation, and PDF generation.
