import type { Metadata } from "next";
import { darkerGrotesque, pattanakarn } from '../lib/fonts';
import "./globals.css";
import { GoogleAnalytics } from '@next/third-parties/google'

export const metadata: Metadata = {
  title: "Exosphere | Async AI Workflows at Scale",
  description:
    "Exosphere powers background job processing for inference models so you can run AI workloads efficiently, reliably, and cost-effectively.",
  keywords: [
    "async AI workflows",
    "background jobs",
    "inference models",
    "machine learning",
    "model deployment",
    "batch processing",
    "job orchestration",
    "batch jobs",
    "batch inference",
    "open source model orchestration",
    "async model orchestration",
    "async model execution",
    "async model deployment",
    "async model processing",
    "async model scheduling",
    
  ],
  authors: [{ name: "Exosphere" }],
  creator: "Exosphere",
  publisher: "Exosphere",
  robots: {
    index: true,
    follow: true
  },  
  icons: {
    icon: '/exospheresmall.png',
    apple: '/exospheresmall.png',
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://exosphere.host',
    siteName: "Exosphere",
    title: "Exosphere | Async AI Workflows at Scale",
    description: "Scale your AI workloads with Exosphere’s robust background processing platform for inference models.",
    images: [
      {
        url: '/exospheresmall.png',
        width: 1200,
        height: 630,
        alt: 'Exosphere Logo',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: "Exosphere | Async AI Workflows at Scale",
    description:"Run and scale inference models effortlessly with Exosphere’s background job engine.",
    images: ['/exospheresmall.png'],
    creator: '@exosphere',
  }  
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${darkerGrotesque.variable} ${pattanakarn.variable} antialiased`}
      >
        {children}
        <GoogleAnalytics gaId="G-XY9H2PN0ZX" />
      </body>
    </html>
  );
}
