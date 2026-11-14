# Warrior Women — Deploy Guide (Streamlit Community Cloud, free)

This app is ready to deploy. Deploying needs two accounts Neko must use
himself — Muse cannot create them for him:

1. **GitHub** (free) — to hold the code. Neko's account: `capitalking0716-cpu`.
2. **Streamlit Community Cloud** (free) — to run the app on the web.

No money is needed for either. The only paid piece is the Stripe key
below, and that costs nothing to create — it is the key to Neko's own
Stripe account, which already exists.

## Step 1 — Create the GitHub repo

On github.com, create a **new public repository** called `warrior-women`
(do not add a README or license there — this folder already has them).

Then, from this folder on a PC with git installed:

```bash
cd warrior-women
git init
git add .
git commit -m "Warrior Women membership app v1.0 — $10/month, Stripe paywall"
git remote add origin https://github.com/capitalking0716-cpu/warrior-women.git
git branch -M main
git push -u origin main
```

**Check before you move on:** open the repo on github.com and confirm
`app.py`, `requirements.txt`, `warrior_women/` and `tests/` are all there.
The `data/` folder and `.venv/` must NOT be in the repo (they are gitignored
— member data and local installs never go on GitHub).

## Step 2 — Deploy on Streamlit Community Cloud

1. Go to https://share.streamlit.io and sign in **with GitHub**.
2. Click **Create app** → pick repository `warrior-women`, branch `main`,
   main file `app.py`.
3. Click **Deploy**. The app builds for a minute or two, then gives you a
   public URL like `https://warrior-women.streamlit.app`.

That URL is the public app. Anyone can open it, sign up, and pay. Post it
anywhere — Instagram, TikTok, anywhere you sell.

## Step 3 — Add the Stripe secret key (turns the paywall on)

Until this step is done, the app runs but the member area stays locked with
a message that payment verification is not set up yet. That is by design.

1. Go to the Stripe Dashboard (https://dashboard.stripe.com) and sign in
   to the **Vault tec AI** account (the same account the $10/month checkout
   link lives in).
2. Go to **Developers → API keys**.
3. Under **Secret key**, click **Reveal live key** and copy it. It starts
   with `sk_live_` — use the **live** key, not the test key, because the
   $10/month price and checkout link are live.
4. In Streamlit Cloud, open the app → **Settings → Secrets** and add:

```toml
STRIPE_SECRET_KEY = "sk_live_paste_your_key_here"
```

5. Click **Save**, then **Reboot** the app.

**Rules for the key:**
- Never type it in chat, never put it in any file in this repo, never share
  it. It lives only in Streamlit Secrets.
- If it ever leaks, revoke it in the Stripe Dashboard and make a new one.

## Step 4 — Test the live paywall (do this once)

1. Open the public app URL on your phone.
2. Create an account with your own email (use the work email,
   capitalking0716@gmail.com, or any email you control).
3. Before paying, confirm the app shows **"Membership required"** and does
   NOT let you into the program. If it lets you in without paying, stop —
   something is wrong, do not sell it yet.
4. Tap **Subscribe — $10/month**, pay with a real card (this is a real
   $10 charge — it is your own product, so it comes back to your Stripe
   account minus Stripe's fee).
5. Go back to the app, tap **Check my subscription**. It should unlock and
   show the full program.
6. If it does not unlock: check the email on the Stripe payment matches the
   account email exactly, then check the key is the live key and the app was
   rebooted after adding it.

After that test, the $10 you paid is a real subscription — cancel it in
Stripe (Dashboard → Customers → your email → cancel subscription) so you
are not charged $10 every month for your own test, or keep it if you want
your own member account.

## What members do

1. Open the app link, read the landing page.
2. Create an account (email + password) — **same email they will pay with**.
3. Subscribe ($10/month) through the checkout link.
4. Tap **Check my subscription** — the program unlocks.
5. Onboarding (their details, gym equipment, rest day), then Day 1 of the
   seven-day re-entry week.

## If something goes wrong

- **"Payment verification is not set up yet"** — the Stripe key is missing
  from Secrets. Repeat Step 3 and reboot.
- **Paid but still locked** — email mismatch is the usual cause. The
  account email and the Stripe payment email must match exactly.
- **App will not start on Streamlit Cloud** — check the Cloud logs for the
  error; usually a missing file in the repo or a typo in Secrets.
- **Forgot the login password** — there is no password reset yet. (A reset
  flow is a future addition; for now, a member who forgets her password
  needs the owner to delete her row from the database.)
