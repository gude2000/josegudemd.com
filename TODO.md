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

- [x] **Sable's Spanish-language speech files** — Shipped:
      `assets/audio/sable-es.mp3` (~225 KB). Wired into the Spanish Sable
      Speak card on `es/tunings.html` — the existing JS already tried
      `../assets/audio/sable-es.mp3` first before falling back to the
      English `sable.mp3` or to system TTS. Updated the loading-status
      strings to drop the obsolete "Sable.wav" filename reference.
      Pending: similar wiring in `es/watch.html` if the audio gallery
      grows there too.

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

- [x] **Phi-tuned chord vs. equal-temperament chord — A/B audio.** Shipped:
      `assets/audio/phi-vs-et-et.mp3` and `phi-vs-et-phi.mp3` (10 s each,
      sine waves, both anchored at E 164.81 Hz). 12-TET stack at G♯ 207.65 /
      C 261.63 vs. φ-stack at 209.64 / 266.67. Card on `tunings.html` between
      the Schumann-hum card and the José/Alex chord. Built by
      `scripts/build_audio.py`.
- [x] **40 Hz gamma binaural-beat demo.** Shipped: new `t10` card on
      `tunings.html`, 200 Hz / 240 Hz panned hard L/R, perceived 40 Hz
      difference. Caption cites Iaccarino 2016 / Martorell 2019 and links
      to the Bioelectromagnetism subsection in `reading.html`.
- [x] **Schumann-resonance hum (~7.83 Hz fundamental).** Shipped:
      `assets/audio/schumann-hum.mp3` (45 s stereo). Five Schumann cavity
      modes (7.83, 14.3, 20.8, 27.3, 33.8 Hz) multiplied × 50 into the
      hearing band (391.5 / 715 / 1040 / 1365 / 1690 Hz) with decreasing
      amplitude per partial, a 7.83 Hz amplitude modulation riding on the
      sum to reproduce the cavity-mode rhythm, slow L/R detune for stereo
      width, and a gentle low-pass. Card on `tunings.html` after the
      Schumann binaural-beat card; links to `schumann-resonance.html`.
- [x] **Cymatics videos (linked, not hosted).** Shipped: "Cymatics in motion"
      section on `chladni.html` after the modern-plates photo. Single embedded
      YouTube player (video ID `wvJAgrUBF4w`) plus a row of ten timestamp
      buttons (0:00 · 1:00 · 1:10 · 1:18 · 1:26 · 1:37 · 1:50 · 1:53 · 2:02 ·
      2:09) that scrub the player to different cymatic modes.
- [x] **Sable's "almost" signal — sound design.** Shipped:
      `assets/audio/sable-almost.mp3` (50 s, stereo, ~575 KB). Synthesized
      drone with the phi-tuned augmented architecture (C/E/G♯ at 266.67 Hz
      and its octaves), slow tremolo per voice, soft noise floor, and a
      gaussian-shaped harmonic bloom every 9.5 seconds — the "almost"
      pulse. Stereo swirl on a high partial. Card on `tunings.html`
      between the Sable speak card and the two recordings.
- [x] **José's journal — the fractal triangle.** Shipped: interactive SVG
      at `assets/webb-triangle.html` with nested φ-similar triangles, angle
      markers, vertex-labels (90° · 55.62° · 34.38° → C / G♯ / E), per-note
      click-to-play, and a "play full chord" button. Embedded on
      `reading.html` as the second iframe right after the Webb fractal.
- [x] **Aquinas Latin epigraph — spoken (alternating 2-way).** Shipped:
      card on `tunings.html` with a "speak the Latin" button. Each click
      alternates between two voices: `assets/audio/aquinas-v2.mp3` (the
      author's recorded take, 4.13 s) and an Italian-female SpeechSynthesis
      voice (filtered by name hints — Alice/Federica/Lucia/Elsa/etc — and
      falling back to any installed Italian voice, then to default).
      Earlier `aquinas.mp3` and the two 0-byte gTTS placeholders in
      `assets/audio/` are still on disk; safe to `git rm` whenever.
- [ ] **Reader audio — chapter-opening excerpts.** Short voice readings
      (yours or a narrator's) of the first 1–2 paragraphs of selected
      chapters: *Anima* I ("The Pause"), *Numen* I ("The Living Room"),
      *Limen* "An Opening Note," *Fragile Light* I ("Light in the Lab").
      Useful for social sharing and as a sample for prospective readers.
- [ ] **A short scrolling animation of the phi-spiral rectangles
      construction unfolding.** Same math as the interactive, but timed
      and exported as a video for share-friendly contexts.
- [x] **Compendium PDF download.** Shipped: `assets/compendium.pdf` (~205 KB,
      28 pages, 16 sections, 130+ entries). Generator script at
      `scripts/build_compendium.py` parses `reading.html` with BeautifulSoup
      and renders via ReportLab Platypus (DejaVu Sans for full Unicode glyph
      coverage — φ, ↗, chord sharps all render). Download button on
      `reading.html` above the Webb interactives.

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
