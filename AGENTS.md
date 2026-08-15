# BERUANG — Project Notes

## Overview
Single-file social app (`index.html`) built on **Supabase** (Postgres + Realtime
+ Storage) with a thin Firebase-RTDB-compatible adapter. Auth, feed, stories,
chat, notifications, profile, plus a points/wallet/QR-transfer system.

## Build environment gotcha
Large `cat >> file << 'EOF'` heredocs in the terminal sometimes report exit 0
but do NOT persist (and `/tmp` writes via Python also fail to persist). Workarounds
that DID work:
- Append in **smaller chunks** (≤ ~80 lines each).
- For the head/style block, use the `file_editor` `str_replace` tool (dedicated
  editor handles exact large content reliably).
- Stray leading characters (`O`, `y`, `$`, etc.) shown in terminal stdout before
  lines are **display artifacts only** — verify with `grep -nE "^[a-z$] "` (empty = clean).

## Verify JS
Extract the module script and run `node --check`:
```bash
python3 -c "import re;h=open('index.html').read();m=re.search(r'<script type=\"module\">(.*?)</script>',h,re.DOTALL);open('/tmp/c.mjs','w').write(re.sub(r'^\s*import .*?;\s*$','',m.group(1),flags=re.MULTILINE))"
node --check /tmp/c.mjs
```

## Features implemented
- Posts are free-form: text-only, image-only, or text + image (image optional).
- Posts render in bordered cards on the beranda; text-only posts show the body
  without an image area. Like + comment only (no share button).
- Like count badge + double-tap image to like.
- Supabase Storage bucket `media` for posts/stories/avatars (uploads return a
  public URL; falls back to base64 if the bucket/policies are missing).
- Pull-to-refresh on every `.view` (touchstart/move/end, `#ptr-indicator`).
- Logout fully resets caches (`usersCache`, `followingCache`, `myTier`, etc.),
  closes any open modal/chat, and shows a toast.
- Points: comment=50, post=20, follow (+10 to follower), like=2 (first-time).
- 6-digit account ID (auto-generated, uniqueness-checked, stored in `account_index`)
- 4-digit transaction PIN (`wallets/{uid}/pin`)
- QR code (my account) + camera scan (jsQR) + manual ID entry
- Transfer flow: scan/lookup → amount → PIN → atomic debit/credit (runTransaction)
- Transaction history modal
- Edit profile modal: fullname, phone, email (optional), gender
- Rank tiers: Star (0), Bronze (500), Silver (2000), Gold (5000), Master (15000)

## Supabase config
`index.html` is wired to the project's Supabase URL + anon key. The bottom of
the file has a `SQL_SETUP` comment (nodes table, cas_update RPC, Realtime, RLS)
and a `STORAGE SETUP` comment (create the public `media` bucket + policies).
DB paths used: `users`, `wallets`, `account_index`, `profiles`, `posts`,
`stories`, `following`, `followers`, `notifications`, `chats`, `private_chats`.
