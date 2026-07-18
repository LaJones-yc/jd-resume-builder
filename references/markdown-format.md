# Resume Markdown format

Use ordinary Markdown plus a small TOML front matter block. TOML is used because Python can parse it without an extra package.

```markdown
+++
language = "en"
location = "Hangzhou, China"
phone = "(86)138-0000-0000"
email = "name@example.com"
photo = ""
max_scale = 1.25
photo_width_mm = 12
photo_height_mm = 16.8
photo_column_mm = 15
header_gap_mm = 0.4
contact_layout = "two-line"
+++

# Full Name

## EDUCATION
### Organization or school || Right-side location
#### Degree or role || 2023.09 - 2027.06
- A concise fact with metrics.

## PROFESSIONAL EXPERIENCE
### Company || City
#### Role || 2025.06 - 2025.08
- Achievement-focused bullet.
```

## Rules

- Use one `#` heading for the person's name.
- Put contact data in front matter; the renderer creates the header line.
- Set `contact_layout = "two-line"` to place location and phone on the first contact line and email on the second. The renderer localizes labels for Chinese and English. Omit it for the compact single-line default.
- Use `##` for sections, `###` for organization/project rows, and `####` for role/date rows.
- Separate the left and right columns with `||`.
- Use `-` bullets only. Continuation lines are joined automatically.
- Keep a paired Chinese and English file with the same section, entry, and bullet order.
- Set `language` to `zh` or `en`.
- `photo` is optional and relative to the Markdown file. The Chinese reference layout supports a portrait in the upper-right.
- `photo_width_mm`, `photo_height_mm`, `photo_column_mm`, and `header_gap_mm` compactly control the portrait header. Keep the photo small enough that it does not create a false blank paragraph before the first section.
- `margin_x_mm`, `margin_top_mm`, and `margin_bottom_mm` are optional page controls. Use them sparingly and verify the rendered page visually.
- `font_regular`, `font_bold`, `font_zh_regular`, and `font_zh_bold` may point to local font files. The renderer otherwise discovers common Windows, macOS, and Linux fonts and gives a clear error when no embeddable Chinese font exists.
- `max_scale` caps automatic enlargement. The renderer chooses the largest size that still fits exactly one page, so shorter resumes do not leave excessive empty space.
- Keep raw Markdown free of font sizes, coordinates, tables, and HTML. The script owns layout.

## One-page policy

The script tries several calibrated density levels. It must either produce exactly one A4 page or fail with a clear message. When it fails, shorten or prioritize content; do not force unreadably small text.

## Visual review loop

After every meaningful content or layout change, render the PDF to an image and inspect it at readable resolution. Check:

- isolated bullets or punctuation on their own lines
- split Latin tokens and phrases such as product names, model names, or `AI Agent`
- early line breaks caused by mixed Chinese and Latin text
- extra blank lines or inconsistent gaps between entries
- portrait-induced whitespace, clipping, collisions, and uneven bottom whitespace

Fix content-driven issues in Markdown first by removing accidental blank bullets, tightening wording, or restructuring a sentence. Use renderer parameters only for genuine layout calibration. Render and inspect again before delivery.
