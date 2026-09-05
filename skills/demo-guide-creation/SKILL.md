---
name: demo-guide-creation
description: >-
  Create professional HTML demo guides for live customer demonstrations of Red Hat
  products. Use when the user asks to "create a demo guide", "build a demo script",
  "make a demo walkthrough", "create a lab guide", or any request to produce a
  step-by-step HTML demo document for customer-facing technical demonstrations.
---

# Demo Guide Creation

Build polished, branded HTML demo guides for live customer demonstrations.
These guides are self-contained single-file HTML documents with copy buttons,
talking points, and clear visual structure.

## When to Use

- "Create a demo guide for [product]"
- "Build a demo script for [feature]"
- "Make a walkthrough for [technology]"
- Any request for a customer-facing demo HTML document

## Architecture

Single self-contained HTML file with:
- Embedded CSS (no external dependencies)
- Embedded JavaScript (copy button functionality)
- Red Hat branding (fonts, colors, styling)
- Progressive demo flow (Demo 0 = setup, Demo 1+ = live demos)

## Required Sections

Every demo guide MUST include these sections in order:

1. **Title and subtitle** with total duration estimate
2. **Table of Contents** (numbered, linked to anchors)
3. **Demo 0: Setup/Prerequisites** (what to do before the customer call)
4. **Demos 1-N** (the actual live demonstrations)
5. **Wrap-Up** (talking points for closing)

## HTML Structure Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Product] Demo Guide</title>
    <style>
        /* See CSS section below */
    </style>
</head>
<body>
<div class="container">
    <h1>[Product] — Live Demo Guide</h1>
    <p class="subtitle">[One-line description of the demo]</p>
    <span class="duration">Total demo time: X-Y minutes</span>
    <div class="toc">...</div>
    <!-- Demos here -->
</div>
<script>/* Copy button JS */</script>
</body>
</html>
```

## CSS Design System

Use these exact styles for consistency across all demo guides:

### Colors
- Primary red: `#ee0000` (Red Hat red — used for step badges, warnings)
- Text: `#1a1a1a` (near-black)
- Secondary text: `#4d4d4d`
- Code background: `#1a1a1a` (dark terminal look)
- Success green: `#3e8635`
- Warning yellow: `#dca614`
- Info blue: `#0066cc`
- Time badge: `#147878` on `#daf2f2`
- Duration badge: `#3d2785` on `#ece6ff`

### Fonts
- Headings: `'Red Hat Display', sans-serif`
- Body: `'Red Hat Text', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`
- Code: `'Red Hat Mono', 'Fira Code', monospace`

### Key Classes
- `.demo-step` — Gray box with rounded corners, has a `data-step` attribute for the red badge label
- `.talking-point` — Yellow-left-bordered box prefixed with "SAY TO CUSTOMER:"
- `.outcome` — Green-left-bordered box prefixed with "EXPECTED RESULT:"
- `.warning` — Red-left-bordered box prefixed with "IMPORTANT:"
- `.time-badge` — Teal pill showing estimated time
- `.gui-badge` / `.cli-badge` — Method indicator badges
- `.copy-btn` — Dark button positioned top-right of code blocks
- `.inline-copy-btn` — Small inline button for individual values
- `.yaml-file` — Code block with filename header bar
- `.toc` — Table of contents with numbered links

## Demo Step Structure

Each demo follows this pattern:

```html
<h2 id="demoN">Demo N: [Title] <span class="time-badge">X min</span> <span class="gui-badge">GUI</span></h2>

<div class="talking-point">[What to say before starting]</div>

<div class="demo-step" data-step="[STEP LABEL]">
    <h3>[Action title]</h3>
    <!-- Instructions, code blocks, lists -->
</div>

<div class="outcome">[What the customer should see]</div>

<div class="talking-point">[What to say after showing the result]</div>
```

## Code Block Rules

1. All YAML that creates Kubernetes resources MUST use heredoc format:
```html
<pre>oc apply -f - &lt;&lt;EOF
apiVersion: ...
kind: ...
metadata:
  name: ...
EOF</pre>
```

2. No comments inside code blocks (keep them clean for copy-paste)

3. Add copy buttons to ALL `<pre>` blocks and important inline values

4. For YAML files with names, use the `.yaml-file` wrapper:
```html
<div class="yaml-file" data-filename="my-resource.yaml">
<pre>oc apply -f - &lt;&lt;EOF
...
EOF</pre>
</div>
```

## Copy Button JavaScript

Include this at the end of `<body>`:

```javascript
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('pre').forEach(function(pre) {
        if (pre.closest('.pre-wrapper')) return;
        var wrapper = document.createElement('div');
        wrapper.className = 'pre-wrapper';
        pre.parentNode.insertBefore(wrapper, pre);
        wrapper.appendChild(pre);
        var btn = document.createElement('button');
        btn.className = 'copy-btn';
        btn.textContent = 'Copy';
        btn.addEventListener('click', function() {
            navigator.clipboard.writeText(pre.textContent.trim());
            btn.textContent = 'Copied!';
            btn.classList.add('copied');
            setTimeout(function() {
                btn.textContent = 'Copy';
                btn.classList.remove('copied');
            }, 2000);
        });
        wrapper.appendChild(btn);
    });

    document.querySelectorAll('.inline-copy-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            navigator.clipboard.writeText(btn.getAttribute('data-copy'));
            btn.textContent = 'Copied!';
            btn.classList.add('copied');
            setTimeout(function() {
                btn.textContent = '⎘';
                btn.classList.remove('copied');
            }, 2000);
        });
    });
});
```

## Writing Guidelines

### Talking Points
- Write as if the presenter is speaking directly to a customer
- Keep them conversational and concise (1-2 sentences)
- Focus on business value, not just technical steps
- Place BEFORE the demo step (to set context) and AFTER (to reinforce the takeaway)

### Demo Steps
- Each step should be executable in under 7 minutes
- Provide BOTH GUI and CLI options where possible
- Include expected output so the presenter knows what "success" looks like
- Add troubleshooting warnings for known failure points

### Code Blocks
- Use `oc apply -f - <<EOF` format for all Kubernetes YAML (one-command execution)
- No comments in code blocks
- Keep code short and focused
- Add inline copy buttons for URLs, passwords, and values the presenter needs to type

### Flow Design
- Demo 0 = Everything done BEFORE the customer joins (operator install, namespace creation, config)
- Demo 1 = Start simple (deploy one app, show it works)
- Middle demos = Build complexity progressively
- Final demos = Advanced topics (optional, time-permitting)
- Wrap-Up = Key takeaways, Q&A ammunition

### Time Estimates
- Assign realistic time badges to each demo
- Include total time in the duration badge at the top
- Format: `Demo 0: X min | Demos 1-N core: Y min | Advanced: Z min`

## Cluster Credentials Section

Always include a credentials box in the prerequisites:

```html
<div style="background:#f0f7ff;border-left:4px solid #0066cc;padding:14px 18px;border-radius:0 6px 6px 0;margin:14px 0;font-size:1.1rem;">
    <strong>Lab Cluster Details</strong><br><br>
    <strong>Console:</strong> <a href="[URL]">[URL]</a> <button class="inline-copy-btn" data-copy="[URL]">⎘</button><br>
    <strong>API:</strong> <code>[API URL]</code> <button class="inline-copy-btn" data-copy="[API URL]">⎘</button><br>
    <strong>Username:</strong> <code>[user]</code> <button class="inline-copy-btn" data-copy="[user]">⎘</button><br>
    <strong>Password:</strong> <code>[pass]</code> <button class="inline-copy-btn" data-copy="[pass]">⎘</button>
</div>
```

## Checklist Before Delivery

- [ ] All code blocks use EOF heredoc format (no raw YAML without `oc apply`)
- [ ] No comments inside code blocks
- [ ] Copy buttons on all `<pre>` blocks and key inline values
- [ ] Every demo has a talking point before AND after
- [ ] Expected outcomes clearly stated
- [ ] Troubleshooting warnings for known failure points
- [ ] Total time estimate is realistic
- [ ] TOC links match section IDs
- [ ] Credentials box has correct values
- [ ] Tested end-to-end on the target cluster

## Reference Implementation

See `/Users/njajodia/Cursor Experiments/gitops/openshift-gitops-demo-guide.html` as the gold-standard reference for style, structure, and quality.
