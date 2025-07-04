"use client"

import { useEffect, useRef, useState } from "react"
import OrbitBackground from "@/components/OrbitBackground"
import { pattanakarn, darkerGrotesque } from "@/lib/fonts"

export default function OrbitalSystem() {
  const [windowDimensions, setWindowDimensions] = useState({ width: 800, height: 600 })

  // Color palette from the provided image
  const colors = {
    darkBlue1: "#001440",
    lightBlue: "#7FD6FF",
    darkBlue2: "#002875",
    purple: "#2A1A3A",
    coral: "#FF5D73",
    peach: "#FFBFB3",
  }

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
      <div className="relative z-10 grid grid-cols-1 md:grid-cols-2 min-h-screen">
          <div className="flex flex-col justify-start items-center md:items-start px-4 md:pl-20  pb-8 md:py-0 max-w-xl mx-auto mt-[20vh]">
            <h1 className={`${pattanakarn.className} text-white text-3xl sm:text-3xl md:text-5xl lg:text-6xl leading-tight mb-4 drop-shadow-lg text-center md:text-left`}>
              the platform for async ai workflows
            </h1>
            <p className={`${darkerGrotesque.className} text-[#B3D6FF] text-sm sm:text-base md:text-lg lg:text-xl mb-6 md:mb-8 drop-shadow-md neon-text text-center md:text-left`}>
              Describe your workflows once, then let Exosphere run them in the background with up to 75 % lower cost—built for jobs that must run reliably at scale. 
            </p>
            <button className="relative inline-flex z-200 h-10 overflow-hidden rounded-full p-[1px] focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 focus:ring-offset-slate-50 pointer-events-auto mt-2"
              onClick={() => {
                window.open('https://forms.gle/YqnXvpzq43fWDoAk8', '_blank');
              }}
            >
              <span className="absolute Z-200 inset-[-1000%] animate-[spin_2s_linear_infinite] bg-[conic-gradient(from_90deg_at_50%_50%,#8bdfff_0%,#e4587d_50%,#66d1b5_100%)]" />
              <span className="inline-flex h-full w-full cursor-pointer items-center justify-center rounded-full bg-slate-950 px-5 py-4 text-sm font-medium text-white backdrop-blur-3xl">
                Book a Call
              </span>
            </button>
          </div>
          <div className="flex items-center justify-center relative h-64 md:h-auto">
            <OrbitBackground />
          </div>
      </div>

  )
}
