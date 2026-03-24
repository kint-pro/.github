# Kint Logo Assets

## Directory Structure

```
logo/
├── favicon.svg                    # SVG favicon with dark mode support (prefers-color-scheme)
├── favicons/                      # Favicon variants (multiple sizes)
│   ├── favicon.ico                # ICO fallback for older browsers
│   └── favicon-{16..256}.png      # PNG variants
├── logos/                         # Branding variants (SVG + PNG + WebP)
│   ├── kint-logo-black.svg        # Vector logo black (scalable)
│   ├── kint-logo-white.svg        # Vector logo white (scalable)
│   ├── kint-logo-{black,white}-transparent.{png,webp}
│   ├── kint-logo-black-white-bg.{png,webp}
│   └── kint-logo-white-black-bg.{png,webp}
└── pwa/                           # PWA and platform icons
    ├── android-chrome-192x192.png # PWA icon (required)
    ├── android-chrome-512x512.png # PWA icon (required)
    ├── apple-touch-icon.png       # iOS home screen (180x180)
    ├── maskable-icon-192x192.png  # Adaptive icon with safe zone
    ├── maskable-icon-512x512.png  # Adaptive icon with safe zone
    ├── mstile-150x150.png         # Windows tile
    └── mstile-310x310.png         # Windows tile
```

## Which File Goes Where? (Vite + React)

### `public/` — Files with fixed URLs, not processed by the build

Files in `public/` are copied as-is and keep their exact filename. Use for everything referenced by browsers, OS, or crawlers via fixed URLs.

> *"Assets in public/ are served at root path as-is during dev, and copied to the root of the dist directory as-is."*
> — [Vite Docs: Static Asset Handling](https://vite.dev/guide/assets.html#the-public-directory)

| File | Source from this repo | Purpose |
|------|----------------------|---------|
| `favicon.svg` | `favicon.svg` | Modern browsers, dark mode support |
| `favicon.ico` | `favicons/favicon.ico` | Legacy browser fallback |
| `apple-touch-icon.png` | `pwa/apple-touch-icon.png` | iOS home screen bookmark |
| `icons/icon-192x192.png` | `pwa/android-chrome-192x192.png` | PWA manifest.json |
| `icons/icon-512x512.png` | `pwa/android-chrome-512x512.png` | PWA manifest.json |
| `icons/maskable-192x192.png` | `pwa/maskable-icon-192x192.png` | PWA manifest.json (maskable) |
| `icons/maskable-512x512.png` | `pwa/maskable-icon-512x512.png` | PWA manifest.json (maskable) |

### `src/assets/` — Files imported in components

Vite processes these files: hashed filenames for cache busting, inlining of small files, tree shaking.

> *"In general, prefer importing assets unless you specifically need the guarantees provided by the public directory."*
> — [Vite Docs: Static Asset Handling](https://vite.dev/guide/assets.html#the-public-directory)

| File | Source from this repo | Purpose |
|------|----------------------|---------|
| `kint-logo-white.webp` | `logos/kint-logo-white-transparent.webp` | In-app logo (dark background) |
| `kint-logo-black.webp` | `logos/kint-logo-black-transparent.webp` | In-app logo (light background) |

WebP is correct here — served only via `<img>` in components, all modern browsers support WebP.

## Format Requirements by Purpose

### Browser Tab Favicon

| Format | Purpose | Source |
|--------|---------|--------|
| **ICO** (32x32) | Legacy fallback, supported by all browsers | [MDN: Favicon](https://developer.mozilla.org/en-US/docs/Glossary/Favicon) |
| **SVG** | Modern standard, scalable, dark mode via `prefers-color-scheme` | [Evil Martians: How to Favicon](https://evilmartians.com/chronicles/how-to-favicon-in-2021-six-files-that-fit-most-needs) |

WebP is **not** reliably supported as a favicon (Safari, older Firefox).

### PWA Manifest Icons

| Format | Sizes | Source |
|--------|-------|--------|
| **PNG** | 192x192, 512x512 (minimum) | [web.dev: Add a web app manifest](https://web.dev/articles/add-manifest#icons) |
| **PNG maskable** | 192x192, 512x512 (safe zone: 40% radius) | [web.dev: Adaptive icon support](https://web.dev/articles/maskable-icon) |

> *"For Chromium, you must provide at least a 192x192 pixel icon and a 512x512 pixel icon."*
> — [web.dev: Add a web app manifest](https://web.dev/articles/add-manifest#icons)

WebP is technically allowed per [MDN](https://developer.mozilla.org/en-US/docs/Web/Manifest/icons) but unreliable on Safari/WebKit. **Use PNG.**

### Apple Touch Icon

| Format | Size | Source |
|--------|------|--------|
| **PNG** | 180x180 | [Apple Developer: Configuring Web Applications](https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/SafariWebContent/ConfiguringWebApplications/ConfiguringWebApplications.html) |

> *"Place an icon file in PNG format in the root document folder called apple-touch-icon.png."*
> — Apple Developer Documentation

No WebP, no SVG. PNG only. No transparency — Apple applies rounded corners automatically.

### Maskable Icons (PWA)

All important content (logo) must be within the **safe zone**: a circle with **40% radius** from the center.

> *"The important parts of your icon must be within a circular area in the center of the icon with a radius equal to 40% of the icon width."*
> — [web.dev: Maskable Icon](https://web.dev/articles/maskable-icon)

Test tool: [maskable.app](https://maskable.app/)

### Open Graph / Social Media

| Format | Size | Source |
|--------|------|--------|
| **PNG** or **JPEG** | 1200x630 | [Open Graph Protocol](https://ogp.me/) |

| File | Size | Purpose |
|------|------|---------|
| `og-image.png` | 1200x630 | Black logo on white — default for light contexts |
| `og-image-dark.png` | 1200x630 | White logo on dark — alternative for dark contexts |
