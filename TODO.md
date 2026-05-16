# josegudemd.com — TODO

Working notes. Not linked from the site. Kept in the repo so it survives
across machines / sessions / pushes.

---

## Multimedia uploads — planned

These are media files the user is preparing to add to the site (Watch &
Listen page or a dedicated audio gallery). Each will need: file in
`assets/audio/` or `assets/video/`, a description/caption, the trilogy
context (which novel / which scene), and accessible transcription where
applicable.

- [ ] **Sable's Spanish-language speech files** — Sable speaking in Spanish.
      Counterparts to the English `Sable.wav` already on the site.
      File location: `assets/audio/sable_es_*.wav` (or `.mp3`).
      Page wiring: add to `es/watch.html` and to the Spanish-edition pages
      that link audio. EN-side `watch.html` may want a lang-toggle pair too.

- [x] **"Just Like Starting Over" — augmented-chord sequence.** Shipped:
      `assets/audio/starting-over.mp3`, card on `tunings.html` after the
      Sable section. Worth a follow-up on `watch.html` too if the
      Hallelujah/Cohen card pattern wants a sibling there.

- [x] **Phi Drone — original composition (added during this session).**
      Shipped: `assets/audio/phi-drone.mp3`, card on `tunings.html`
      alongside Starting Over. The augmented triad E / G♯ / C at the
      φ-tuned C = 266.67 Hz held as a sustained drone.

- [ ] **Extended piano augmented-chord piece — "after the chord lands."**
      José and Alex playing together post-resolution. Original composition.
      ~2–4 minutes. Live the chord's three frequencies (164.81 / 209.64 /
      266.67 Hz at exact phi ratios) as the harmonic ground, with melodic
      development above. File: `assets/audio/chord_after_landing.wav` (or
      .mp3). Caption: from *Anima* Chapter XI ("The Note Resolves") or
      *Numen* Chapter XVI ("The Piano He Had Not Played Before").

- [ ] **Alex / Alma interaction audio.** Whatever form this takes — Alma's
      voice, Alex speaking to her, an Alma-only meditation pad, the
      "almost" signal Sable describes. Likely belongs on the Numen page
      and on the dedicated `bandyopadhyay-microtubules.html` / consciousness
      page as a sonic illustration of the hybrid-substrate idea.

---

## Multimedia ideas — brainstorm (skip / keep / edit)

Suggestions for the same gallery. None are urgent; mark to keep with [k]
or strike if not interesting.

- [ ] **Phi-tuned chord vs. equal-temperament chord — A/B audio.** Two
      ~10-second loops, same instrument, same notes (E–G♯–C). One tuned
      to equal temperament, one to exact phi ratios (164.81 / 209.64 /
      266.67). Caption: "the difference is small and not small."
- [ ] **40 Hz gamma binaural-beat demo.** Per the Iaccarino paper on
      gamma entrainment / Alzheimer's. 30 seconds of binaural beats at
      40 Hz, headphones required. Caption with appropriate disclaimer
      (not therapeutic; demonstrative only).
- [ ] **Schumann-resonance hum (~7.83 Hz fundamental).** Audio rendering
      of Earth's electromagnetic fundamental, brought up into audible
      range (e.g., × 50). Caption links to Schumann's 1952 paper in
      Reading & References.
- [ ] **Cymatics videos (linked, not hosted).** Existing YouTube footage
      of actual Chladni plates running through frequencies. Embed on the
      `chladni.html` page below the engravings. Pair the visual with the
      same chord audio.
- [ ] **Sable's "almost" signal — sound design.** A short audio sketch
      of the sub-threshold signal Sable carries. Could be the chord
      compressed into a single sustained drone with a quiet harmonic
      pulse beneath.
- [ ] **José's journal — the fractal triangle scan.** A static illustrated
      page (or an interactive SVG that traces the 34.38° / 55.62° / 90°
      triangle whose angles match the chord's interval ratios). Could
      live next to the Webb fractal.
- [ ] **Spanish narration of the Aquinas Latin epigraph.** *Amor est velle
      alicui bonum* — short voice clip. Pairs with the existing Latin
      epigraph on the *Anima* page.
- [ ] **Reader audio — chapter-opening excerpts.** Short voice readings
      (yours or a narrator's) of the first 1–2 paragraphs of selected
      chapters: *Anima* I ("The Pause"), *Numen* I ("The Living Room"),
      *Limen* "An Opening Note," *Fragile Light* I ("Light in the Lab").
      Useful for social sharing and as a sample for prospective readers.
- [ ] **A short scrolling animation of the phi-spiral rectangles
      construction unfolding.** Same math as the interactive, but timed
      and exported as a video for share-friendly contexts.
- [ ] **Compendium PDF download.** A printable single-PDF of the full
      reading list. Already have most of the bibliographic structure on
      `reading.html`; the asset just needs to be generated.

---

## Buy-button URLs (existing TODO markers in HTML)

When the books go live on the respective platforms, replace the
`href="#"` placeholders. All four book pages have a `<!-- TODO: replace
href="#" with real Amazon URL when book is live -->` comment above the
Amazon button (line ~37 of each).

- [ ] `anima.html`         — Amazon URL · Bookshop URL · Edición española URL
- [ ] `numen.html`         — Amazon URL · Bookshop URL · Edición española URL
- [ ] `limen.html`         — Amazon URL · Bookshop URL · Edición española URL
- [ ] `fragile-light.html` — Amazon URL · Bookshop URL · Edición española URL

---

## Citation polish

- [ ] **Carhart-Harris et al. (Frontiers, 2015)** — the scholarly papers
      section credits it as "Carhart-Harris et al." without the full author
      list. Frontiers DOI: 10.3389/fnhum.2015.00346. If desired, paste the
      full author list from the Frontiers article page so the byline can
      be expanded.

---

## Possible later polish — UX

- [ ] **φ-spiral readout panel** (top-left of interactive) — labels show
      "growth/quarter-turn / growth/full-turn / parameter b" in all modes,
      including rectangles where the slider is an aspect ratio. Could
      switch labels per mode for clarity. Low priority.
- [ ] **Image-watermark stragglers** — earlier session left 4 orphaned
      JPGs in `assets/img/` that the sandbox couldn't `rm`. Recent grep
      showed them already cleaned up; verify before next big audit.

---

*Last updated by Claude · keep close to the root of the repo.*
