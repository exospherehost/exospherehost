import Link from 'next/link'
import Image from 'next/image'
import { darkerGrotesque, pattanakarn } from '../lib/fonts'

const Footer = () => {
  return (
    <footer className="relative w-full py-2 mt-20 border-[#7FD6FF]/20">
      <div className="max-w-7xl mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Company Info */}
          <div className="space-y-4">
            <div className="relative w-32 h-8">
              <Image
                src="/exospherelogo.png"
                alt="Exosphere Logo"
                width={250}
                height={250}
                className="object-contain"
                priority
              />
            </div>
            <p className={`text-[#8bdfff] text-lg ${darkerGrotesque.className}`}>
            The platform for async AI workflows
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className={`text-white text-lg mb-4 ${pattanakarn.className}`}>legal</h4>
            <ul className="space-y-2">
              <li><Link href="/terms" className={`text-[#8bdfff] hover:text-white transition-colors ${darkerGrotesque.className}`}>Terms & Conditions</Link></li>
              <li><Link href="/privacy" className={`text-[#8bdfff] hover:text-white transition-colors ${darkerGrotesque.className}`}>Privacy Policy</Link></li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className={`text-white text-lg mb-4 ${pattanakarn.className}`}>quick links</h4>
            <ul className="space-y-2">
              <li><Link href="https://docs.exosphere.host/" className={`text-[#8bdfff] hover:text-white transition-colors ${darkerGrotesque.className}`}>Documentation</Link></li>
              <li><Link href="/blog" className={`text-[#8bdfff] hover:text-white transition-colors ${darkerGrotesque.className}`}>Blog</Link></li>
              <li><Link href="https://calendly.com/nikita-exosphere/exosphere-intro" className={`text-[#8bdfff] hover:text-white transition-colors ${darkerGrotesque.className}`}>Support</Link></li>
            </ul>
          </div>

          {/* Social Links */}
          <div>
            <h4 className={`text-white text-lg mb-4 ${pattanakarn.className}`}>connect</h4>
            <div className="flex space-x-4">
              <a href="https://x.com/exospherehost" target="_blank" rel="noopener noreferrer" className="text-[#8bdfff] hover:text-white transition-colors">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                </svg>
              </a>
              <a href="https://github.com/exospherehost" target="_blank" rel="noopener noreferrer" className="text-[#8bdfff] hover:text-white transition-colors">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                </svg>
              </a>
              <a href="https://www.linkedin.com/company/exospherehost/" target="_blank" rel="noopener noreferrer" className="text-[#8bdfff] hover:text-white transition-colors">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
                </svg>
              </a>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-12 pt-8 border-t border-[#7FD6FF]/10">
          <div className="flex flex-col md:flex-row justify-center items-center gap-4">
            <p className={`${darkerGrotesque.className} text-center text-[#8bdfff] text-md`}>
              © {new Date().getFullYear()} Mathrithms Technologies Pvt Ltd. All rights reserved.
            </p>            
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer 