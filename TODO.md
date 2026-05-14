- [x] Gather current responsive/performance issues across invitation templates (home, details, rsvp, video)
- [x] Brainstorm mobile-first responsive optimization plan (CSS + minimal JS)
- [x] Implement CSS refactor: mobile-first breakpoints, clamp typography, safe-area padding, overflow fixes, reduced blur on mobile
- [x] Implement mobile performance guardrails in JS: reduced sparkle/particle counts, disable mouse parallax/3D on touch devices, respect prefers-reduced-motion

- [ ] Responsive hero: split on desktop, stacked text-centered on mobile + simplified 3D
- [ ] Responsive video: mobile-safe playback (playsinline, poster fallback), reduce particles & disable heavy scroll transforms on mobile
- [ ] Responsive RSVP + guest list: touch-friendly inputs, convert table to cards on mobile if applicable
- [ ] Add lazy loading to images and reduce image requests/sizes via srcset (where possible)
- [x] Run Django system checks and test suite (0 tests)
- [ ] Apply responsive/performance optimization to details.html, rsvp.html, guest_list.html, and video.html



