'use client';

import Link from 'next/link';
import Image from 'next/image';
import { darkerGrotesque } from '../lib/fonts';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <nav className="relative z-20 w-full flex justify-center">
      <div className="bg-[#314877]/0 rounded-full px-4 md:px-10 py-4 md:py-8 flex items-center w-[90vw] max-w-6xl justify-between border-none shadow-none">
        <div className="flex items-center space-x-4">
          <Link href="/">
            <img src="/exospherelogo1.png" alt="Exosphere Logo" className="h-6 md:h-10" />
          </Link>
        </div>
        
        {/* Hamburger Menu Button */}
        <button 
          className="md:hidden text-[#8bdfff] hover:text-white transition-colors"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {isMenuOpen ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>

        {/* Desktop Menu */}
        <div className="hidden md:flex items-center space-x-10">
          <a href="/blog" className={`${darkerGrotesque.className} text-[#8bdfff] hover:text-white transition-colors font-normal text-xl tracking-wide`}>Blog</a>
          <a href="https://demo.exosphere.host" className={`${darkerGrotesque.className} text-[#8bdfff] hover:text-white transition-colors font-normal text-xl tracking-wide`}>Demo</a>
          <a href="https://forms.gle/rxz1oPxLk34jfr2g7" className={`${darkerGrotesque.className} text-[#e4587d] hover:text-white transition-colors font-bold text-xl tracking-wide`}>Book a Call</a>          
        </div>

        {/* Mobile Menu */}
        <AnimatePresence>
          {isMenuOpen && (
            <motion.div
              key="mobile-menu"
              initial={{ opacity: 0, y: -24 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -24 }}
              transition={{ duration: 0.3, ease: 'easeInOut' }}
              className="md:hidden absolute top-full left-0 right-0 bg-[#031035]/10 backdrop-blur-md border border-[#daf5ff]/20 shadow-lg flex flex-col items-center space-y-3 py-6 rounded-b-2xl z-30"
            >
              <a href="/blog" className={`${darkerGrotesque.className} text-[#8bdfff] hover:text-white transition-colors font-normal text-xl tracking-wide`}>Blog</a>
              <a href="https://demo.exosphere.host" className={`${darkerGrotesque.className} text-[#8bdfff] hover:text-white transition-colors font-normal text-xl tracking-wide`}>Demo</a>
              <a href="https://forms.gle/rxz1oPxLk34jfr2g7" className={`${darkerGrotesque.className} text-[#e4587d] hover:text-white transition-colors font-bold text-xl tracking-wide`}>Book a Call</a>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </nav>
  );
} 