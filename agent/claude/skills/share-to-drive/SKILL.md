---
name: share-to-drive
description: Put a plan, feasibility or other markdown write-up into Google Drive as a Google Doc with gsync, and pull reviewers' doc comments back. Use when Harman says share, publish, upload or send a plan / feasibility / write-up to Drive or Google Docs, or asks to read or resolve comments on a doc that was shared this way.
---

# Share a write-up to Google Drive (gsync)

`gsync` is Vanta's CLI for pushing a markdown file to Google Docs (`npx gsync`, in the obsidian
repo). Its Claude plugin syncs doc comments back to the local file.

## Before you start

1. **Read the tool's README first**: `scripts/gsync/README.md` in the obsidian checkout
   (`/workspaces/obsidian`). Use the exact commands it gives; do not guess flags.
2. **Login.** If a gsync command fails because it is not logged in, stop and tell Harman to run
   `npx gsync auth login` from an editor (VS Code / Cursor) terminal on this box. The browser
   sign-in does not work from a plain agent shell.
3. **Ask before every upload.** Writing to Google Drive is visible to other people. Say which
   file, which Drive folder or doc, and wait for a yes. Never change sharing settings.

## Upload

1. If the file has a `layersmap` block (plans and feasibility ticket maps), make the Drive copy:
   `python3 ~/.agent-setup/bin/plan-for-drive.py <file>.md` → `<file>.drive.md`.
   Google Docs cannot run the interactive map, so the copy shows it as tables. Upload the
   `.drive.md` copy; keep editing the original.
2. Upload with gsync as its README describes. Destination: the folder Harman names. If he names
   none, ask; do not pick one.
3. Reply with the Google Doc link, and the `ws plan <box> <name>` command for the interactive map.

## Comments

When Harman says reviewers commented: use gsync's Claude plugin (listed under plugin skills in
`ws skills`) to pull the comments, apply the agreed changes to the **original** `.md`, re-run
`check-plan.py` if it is a plan, regenerate the `.drive.md` copy and upload again.

## Editing an existing Google Doc

gsync is for docs it created from markdown. To change a doc someone else owns (for example one
tab of a team doc), use the Google Workspace CLI `gws` instead (Guru: "CLI Tools for Agents"),
and ask Harman first.
