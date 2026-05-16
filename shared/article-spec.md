# Article Generation Spec — AdSense Matrix Sites

## SEO Requirements (non-negotiable)
- **Title**: 50-60 chars, include primary keyword near beginning, end with site brand via pipe
- **Meta description**: 120-155 chars, include primary keyword, actionable language, no fluff
- **OG tags**: og:title, og:description, og:type=article, og:url, og:site_name, og:locale=en_US
- **Canonical**: full absolute URL
- **JSON-LD Schema**: Article type with headline, description, datePublished, dateModified, author
- **lang="en"** on html tag
- **H1**: single, matches or closely mirrors title
- **H2**: 4-6 per article, each containing related keywords
- **H3**: optional, under H2 where needed
- **Body text**: 1000-1500 words, paragraphs 2-4 sentences max, readable at 16px

## Structure
1. `<header>` — nav bar (copy from site index.html)
2. `<main>` — article content
   - Breadcrumb nav (Home > Article Title)
   - H1 title
   - Publish date + reading time
   - Article body (H2 sections, short paragraphs)
   - Tags (4-6, pill style)
   - Related articles (3 cards, grid)
3. AdSense unit (between body and footer)
4. `<footer>` — legal links (copy from site index.html)

## Content Rules
- Original, not AI-detectable: vary sentence length, use contractions, avoid "delve/embrace/elevate"
- Active voice, 2nd person ("you"), direct advice
- No emoji, no markdown, no placeholder text
- Stats/numbers when possible (e.g., "37% of users" not "many users")
- Each H2 section: core claim → supporting detail → practical takeaway

## File Naming
- Format: `article-{N}.html` where N continues existing numbering
- Example: if site has article-1 through article-12, new files start at article-13

## Delivery
- One complete .html file per article
- Include all CSS/tailwind via CDN (copy from site's existing articles)
- Valid HTML5, no broken tags, no JS errors
- **Must include both Google tags in <head>:**
  - GA4: `G-GGNWR1X1GV` (gtag.js tracking)
  - AdSense: `ca-pub-2595917642864488` (pagead2 script)
