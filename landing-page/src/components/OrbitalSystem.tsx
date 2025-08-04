"use client"

import { useEffect, useState } from "react"
import OrbitBackground from "@/components/OrbitBackground"
import { pattanakarn, darkerGrotesque } from "@/lib/fonts"

export default function OrbitalSystem() {
  const [windowDimensions, setWindowDimensions] = useState({ width: 800, height: 600 })

  useEffect(() => {
    const handleResize = () => {
      setWindowDimensions({
        width: window.innerWidth,
        height: window.innerHeight
      })
    }

    handleResize()
    window.addEventListener("resize", handleResize)
    return () => window.removeEventListener("resize", handleResize)
  }, [])

  return (  
      <div className="relative z-10 grid grid-cols-1 md:grid-cols-2 min-h-[80vh]">
          <div className="flex flex-col justify-start items-center md:items-start px-4 md:pl-20  pb-2 md:py-0 max-w-xl mx-auto mt-[10vh]">
                 
            <h1 className={`${pattanakarn.className} text-white text-3xl sm:text-3xl md:text-5xl lg:text-6xl leading-tight mb-4 drop-shadow-lg text-center md:text-left`}>
              batch ai agents for any scale
            </h1>
            <p className={`${darkerGrotesque.className} text-[#B3D6FF] text-sm sm:text-base md:text-lg lg:text-xl mb-6 md:mb-8 drop-shadow-md text-center md:text-left`}>
            Truly dynamic, built for agents at scale. Branching agent flows, autoscaling compute, and state persistence for your AI agents.
            </p>
            <div className="flex flex-col md:flex-row items-center gap-3 mb-4 w-full md:justify-start justify-center">
            <button className="relative inline-flex z-200 h-10 overflow-hidden rounded-xl p-[1px] focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 focus:ring-offset-slate-50 pointer-events-auto mt-2 group"
              onClick={() => {
                window.open('https://calendly.com/nikita-exosphere/exosphere-intro', '_blank');
              }}
            >
              <span className="absolute Z-200 inset-[-1000%] animate-[spin_2s_linear_infinite] bg-[conic-gradient(from_90deg_at_50%_50%,#8bdfff_0%,#e4587d_50%,#66d1b5_100%)] group-hover:animate-none" />
              <span className={`${darkerGrotesque.className} inline-flex h-full w-full cursor-pointer items-center justify-center rounded-xl bg-slate-950 px-5 py-4 text-md font-medium text-white backdrop-blur-3xl`}>
              Start batching
              </span>
            </button>
            <button className="relative inline-flex z-200 h-10 overflow-hidden rounded-xl p-[1px] f pointer-events-auto mt-2 transition-all duration-300 hover:shadow-lg"
              onClick={() => {
                window.open('https://github.com/exospherehost/exospherehost', '_blank');
              }}
            >
              <span className="absolute Z-200 inset-[-1000%] border border-[#ffffff]/20 transition-all duration-300 hover:border-[#8bdfff]/40" />
              <span className={`${darkerGrotesque.className} inline-flex h-full w-full cursor-pointer items-center justify-center rounded-xl bg-slate-950/30 px-5 py-4 text-md font-medium text-white backdrop-blur-3xl transition-all duration-300 hover:bg-slate-950/50 hover:text-[#8bdfff]`}>
              <svg className="w-4 h-4 mr-1.5 transition-transform duration-300 hover:rotate-12" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
              </svg>
              Star us on GitHub
              </span>
            </button>        
           
          </div>  
          </div>
          <div className="flex items-center justify-center relative h-64 md:h-auto">
            <OrbitBackground />
          </div>
      </div>

  )
}
