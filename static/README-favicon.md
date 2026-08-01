# Favicon Setup for Yilue's Blog

I've created a basic SVG favicon (`favicon.svg`) and configured it in your Hugo site. The favicon should now appear in browser tabs.

## Current Setup

- ✅ `favicon.svg` - Modern SVG favicon (configured in hugo.toml)
- ✅ `site.webmanifest` - Web app manifest for PWA support
- ⚠️ `favicon.ico` - Placeholder (needs actual ICO file)

## To Complete the Setup

For full browser compatibility, you should generate these additional favicon formats:

### Option 1: Online Favicon Generators
1. Go to https://favicon.io/favicon-converter/
2. Upload the `favicon.svg` file
3. Download the generated package
4. Replace the placeholder files in the `static/` directory

### Option 2: Manual Generation
Generate these files and place them in the `static/` directory:

- `favicon-16x16.png` (16x16 pixels)
- `favicon-32x32.png` (32x32 pixels)
- `apple-touch-icon.png` (180x180 pixels)
- `android-chrome-192x192.png` (192x192 pixels)
- `android-chrome-512x512.png` (512x512 pixels)
- `safari-pinned-tab.svg` (SVG for Safari pinned tabs)

### Option 3: Using ImageMagick (if installed)
```bash
# Convert SVG to PNG formats
convert favicon.svg -resize 16x16 favicon-16x16.png
convert favicon.svg -resize 32x32 favicon-32x32.png
convert favicon.svg -resize 180x180 apple-touch-icon.png
convert favicon.svg -resize 192x192 android-chrome-192x192.png
convert favicon.svg -resize 512x512 android-chrome-512x512.png
```

## Current Configuration

The favicon is configured in `hugo.toml`:
```toml
[params.app]
  svgFavicon = "/favicon.svg"
```

This will use the modern SVG favicon for browsers that support it, with fallbacks to the traditional ICO/PNG formats when available. 