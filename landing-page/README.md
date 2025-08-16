# ExosphereHost Landing Page

The official landing page for ExosphereHost - an open-source infrastructure layer for background AI workflows and agents. Built with Next.js 15, TypeScript, and Tailwind CSS.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ 
- npm, yarn, pnpm, or bun

### Installation

1. **Navigate to the landing page directory:**
   ```bash
   cd landing-page
   ```

2. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   # or
   bun install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   # or
   yarn dev
   # or
   pnpm dev
   # or
   bun dev
   ```

4. **Open in browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🏗️ Project Structure

```
landing-page/
├── 📁 src/
│   ├── 📁 app/              # Next.js 15 app router
│   ├── 📁 components/       # React components
│   ├── 📁 lib/             # Utility functions
│   └── 📁 styles/          # CSS and styling
├── 📁 public/              # Static assets
│   ├── 🖼️ images/         # Images and icons
│   └── 📄 favicon.ico      # Favicon
├── 📄 next.config.ts       # Next.js configuration
├── 📄 tailwind.config.js   # Tailwind CSS configuration
├── 📄 tsconfig.json        # TypeScript configuration
└── 📄 package.json         # Dependencies and scripts
```

## 🎨 Features

### Current Features
- **🌟 Hero Section**: Compelling introduction to ExosphereHost
- **🛰️ Satellite Showcase**: Interactive demonstration of satellite capabilities
- **📊 Architecture Overview**: Visual representation of the platform architecture
- **💰 Pricing Information**: Transparent pricing with cost savings calculator
- **📚 Documentation Links**: Easy access to comprehensive documentation
- **🤝 Community Section**: Links to Discord, GitHub, and social media

### Responsive Design
- **📱 Mobile First**: Optimized for mobile devices
- **💻 Desktop Enhanced**: Rich experience on larger screens
- **🎯 Accessibility**: WCAG compliant with proper contrast and navigation

### Performance Optimizations
- **⚡ Next.js 15**: Latest framework features and optimizations
- **🖼️ Image Optimization**: Automatic image optimization and WebP conversion
- **📦 Code Splitting**: Automatic code splitting for faster loading
- **🔄 Static Generation**: Pre-rendered pages for better performance

## 🛠️ Development

### Available Scripts

```bash
# Development server
npm run dev

# Production build
npm run build

# Start production server
npm run start

# Lint code
npm run lint

# Type checking
npm run type-check

# Format code
npm run format
```

### Environment Variables

Create a `.env.local` file for local development:

```bash
# Analytics
NEXT_PUBLIC_GA_ID=your-google-analytics-id
NEXT_PUBLIC_HOTJAR_ID=your-hotjar-id

# API Endpoints
NEXT_PUBLIC_API_URL=https://api.exosphere.host
NEXT_PUBLIC_DOCS_URL=https://docs.exosphere.host

# Feature Flags
NEXT_PUBLIC_SHOW_PRICING=true
NEXT_PUBLIC_SHOW_BETA_BANNER=true
```

### Styling

The landing page uses **Tailwind CSS** for styling with a custom design system:

```css
/* Custom color palette */
:root {
  --color-primary: #6366f1;      /* Indigo */
  --color-secondary: #8b5cf6;    /* Purple */
  --color-accent: #06b6d4;       /* Cyan */
  --color-success: #10b981;      /* Emerald */
  --color-warning: #f59e0b;      /* Amber */
  --color-error: #ef4444;        /* Red */
}
```

### Components

#### Key Components
- `HeroSection`: Main landing section with CTA
- `SatelliteDemo`: Interactive satellite showcase
- `ArchitectureDiagram`: Platform architecture visualization
- `PricingCalculator`: Cost savings calculator
- `TestimonialSlider`: Customer testimonials
- `NewsletterSignup`: Email subscription form

#### Component Guidelines
- Use TypeScript for all components
- Follow the existing naming conventions
- Include proper prop types and documentation
- Implement responsive design patterns
- Add accessibility attributes (ARIA labels, etc.)

## 📈 Analytics and Tracking

### Google Analytics
The landing page includes Google Analytics 4 tracking for:
- Page views and user sessions
- Conversion tracking for signups
- Performance metrics
- User behavior analysis

### Hotjar Integration
User experience tracking with:
- Heatmaps for user interaction patterns
- Session recordings for UX optimization
- Feedback polls and surveys
- Conversion funnel analysis

## 🚀 Deployment

### Vercel Deployment (Recommended)

1. **Connect to Vercel:**
   ```bash
   npx vercel
   ```

2. **Configure environment variables** in the Vercel dashboard

3. **Deploy:**
   ```bash
   vercel --prod
   ```

### Docker Deployment

1. **Build the Docker image:**
   ```bash
   docker build -t exosphere-landing-page .
   ```

2. **Run the container:**
   ```bash
   docker run -p 3000:3000 exosphere-landing-page
   ```

### Static Export

For static hosting (Netlify, GitHub Pages, etc.):

```bash
npm run build
npm run export
```

## 🔧 Configuration

### Next.js Configuration

```typescript
// next.config.ts
const nextConfig = {
  experimental: {
    appDir: true,
  },
  images: {
    domains: ['assets.exosphere.host'],
    formats: ['image/webp', 'image/avif'],
  },
  async redirects() {
    return [
      {
        source: '/docs',
        destination: 'https://docs.exosphere.host',
        permanent: true,
      },
    ]
  },
}
```

### Tailwind Configuration

```javascript
// tailwind.config.js
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#6366f1',
        secondary: '#8b5cf6',
        accent: '#06b6d4',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
  ],
}
```

## 🎯 SEO Optimization

### Meta Tags
- Comprehensive Open Graph tags
- Twitter Card optimization
- Structured data (JSON-LD)
- Canonical URLs
- Meta descriptions and keywords

### Performance
- Core Web Vitals optimization
- Image optimization and lazy loading
- Font optimization with next/font
- Critical CSS inlining
- Service worker for caching

## 🧪 Testing

### Unit Testing
```bash
npm run test
```

### E2E Testing
```bash
npm run test:e2e
```

### Accessibility Testing
```bash
npm run test:a11y
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/landing-page-enhancement`
3. **Make your changes** following the style guide
4. **Test your changes** thoroughly
5. **Update documentation** as needed
6. **Submit a pull request**

### Style Guide
- Use semantic HTML elements
- Follow accessibility best practices
- Maintain consistent component structure
- Use TypeScript for type safety
- Follow the existing CSS class naming conventions

## 📄 License

This landing page is part of the ExosphereHost project and is licensed under the Elastic License 2.0 (ELv2).

## 📞 Support

For landing page specific issues:
- **GitHub Issues**: [Create an issue](https://github.com/exospherehost/exospherehost/issues)
- **Email**: [nivedit@exosphere.host](mailto:nivedit@exosphere.host)
- **Discord**: [Join our community](https://discord.gg/JzCT6HRN)

---

**Showcasing the future of AI infrastructure 🌟**
