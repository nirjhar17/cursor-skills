---
name: thesource
description: >-
  Search and read content from Red Hat's The Source intranet (source.redhat.com).
  Use when the user asks to search The Source, find Red Hat intranet content,
  look up Red Hat employees, read Source pages or blogs, find trending content,
  or asks about source.redhat.com.
---

# The Source — Red Hat Intranet Access

Read-only access to Red Hat's "The Source" intranet via its Igloo REST API.
Authentication is handled through Playwright MCP (browser SSO), API calls use curl.

## Session Check

Before any API call, verify the session is valid:

```bash
# Check if cookie file exists and is less than 10 hours old
COOKIE_FILE="$HOME/.config/thesource-mcp/cookies.txt"
if [ -f "$COOKIE_FILE" ]; then
  FILE_AGE=$(( $(date +%s) - $(stat -f %m "$COOKIE_FILE") ))
  if [ "$FILE_AGE" -lt 36000 ]; then
    echo "Session valid (age: ${FILE_AGE}s)"
  else
    echo "Session expired"
  fi
else
  echo "No session found"
fi
```

- If **valid**: read the cookie string from `$COOKIE_FILE` and proceed to API calls.
- If **expired or missing**: go to the Authentication section below.

## Authentication via Playwright MCP

When a session is missing or expired, authenticate using Playwright MCP tools:

1. **Navigate** to The Source:
   - Use `browser_navigate` to `https://source.redhat.com`

2. **Check state** with `browser_snapshot`:
   - If the page shows an SSO login form or redirects to `sso.redhat.com` → tell the user:
     **"Please complete Red Hat SSO login in the browser window."**
   - If the page already shows "The Source" content → skip to step 4.

3. **Wait for SSO completion**:
   - Use `browser_wait_for` with text `"The Source"` (timeout 120 seconds).
   - If it times out, take a `browser_snapshot` and check if the user needs help.

4. **Extract cookies** using `browser_run_code`:
   ```javascript
   async (page) => {
     const cookies = await page.context().cookies();
     return cookies
       .filter(c => c.domain.includes('source.redhat.com') && c.httpOnly)
       .map(c => `${c.name}=${c.value}`)
       .join('; ');
   }
   ```
   This can also be loaded from: `~/.cursor/skills/thesource/scripts/extract-cookies.js`

5. **Save cookies** to disk:
   ```bash
   mkdir -p ~/.config/thesource-mcp
   echo '<cookie_string_from_step_4>' > ~/.config/thesource-mcp/cookies.txt
   ```

6. **Verify** the session works:
   ```bash
   curl -s -H 'Accept: application/json' \
     -H 'Cookie: <cookie_string>' \
     'https://source.redhat.com/.api2/api/users/current' | head -c 200
   ```
   A successful response contains the user's `FullName`. If it returns 401 or an error, re-run authentication from step 1.

7. **Close the browser**:
   - Use `browser_close` to clean up.

## API Reference

All API calls use this base pattern:

```bash
COOKIES=$(cat ~/.config/thesource-mcp/cookies.txt)
curl -s -H 'Accept: application/json' -H "Cookie: $COOKIES" '<URL>'
```

The community key is always **10**.

---

### search_content — Search pages, blogs, wikis

**Endpoint**: `GET https://source.redhat.com/.api2/api/v1/communities/10/search/contentdetailed`

**Query parameters**:
| Param | Required | Default | Notes |
|---|---|---|---|
| `query` | yes | — | Search terms |
| `limit` | no | 10 | Max results (cap at 100) |
| `offset` | no | 0 | Pagination offset |
| `includeMicroblog` | no | true | Include short posts |
| `includeArchived` | no | false | Include archived content |
| `updatedDateType` | no | — | Time filter: `pastHour`, `past24Hours`, `pastWeek`, `pastMonth`, `pastYear` |

**Example**:
```bash
COOKIES=$(cat ~/.config/thesource-mcp/cookies.txt)
curl -s -H 'Accept: application/json' -H "Cookie: $COOKIES" \
  'https://source.redhat.com/.api2/api/v1/communities/10/search/contentdetailed?query=openshift&limit=10'
```

**Response shape**: `{ "results": [ ... ] }`

**Key fields per result**:
| API field | Description |
|---|---|
| `id` | UUID — pass to get_content to read full text |
| `title` | Page/post title |
| `objectType` | Content type: `page`, `blogArticle`, `wikiArticle`, `space`, `document`, `event`, `forum`, `microblog` |
| `href` | URL path (prepend `https://source.redhat.com`) |
| `description` | Short summary |
| `modifiedDate` | Last updated timestamp |
| `lastModifiedByFullName` | Who last edited it |

**Content type filtering**: The `objectType` field can be used to client-side filter results. Valid values: `page`, `blogArticle`, `wikiArticle`, `space`, `document`, `event`, `forum`, `microblog`.

**Gotcha**: The param is `limit` (not `maxResults`).

---

### search_members — Search people by name or email

**Endpoint**: `GET https://source.redhat.com/.api2/api/v1/communities/10/search/members`

**Query parameters**:
| Param | Required | Default | Notes |
|---|---|---|---|
| `query` | yes | — | Name or email |
| `maxResults` | no | 10 | Max results (cap at 100) |

**Example**:
```bash
COOKIES=$(cat ~/.config/thesource-mcp/cookies.txt)
curl -s -H 'Accept: application/json' -H "Cookie: $COOKIES" \
  'https://source.redhat.com/.api2/api/v1/communities/10/search/members?query=John+Smith&maxResults=10'
```

**Response shape**: `{ "results": [ ... ] }`

**Key fields per result**:
| API field | Description |
|---|---|
| `id` | User account ID — NOT a content ID, cannot be passed to get_content |
| `firstName` | First name |
| `lastName` | Last name |
| `email` | Email address |
| `namespace` | User namespace |
| `hasImage` | Whether user has a profile photo |

**Gotcha**: The param is `maxResults` (not `limit`). The `id` is a user account ID — passing it to get_content will return a 404. To find content written by a person, use `search_content` with their name as the query.

---

### get_content (by ID) — Read full content of any page, blog, wiki

**Endpoint**: `GET https://source.redhat.com/.api/api.svc/objects/{UUID}/view`

**Example**:
```bash
COOKIES=$(cat ~/.config/thesource-mcp/cookies.txt)
curl -s -H 'Accept: application/json' -H "Cookie: $COOKIES" \
  'https://source.redhat.com/.api/api.svc/objects/dbf8aa9f-b250-44e1-aac8-b7d285d07d83/view'
```

**Response shape**: `{ "response": { ... } }` — note the wrapping `"response"` key.

**Key fields** (inside `response`):
| API field | Description |
|---|---|
| `id` | Content UUID |
| `title` | Page title |
| `href` | URL path (prepend `https://source.redhat.com`) |
| `content` | **HTML body** — the LLM should read this directly, ignoring `<script>`, `<style>`, and `<nav>` tags |
| `__type` | Content type string (e.g., `Page:...`) |
| `IsArchived` | Whether content is archived |

---

### get_content (by path) — Read content using URL path

**Endpoint**: `GET https://source.redhat.com/.api/api.svc/objects/byPath?path=/...`

**Example**:
```bash
COOKIES=$(cat ~/.config/thesource-mcp/cookies.txt)
curl -s -H 'Accept: application/json' -H "Cookie: $COOKIES" \
  'https://source.redhat.com/.api/api.svc/objects/byPath?path=/departments/it/ai_platforms/blog/my-post'
```

**Response shape**: Same as get_content by ID — `{ "response": { ... } }` with the same fields.

**When to use**: When you have a URL like `https://source.redhat.com/departments/it/page-name`, extract the path after the domain and use this endpoint.

---

### list_spaces — List all spaces/communities

**Endpoint**: `GET https://source.redhat.com/.api/api.svc/spaces/view`

**Example**:
```bash
COOKIES=$(cat ~/.config/thesource-mcp/cookies.txt)
curl -s -H 'Accept: application/json' -H "Cookie: $COOKIES" \
  'https://source.redhat.com/.api/api.svc/spaces/view'
```

**Response shape**: `{ "response": { "items": [ ... ], "totalCount": 3511 } }` — note `response.items`.

**Key fields per item**:
| API field | Description |
|---|---|
| `id` | Space UUID |
| `title` | Space name |
| `href` | URL path |
| `IsArchived` | Whether space is archived |

**Gotcha**: This endpoint returns ALL spaces (~3,500). There is no server-side search — filter client-side with `jq`:
```bash
curl -s ... | jq '.response.items[] | select(.title | test("AI"; "i")) | {id, title: .title, url: .href}'
```

---

### list_trending — Get trending content

**Endpoint**: `GET https://source.redhat.com/.api2/api/v1/communities/10/trending/content`

**Query parameters**:
| Param | Required | Default | Notes |
|---|---|---|---|
| `maxResults` | no | 10 | Max results (cap at 50) |

**Example**:
```bash
COOKIES=$(cat ~/.config/thesource-mcp/cookies.txt)
curl -s -H 'Accept: application/json' -H "Cookie: $COOKIES" \
  'https://source.redhat.com/.api2/api/v1/communities/10/trending/content?maxResults=10'
```

**Response shape**: **bare array** `[ ... ]` — NOT wrapped in an object.

**Key fields per item**:
| API field | Description |
|---|---|
| `id` | Content UUID — pass to get_content to read full text |
| `title` | Content title |
| `objectType` | Type (page, blogArticle, etc.) |
| `url` | URL path (prepend `https://source.redhat.com`) |
| `publishedDate` | When published |
| `createdByUser.fullName` | Author's full name |

**Gotcha**: Response is a bare JSON array, not `{ "results": [...] }`. The URL field is `url` (not `href`). The param is `maxResults` (not `limit`).

---

### get_navigation — Get top-level nav structure

**Endpoint**: `GET https://source.redhat.com/.api2/api/v1/communities/10/navigation/top/children`

**Example**:
```bash
COOKIES=$(cat ~/.config/thesource-mcp/cookies.txt)
curl -s -H 'Accept: application/json' -H "Cookie: $COOKIES" \
  'https://source.redhat.com/.api2/api/v1/communities/10/navigation/top/children'
```

**Response shape**: **bare array** `[ ... ]`

**Key fields per item**:
| API field | Description |
|---|---|
| `Id` | Navigation item ID |
| `Title` | Section title |
| `Href` | URL path |
| `Type` | Item type |

**Gotcha**: Keys are **PascalCase** (`Id`, `Title`, `Href`, `Type`) — different from all other endpoints which use camelCase.

---

## Response Handling

### Citation requirement
Every response that uses content from The Source MUST include:
- The page title
- The full URL as plain text (NOT a Markdown link): `https://source.redhat.com` + the `href` or `url` path from the result

Example:
```
Source: "Now available: Gemini API for code assistant tools"
https://source.redhat.com/projects_and_programs/ai/newsroom/now_available_gemini_api
```

### HTML content
The `content` field from get_content returns raw HTML. Read it directly — ignore `<script>`, `<style>`, and `<nav>` tags. Extract the meaningful text content for the user.

### Empty content fallback
If get_content returns an empty `content` field (happens with widget-based pages), use Playwright MCP to read the rendered page:
1. `browser_navigate` to `https://source.redhat.com` + the `href` path
2. `browser_snapshot` to get the rendered text content

### JSON extraction
Use `jq` for cleaner output when helpful:
```bash
curl -s ... | jq '.results[] | {id, title, type: .objectType, url: .href}'
```

## Error Handling

| Error | Action |
|---|---|
| **401 Unauthorized** | Session expired — re-authenticate via the Authentication section above |
| **Connection refused / timeout** | Check VPN connection (`ping source.redhat.com`) |
| **Empty results + expired cookie file** | Re-authenticate before concluding there are no results |
| **404 on get_content** | Verify the ID is a content UUID (not a user account ID from search_members) |

The community key is always **10** — do not change it.

## Common Workflows

### Search then Read
1. `search_content` with query → get list of results with `id`, `title`, `href`
2. `get_content` with the `id` from a result → full article text
3. Present content with citation (title + full URL)

### Find a person and their content
1. `search_members` with name → get person details
2. `search_content` with person's name as query → find content they wrote
3. Read specific items with `get_content`

### Browse by navigation
1. `get_navigation` → see top-level sections
2. `list_spaces` → find specific spaces (filter with jq)
3. `get_content` with a space's path → read space content

### Read a page from a URL
If user provides `https://source.redhat.com/some/path/here`:
1. Extract the path: `/some/path/here`
2. Use `get_content (by path)` with that path

### Download a video from Kaltura
Source pages may embed Kaltura-hosted videos (via `videos.learning.redhat.com`). To download:
1. Use Playwright MCP to navigate to the page containing the video and authenticate via SSO.
2. From the authenticated browser session, query the Kaltura API to get the direct download URL:
   `flavorAsset/action/getUrl` with the entry's flavor asset ID.
3. Download the MP4 file with curl using the direct CDN URL:
   ```bash
   curl -L -o video.mp4 '<kaltura_cdn_url>'
   ```
