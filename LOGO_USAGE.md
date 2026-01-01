# Natpudan AI Logo Usage Guide

## Files Created

1. **`NatpudanLogo.tsx`** - React component with two variants
2. **`logo-icon.svg`** - Standalone icon SVG (80x80)
3. **`logo-full.svg`** - Full logo with text (400x100)

## Usage Examples

### 1. Using the React Component

```tsx
import NatpudanLogo from './components/NatpudanLogo';

// Icon only (perfect for app bar, favicon)
<NatpudanLogo variant="icon" sx={{ fontSize: 40 }} />

// Full logo with text (for landing page, header)
<NatpudanLogo variant="full" />

// With custom colors
<NatpudanLogo variant="icon" sx={{ fontSize: 60, color: 'primary.main' }} />
```

### 2. Using Standalone SVG Files

```tsx
// In HTML
<img src="/logo-icon.svg" alt="Natpudan AI" width="80" height="80" />
<img src="/logo-full.svg" alt="Natpudan AI" width="400" height="100" />

// As favicon in index.html
<link rel="icon" type="image/svg+xml" href="/logo-icon.svg" />
```

### 3. Common Use Cases

**App Bar / Navigation:**
```tsx
<AppBar>
  <Toolbar>
    <NatpudanLogo variant="icon" sx={{ mr: 2, fontSize: 32 }} />
    <Typography variant="h6">Natpudan AI</Typography>
  </Toolbar>
</AppBar>
```

**Landing Page Header:**
```tsx
<Box sx={{ textAlign: 'center', py: 4 }}>
  <NatpudanLogo variant="full" />
</Box>
```

**Login/Register Pages:**
```tsx
<Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
  <NatpudanLogo variant="icon" sx={{ fontSize: 80 }} />
</Box>
```

## Logo Features

- **Medical Cross**: Represents healthcare focus
- **AI Circuit Nodes**: Symbolizes artificial intelligence
- **Blue-Green Gradient**: Blue (trust/medical) + Green (health/growth)
- **HD Quality**: Vector-based, scalable to any size without quality loss
- **Responsive**: Works perfectly at any resolution

## Color Palette

- Primary Blue: `#1976d2` → `#2196f3`
- Accent Green: `#4caf50` → `#8bc34a`
- White highlights for contrast

## Export Options

The SVG files can be:
- Used directly in web applications
- Converted to PNG/JPG at any resolution using tools like Inkscape or online converters
- Imported into design tools (Figma, Adobe Illustrator, etc.)
- Used as favicon, app icons, or social media images

## Recommended Sizes

- **Favicon**: 32x32, 64x64
- **App Icon**: 192x192, 512x512
- **Social Media**: 1200x630 (Facebook), 1024x512 (Twitter)
- **GitHub**: 400x400 for repository social preview
