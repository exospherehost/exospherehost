"use client"

import Navbar from "@/components/Navbar"
import Stars from "@/components/Stars"
import PulsatingGradient from "@/components/PulsatingGradient"
import { darkerGrotesque, pattanakarn } from "@/lib/fonts"
import OrbitalSystem from "@/components/OrbitalSystem"
import BookCallCTA from "@/components/BookCallCTA"
import dynamic from 'next/dynamic'
import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'

const Features = dynamic(() => import("@/components/Features").then(mod => mod.Features))
const BenchmarkingSection = dynamic(() => import("@/components/BenchmarkingSection"))
const Footer = dynamic(() => import("@/components/Footer"))
const FloatingBar = dynamic(() => import("@/components/FloatingBar"))
const CodeComparisonDemo = dynamic(() => import("@/components/code").then(mod => mod.CodeComparisonDemo))
const BlogSection = dynamic(() => import("@/components/BlogSection"))

export default function Exosphere() {
  const featuresRef = useRef(null)
  const codeRef = useRef(null)
  const benchmarkRef = useRef(null)
  const blogRef = useRef(null)
  const ctaRef = useRef(null)
  const videoRef = useRef(null)

  const featuresInView = useInView(featuresRef, { once: true, margin: "-100px" })
  const codeInView = useInView(codeRef, { once: true, margin: "-100px" })
  const benchmarkInView = useInView(benchmarkRef, { once: true, margin: "-100px" })
  const blogInView = useInView(blogRef, { once: true, margin: "-100px" })
  const ctaInView = useInView(ctaRef, { once: true, margin: "-100px" })
  const videoInView = useInView(videoRef, { once: true, margin: "-100px" })

  return (
    <div className="w-full h-screen relative bg-[#031035]">
      <PulsatingGradient />
      {/* Twinkling Stars */}
      <Stars />

      <div className="relative z-100">
        <Navbar />       
      </div>

      <OrbitalSystem />
     
      <div className="w-full px-[5%] z-50 flex justify-center items-center ">
        <div className="bg-[#0a1736] z-50 border border-[#7FD6FF]/20 rounded-xl shadow-[0_0_32px_0_rgba(0,123,255,0.15)] flex justify-center items-center w-full max-w-5xl transition-all duration-300">
          <iframe
            className="block z-50 rounded-lg shadow-lg w-full aspect-video border border-[#7FD6FF]/30 shadow-xl  bg-[#0a1736]"
            src="https://www.youtube.com/embed/Nno5URDTGsI?si=7_VxICr5bVr4I_vK&autoplay=1&mute=1&loop=1&playlist=Nno5URDTGsI&showinfo=0&rel=0&modestbranding=1"
            title="Exosphere Demo Video"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowFullScreen
          />
        </div>
      </div>
    

      {/* Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-[#031035] to-transparent" />
 
      {/* Bento Section with Exosphere-style padding and centering */}
      <motion.div 
        ref={featuresRef}
        initial={{ opacity: 0, y: 50 }}
        animate={featuresInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 50 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="relative flex flex-col items-center justify-center px-4 py-16 max-w-6xl mx-auto w-full z-10"
      >
        <Features />
      </motion.div>

      

      {/* Code Comparison Section */}
      {/* <motion.div 
        ref={codeRef}
        initial={{ opacity: 0, y: 50 }}
        animate={codeInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 50 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="relative w-full flex flex-col items-center justify-center py-16 gap-2"
      >
        <h3 className={`${pattanakarn.className} text-center text-2xl text-white mb-2`}>get running within two lines of code</h3>
        <p className={`${darkerGrotesque.className} text-center text-xl text-blue-200 mb-6 max-w-2xl`}>Say goodbye to managing your own code to orchestrate ai workflows.</p>
        <div className="w-full flex justify-center items-center pb-10">
          <CodeComparisonDemo/>
        </div>
      </motion.div> */}

       {/* Benchmarking Section */}
       {/* <motion.div 
        ref={benchmarkRef}
        initial={{ opacity: 0, y: 50 }}
        animate={benchmarkInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 50 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="relative py-16 px-4 max-w-6xl mx-auto"
      >
        <BenchmarkingSection />
      </motion.div> */}

      {/* Blog Section */}
      <motion.div 
        ref={blogRef}
        initial={{ opacity: 0, y: 50 }}
        animate={blogInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 50 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      >
        <BlogSection />    
      </motion.div>
      

      {/* Book a Call CTA and Footer */}
      <motion.div 
        ref={ctaRef}
        initial={{ opacity: 0, y: 50 }}
        animate={ctaInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 50 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="relative"
      >
        <PulsatingGradient />
        <BookCallCTA />
        <Footer />
      </motion.div>

      {/* Floating Social Bar */}
      <FloatingBar />
    </div>
  )
}
