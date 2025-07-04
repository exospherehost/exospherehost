"use client"

import Navbar from "@/components/Navbar"
import Stars from "@/components/Stars"
import PulsatingGradient from "@/components/PulsatingGradient"
import { darkerGrotesque, pattanakarn } from "@/lib/fonts"
import OrbitalSystem from "@/components/OrbitalSystem"
import BookCallCTA from "@/components/BookCallCTA"
import dynamic from 'next/dynamic'

const Features = dynamic(() => import("@/components/Features").then(mod => mod.Features))
const BenchmarkingSection = dynamic(() => import("@/components/BenchmarkingSection"))
const Footer = dynamic(() => import("@/components/Footer"))
const FloatingBar = dynamic(() => import("@/components/FloatingBar"))
const CodeComparisonDemo = dynamic(() => import("@/components/code").then(mod => mod.CodeComparisonDemo))
const BlogSection = dynamic(() => import("@/components/BlogSection"))

export default function Exosphere() {
  return (
    <div className="w-full h-screen relative bg-[#031035]">
      <PulsatingGradient />
      {/* Twinkling Stars */}
      <Stars />

      <div className="relative z-100">
        <Navbar />       
      </div>

      <OrbitalSystem />

      {/* Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-[#031035] to-transparent " />    


      {/* Bento Section with Exosphere-style padding and centering */}
      <div className="relative flex flex-col items-center justify-center px-4 py-16 max-w-6xl mx-auto w-full z-10">
        <Features />
      </div>

      {/* Code Comparison Section */}
      <div className="relative w-full flex flex-col items-center justify-center py-16 gap-2">
        <h3 className={`${pattanakarn.className} text-center text-2xl text-white mb-2`}>get running within two lines of code</h3>
        <p className={`${darkerGrotesque.className} text-center text-xl text-blue-200 mb-6 max-w-2xl`}>Say goodbye to managing your own code to orchestrate ai workflows.</p>
        <div className="w-full flex justify-center items-center pb-10">
          <CodeComparisonDemo/>
        </div>
      </div>

       {/* Benchmarking Section */}
       <div className="relative py-16 px-4 max-w-6xl mx-auto">
        <BenchmarkingSection />
      </div>

      {/* Blog Section */}
      <BlogSection />    
      

      {/* Book a Call CTA and Footer */}
      <div className="relative">
        <PulsatingGradient />
        <BookCallCTA />
        <Footer />
      </div>

      {/* Floating Social Bar */}
      <FloatingBar />
    </div>
  )
}
