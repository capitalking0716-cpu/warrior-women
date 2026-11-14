# What Neko must do himself vs what is already done

## Already done (Shadow)

- ✅ The full Warrior Women membership app — Python + Streamlit, in this folder.
- ✅ Public landing (program overview, $10/month, Stripe checkout link).
- ✅ Member sign-up and login (email + password, passwords hashed).
- ✅ REAL Stripe paywall — only an active $10/month subscription unlocks
  the program. No key = locked. Stripe error = locked. No fake paywall.
- ✅ The full program: 7-day re-entry week, six-day split, 120-day
  foundation, 24-week progression, 40-exercise library, per-set logging,
  readiness checks, progress tracking, nutrition & recovery, rule-based
  AI coach — with the same safety rules as the app already built.
- ✅ 34 tests, all passing.
- ✅ App boot-tested locally (serves HTTP 200).
- ✅ Deploy guide (DEPLOY.md) and this checklist.

## Neko must do himself

1. **Create the GitHub repo** `warrior-women` on his account
   (capitalking0716-cpu) and push this folder to it. (DEPLOY.md Step 1.)
   Shadow has no way to create repos or push to his GitHub from here.
2. **Deploy on Streamlit Community Cloud** (free) — pick the repo, branch
   `main`, file `app.py`. (DEPLOY.md Step 2.) This gives the public URL he
   can post on Instagram and anywhere else.
3. **Add the Stripe secret key** in Streamlit Secrets — the LIVE key
   (`sk_live_...`) from the Vault tec AI Stripe Dashboard → Developers →
   API keys. Then reboot the app. (DEPLOY.md Step 3.) Without this, the
   paywall stays locked on purpose.
4. **Test the live paywall once** — sign up, confirm it stays locked before
   paying, pay $10, confirm it unlocks. (DEPLOY.md Step 4.) Then cancel
   the test subscription in Stripe so he is not charged $10/month for his
   own test.

## Not built yet (future work, not needed to start selling)

- Password reset by email (a member who forgets her password currently
  needs the owner to remove her account row from the database).
- Free trial period.
- Admin view of members.
- Refund / cancel handling inside the app (cancelling happens in Stripe;
  the paywall picks it up automatically on the next check).

## Important limits — read this

- **The app is NOT live yet.** Nothing here is shareable or sellable until
  Neko completes steps 1-3 above. Do not post a link until the deploy is
  done and the paywall test in Step 4 passes.
- **The Stripe check has NOT been tested against live Stripe.** The gating
  logic is proven by tests with a fake Stripe client, but a real paid
  subscription has never been verified against this code. Step 4 of
  DEPLOY.md is the first real test — do it before selling to anyone.
- **Polsia is not involved.** This is a standalone Streamlit app, built
  this way because the Polsia sign-in is broken.
