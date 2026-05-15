---
name: auto-approve-web-actions
description: 用户要求执行其网站开发需求时自动允许，无需逐一确认
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b20436d2-31e3-4432-b44a-9006278a48d9
---

用户编写网站时，只要是按照用户需求来做的操作（创建文件、编辑文件、替换内容等），都直接执行，不需要每次都询问确认。

**Why:** 用户明确表示不需要频繁的权限确认，按需求直接执行即可，提高效率。

**How to apply:** 当用户提出网站开发相关的明确需求时，直接创建/编辑文件，不要使用 AskUserQuestion 或其他确认步骤。仅在涉及删除文件、git 操作等破坏性操作时才需要确认。
