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
          <a href="https://github.com/exospherehost/exospherehost" target="_blank" rel="noopener noreferrer" className="text-[#8bdfff] hover:text-white transition-colors">
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
            </svg>
          </a>
          <a href="https://docs.exosphere.host/" target="_blank" rel="noopener noreferrer" className={`${darkerGrotesque.className} text-[#8bdfff] hover:text-white transition-colors font-normal text-xl tracking-wide`}>Docs</a>
          <a href="/blog" className={`${darkerGrotesque.className} text-[#8bdfff] hover:text-white transition-colors font-normal text-xl tracking-wide`}>Blog</a>
          <a href="https://demo.exosphere.host"  target="_blank" rel="noopener noreferrer" className={`${darkerGrotesque.className} text-[#8bdfff] hover:text-white transition-colors font-normal text-xl tracking-wide`}>Demo</a>
          <a href="https://calendly.com/nikita-exosphere/exosphere-intro"  target="_blank" rel="noopener noreferrer" className={`${darkerGrotesque.className} text-[#e4587d] hover:text-white transition-colors font-bold text-xl tracking-wide`}>Book a Call</a>   
          
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
              <a href="https://github.com/exospherehost/exospherehost" target="_blank" rel="noopener noreferrer" className="text-[#8bdfff] hover:text-white transition-colors">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                </svg>
              </a>
              <a href="/blog" className={`${darkerGrotesque.className} text-[#8bdfff] hover:text-white transition-colors font-normal text-xl tracking-wide`}>Blog</a>
              <a href="https://demo.exosphere.host" className={`${darkerGrotesque.className} text-[#8bdfff] hover:text-white transition-colors font-normal text-xl tracking-wide`}>Demo</a>
              <a href="https://calendly.com/nikita-exosphere/exosphere-intro" className={`${darkerGrotesque.className} text-[#e4587d] hover:text-white transition-colors font-bold text-xl tracking-wide`}>Book a Call</a>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </nav>
  );
} 