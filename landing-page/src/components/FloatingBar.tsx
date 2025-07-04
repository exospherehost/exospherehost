import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaGithub, FaLinkedin, FaWhatsapp, FaCalendarAlt, FaBlog } from 'react-icons/fa';
import Image from 'next/image';
import { darkerGrotesque } from "@/lib/fonts";

interface TooltipProps {
  text: string;
  children: React.ReactNode;
}

const Tooltip = ({ text, children }: TooltipProps) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div 
      className="relative"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {children}
      <AnimatePresence>
        {isHovered && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ duration: 0.2 }}
            className={`absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-1.5 bg-[#031035]/40 backdrop-blur-sm rounded-lg text-sm text-white whitespace-nowrap border border-[#7FD6FF]/30 ${darkerGrotesque.className}`}
          >
            {text}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

const FloatingBar = () => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.scrollY;
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;
      
      // Show bar when scrolled past 100px and not at the bottom
      const isAtBottom = windowHeight + scrollPosition >= documentHeight - 100;
      setIsVisible(scrollPosition > 100 && !isAtBottom);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 100, opacity: 0 }}
          transition={{ duration: 0.3 }}
          className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50"
        >
          <div className="bg-[#031035]/40 backdrop-blur-sm px-8 py-4 rounded-full border border-[#7FD6FF]/20 shadow-[0_0_15px_rgba(127,214,255,0.1)] flex gap-8 items-center">
            {/* Exosphere Logo */}
            <Tooltip text="Home">
              <a href="/" className="text-[#7FD6FF] hover:text-white transition-colors">
                <Image 
                  src="/exospheresmall.png" 
                  alt="Exosphere" 
                  width={24} 
                  height={24}
                  className="hover:opacity-80 transition-opacity"
                />
              </a>
            </Tooltip>

            {/* Book a Call */}
            <Tooltip text="Book a Call">
              <a href="https://forms.gle/rxz1oPxLk34jfr2g7" target="_blank" rel="noopener noreferrer" className="text-[#7FD6FF] hover:text-white transition-colors">
                <FaCalendarAlt size={20} />
              </a>
            </Tooltip>

            {/* GitHub */}
            <Tooltip text="GitHub">
              <a href="https://github.com/exosphere-host" target="_blank" rel="noopener noreferrer" className="text-[#7FD6FF] hover:text-white transition-colors">
                <FaGithub size={20} />
              </a>
            </Tooltip>

            {/* WhatsApp */}
            {/* <Tooltip text="WhatsApp">
              <a href="https://wa.me/your-number" target="_blank" rel="noopener noreferrer" className="text-[#7FD6FF] hover:text-white transition-colors">
                <FaWhatsapp size={20} />
              </a>
            </Tooltip> */}

            {/* LinkedIn */}
            <Tooltip text="LinkedIn">
              <a href="https://www.linkedin.com/company/exosphere-host/" target="_blank" rel="noopener noreferrer" className="text-[#7FD6FF] hover:text-white transition-colors">
                <FaLinkedin size={20} />
              </a>
            </Tooltip>

            {/* Blog */}
            <Tooltip text="Blog">
              <a href="/blog" className="text-[#7FD6FF] hover:text-white transition-colors">
                <FaBlog size={20} />
              </a>
            </Tooltip>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default FloatingBar; 