# Deploying josegudemd.com to GitHub Pages

This is a static site — no build step, no server. Drop it on GitHub Pages and you're live.

## 1. Create the repo

On GitHub (as user `gude2000`):

- Repo name: **`gude2000.github.io`**  
  (Naming the repo this way makes it your "user site" — it serves at the root of your domain instead of `/<reponame>/`.)
- Visibility: public (required for free GitHub Pages)
- Don't initialize with a README — we'll push from local

## 2. Push the site

From this folder:

```bash
git init
git add .
git commit -m "Initial site"
git branch -M main
git remote add origin https://github.com/gude2000/gude2000.github.io.git
git push -u origin main
```

GitHub Pages will auto-build on push. Within ~1 minute the site is live at:

- https://gude2000.github.io/

## 3. Connect the josegudemd.com domain

### a. In GitHub (one-time)

Repo → **Settings** → **Pages** → **Custom domain** → enter `josegudemd.com` → Save.

GitHub will create the `CNAME` file in the repo automatically (we've already included one — leave it).

### b. In Namecheap (one-time)

Domain List → **Manage** → **Advanced DNS**. Add these records:

| Type     | Host  | Value                       | TTL     |
|----------|-------|-----------------------------|---------|
| A Record | @     | 185.199.108.153             | Auto    |
| A Record | @     | 185.199.109.153             | Auto    |
| A Record | @     | 185.199.110.153             | Auto    |
| A Record | @     | 185.199.111.153             | Auto    |
| CNAME    | www   | gude2000.github.io          | Auto    |

Delete any existing parked-domain records that conflict.

### c. Wait

DNS propagates in 5–60 minutes (rarely longer). Back in GitHub Pages settings, once DNS is detected you'll see a green check and a "Enforce HTTPS" option. **Tick that box** — Let's Encrypt will issue a free certificate automatically.

The site is now live at https://josegudemd.com and https://www.josegudemd.com.

## 4. Updating the site

Every change is just `git add . && git commit -m "..." && git push`. GitHub Pages re-deploys within a minute.

## File map

```
index.html             ← Home (all four books)
anima.html             ← Anima
numen.html             ← Numen
limen.html             ← Limen
fragile-light.html     ← Fragile Light
reading.html           ← Bibliography
watch.html             ← Music / talks / films
about.html             ← Author bio + contact
assets/css/style.css   ← All styling
assets/img/            ← Cover JPGs
CNAME                  ← Custom domain (do not delete)
```

## Buy buttons

The `Amazon` / `IngramSpark` / `Signed copy` buttons on each book page have `href="#"` placeholders. Replace with the actual purchase URLs when ready:

- Amazon: the book's product page URL after KDP publishes
- IngramSpark: your IngramSpark public product page (or `https://www.ingramspark.com/`)
- Signed copy: a Payhip / Lemon Squeezy / Gumroad checkout link

For Payhip (recommended):
- Sign up at payhip.com (free, ~5% per sale, no monthly fee)
- Create a product with a buy button → copy the URL
- Replace the `href="#"` on the relevant button
