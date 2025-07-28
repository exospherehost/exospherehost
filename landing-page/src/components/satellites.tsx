"use client"

import type { ReactNode } from "react"
import { useEffect, useRef, useState } from "react"

interface AnimatedExosphereBackgroundProps {
  children?: ReactNode
  height?: string
}

interface Particle {
  x: number
  y: number
  size: number
  speed: number
  color: string
  alpha: number
}

interface Satellite {
  x: number
  y: number
  rotation: number
  orbitRadius: number
  orbitSpeed: number
  pulseSize: number
  pulseMax: number
  pulseSpeed: number
}

interface Colors {
  background: string
  lightBlue: string
  coral: string
  teal: string
  darkBlue: string
  purple: string
}

export default function AnimatedExosphereBackground({
  children,
  height = "100vh",
}: AnimatedExosphereBackgroundProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [dimensions, setDimensions] = useState({ width: 1200, height: 800 })

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    // Set canvas dimensions
    const resizeCanvas = () => {
      const parent = canvas.parentElement
      if (!parent) return

      const { width, height } = parent.getBoundingClientRect()
      canvas.width = width
      canvas.height = height
      setDimensions({ width, height })
    }

    // Initial resize
    resizeCanvas()

    // Listen for window resize
    window.addEventListener("resize", resizeCanvas)

    return () => {
      window.removeEventListener("resize", resizeCanvas)
    }
  }, [])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    // Load satellite image
    const satelliteImg = new window.Image()
    satelliteImg.src = "/satellite.png"

    // Colors
    const colors: Colors = {
      background: "#001440",
      lightBlue: "#7FD6FF",
      coral: "#FF5D73",
      teal: "#00B8A9",
      darkBlue: "#002875",
      purple: "#2A1A3A",
    }

    // Particles
    const particles: Particle[] = []

    for (let i = 0; i < 50; i++) {
      particles.push({
        x: Math.random() * dimensions.width,
        y: Math.random() * dimensions.height,
        size: Math.random() * 2 + 0.5,
        speed: Math.random() * 0.5 + 0.1,
        color: [colors.lightBlue, colors.coral, colors.teal][Math.floor(Math.random() * 3)],
        alpha: Math.random() * 0.5 + 0.1,
      })
    }

    // Satellites
    const satellites: Satellite[] = [
      { x: 0, y: 0, rotation: 0, orbitRadius: 0, orbitSpeed: 0, pulseSize: 0, pulseMax: 30, pulseSpeed: 0.3 },
      {
        x: -70,
        y: -50,
        rotation: 45,
        orbitRadius: 85.6,
        orbitSpeed: 0.0002,
        pulseSize: 0,
        pulseMax: 30,
        pulseSpeed: 0.2,
      },
      {
        x: 60,
        y: -40,
        rotation: -30,
        orbitRadius: 72.1,
        orbitSpeed: -0.0003,
        pulseSize: 0,
        pulseMax: 30,
        pulseSpeed: 0.25,
      },
    ]

    // Orbit rotation
    let orbit1Rotation = 0
    let orbit2Rotation = Math.PI / 4

    let animationFrameId: number
    let lastTimestamp = 0

    const animate = (timestamp: number) => {
      if (!lastTimestamp) lastTimestamp = timestamp
      const deltaTime = timestamp - lastTimestamp
      lastTimestamp = timestamp

      // Clear canvas
      ctx.clearRect(0, 0, dimensions.width, dimensions.height)

      // Fill background with gradient
      const gradient = ctx.createLinearGradient(0, 0, 0, dimensions.height)
      gradient.addColorStop(0, colors.background)
      gradient.addColorStop(1, "#000c28")
      ctx.fillStyle = gradient
      ctx.fillRect(0, 0, dimensions.width, dimensions.height)

      // Update center position based on canvas size
      const centerX = dimensions.width * 0.5
      const centerY = dimensions.height * 0.5

      // Draw particles
      particles.forEach((particle) => {
        ctx.beginPath()
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
        ctx.fillStyle =
          particle.color +
          Math.floor(particle.alpha * 255)
            .toString(16)
            .padStart(2, "0")
        ctx.fill()

        // Move particles
        particle.y += particle.speed
        if (particle.y > dimensions.height) {
          particle.y = 0
          particle.x = Math.random() * dimensions.width
        }
      })

      // Update orbit rotations
      orbit1Rotation += 0.0001 * deltaTime
      orbit2Rotation -= 0.00015 * deltaTime

      // Draw orbits
      // Cluster circle (REMOVE THIS)
      // ctx.beginPath()
      // ctx.arc(centerX, centerY, 150, 0, Math.PI * 2)
      // ctx.strokeStyle = colors.lightBlue + "40" // More transparent
      // ctx.setLineDash([5, 5])
      // ctx.lineWidth = 2
      // ctx.stroke()
      // ctx.setLineDash([])

      // Outer orbits
      // Orbit 1 - Coral
      ctx.beginPath()
      ctx.ellipse(centerX, centerY, dimensions.width * 0.4, dimensions.height * 0.3, orbit1Rotation, 0, Math.PI * 2)
      ctx.strokeStyle = colors.coral + "B0" // Slightly more transparent for sky-like effect
      ctx.setLineDash([])
      ctx.lineWidth = 1 // Thin line
      ctx.stroke()

      // Orbit 2 - Teal
      ctx.beginPath()
      ctx.ellipse(centerX, centerY, dimensions.width * 0.3, dimensions.height * 0.25, orbit2Rotation, 0, Math.PI * 2)
      ctx.strokeStyle = colors.teal + "B0"
      ctx.setLineDash([])
      ctx.lineWidth = 1 // Thin line
      ctx.stroke()

      // Update and draw satellites
      satellites.forEach((satellite, idx) => {
        // Update satellite position if it's orbiting
        if (idx === 1) { // First orbiting satellite
          // Orbit 1
          const angle = timestamp * satellite.orbitSpeed
          satellite.x = Math.cos(angle + orbit1Rotation) * (dimensions.width * 0.4)
          satellite.y = Math.sin(angle + orbit1Rotation) * (dimensions.height * 0.3)
          satellite.rotation += 0.02 * deltaTime
        } else if (idx === 2) { // Second orbiting satellite
          // Orbit 2
          const angle = timestamp * satellite.orbitSpeed
          satellite.x = Math.cos(angle + orbit2Rotation) * (dimensions.width * 0.3)
          satellite.y = Math.sin(angle + orbit2Rotation) * (dimensions.height * 0.25)
          satellite.rotation += 0.02 * deltaTime
        }
        // Update pulse size
        satellite.pulseSize += satellite.pulseSpeed * (deltaTime / 16)
        if (satellite.pulseSize > satellite.pulseMax) {
          satellite.pulseSize = 0
        }
        // Draw satellite image instead of drawing with canvas
        ctx.save()
        ctx.translate(centerX + satellite.x, centerY + satellite.y)
        ctx.rotate((satellite.rotation * Math.PI) / 180)
        // Draw the image centered, scale to 60x60 (adjust as needed)
        ctx.drawImage(satelliteImg, -30, -30, 60, 60)
        ctx.restore()
      })

    //   // Draw info boxes
    //   drawInfoBox(
    //     ctx,
    //     centerX - 150,
    //     centerY + 180,
    //     300,
    //     100,
    //     colors.darkBlue,
    //     colors.lightBlue,
    //     "Satellite:",
    //     "Atomic unit of exosphere",
    //     "Singular function/task",
    //   )

    //   drawInfoBox(
    //     ctx,
    //     dimensions.width * 0.75,
    //     centerY - 150,
    //     300,
    //     100,
    //     colors.darkBlue,
    //     colors.lightBlue,
    //     "Cluster:",
    //     "End to End workflow",
    //     "SLA defined on a cluster",
    //   )

    //   drawInfoBox(
    //     ctx,
    //     dimensions.width * 0.75,
    //     centerY + 100,
    //     300,
    //     100,
    //     colors.darkBlue,
    //     colors.lightBlue,
    //     "Orbit:",
    //     "Open Source backbone of",
    //     "exosphere to launch satellites",
    //   )

      animationFrameId = requestAnimationFrame(animate)
    }

    animationFrameId = requestAnimationFrame(animate)

    return () => {
      cancelAnimationFrame(animationFrameId)
    }
  }, [dimensions])

  const drawInfoBox = (
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    width: number,
    height: number,
    bgColor: string,
    textColor: string,
    title: string,
    line1: string,
    line2: string,
  ) => {
    // Box
    ctx.fillStyle = bgColor + "80" // Semi-transparent
    ctx.beginPath()
    ctx.roundRect(x, y, width, height, 15)
    ctx.fill()

    // Text
    ctx.fillStyle = textColor
    ctx.font = "bold 24px Arial"
    ctx.textAlign = "center"
    ctx.fillText(title, x + width / 2, y + 30)

    ctx.font = "20px Arial"
    ctx.fillText(line1, x + width / 2, y + 60)
    ctx.fillText(line2, x + width / 2, y + 90)
  }

  return (
    <div className="relative w-full" style={{ height }}>
      <canvas ref={canvasRef} className="absolute top-0 left-0 w-full h-full" />
      <div className="relative z-10 w-full h-full">{children}</div>
    </div>
  )
} 