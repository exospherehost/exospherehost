import React, { useRef, useEffect, useState } from "react"

// Color palette from the attached image
const palette = {
  darkBlue: "#031035",
  skyBlue: "#8ee3ff",
  navy: "#0b2260",
  paleBlue: "#e0f7ff",
  deepPurple: "#2a223d",
  teal: "#5ed6c2",
  pink: "#e4587d",
  yellow: "#ffed9e",
}

// Orbits and satellites will be defined as ratios relative to canvas size
const orbits = [
  { major: 0.6, minor: 0.18, color: palette.teal, rotation: -Math.PI / 12 },
  { major: 0.75, minor: 0.28, color: palette.pink, rotation: -Math.PI / 35 },
  { major: 0.8, minor: 0.2, color: palette.paleBlue, rotation: -Math.PI / 15},
]

const satellitesConfig = [
  [
    { size: 0.018, speed: 0.3, offset: 0 },
    { size: 0.01, speed: 0.5, offset: Math.PI / 2 },
  ],
  [
    { size: 0.016, speed: 0.375, offset: 0 },
    { size: 0.01, speed: 0.325, offset: Math.PI },
  ],
  [
    { size: 0.02, speed: 0.175, offset: 0 },
    { size: 0.014, speed: 0.275, offset: Math.PI / 4 },
    { size: 0.01, speed: 0.35, offset: Math.PI / 2 },
    { size: 0.016, speed: 0.3, offset: Math.PI },
  ],
]

const OrbitBackground: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [dimensions, setDimensions] = useState({ width: 100, height: 100 })
  const [time, setTime] = useState(0)
  const animationFrameRef = useRef<number | undefined>(undefined)

  // ResizeObserver to track container size
  useEffect(() => {
    const updateSize = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect()
        setDimensions({ width: rect.width, height: rect.height })
      }
    }
    updateSize()
    const observer = new (window as any).ResizeObserver(updateSize)
    if (containerRef.current) observer.observe(containerRef.current)
    window.addEventListener('resize', updateSize)
    return () => {
      observer.disconnect()
      window.removeEventListener('resize', updateSize)
    }
  }, [])

  useEffect(() => {
    const animate = () => {
      setTime(prev => (prev + 0.01) % (Math.PI * 2))
      animationFrameRef.current = requestAnimationFrame(animate)
    }
    animationFrameRef.current = requestAnimationFrame(animate)
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    // Handle high-DPI screens
    const dpr = window.devicePixelRatio || 1
    const width = dimensions.width
    const height = dimensions.height
    canvas.width = width * dpr
    canvas.height = height * dpr
    canvas.style.width = `${width}px`
    canvas.style.height = `${height}px`
    ctx.setTransform(1, 0, 0, 1, 0, 0)
    ctx.scale(dpr, dpr)

    // Clear
    ctx.clearRect(0, 0, width, height)

    // Glowing light source (radial gradient)
    const glowX = width * 1
    const glowY = height * 0.4
    const glowRadius = Math.min(width, height) * 0.35
    const gradient = ctx.createRadialGradient(glowX, glowY, 10, glowX, glowY, glowRadius)
    gradient.addColorStop(0, palette.paleBlue + "CC")
    gradient.addColorStop(0.3, palette.skyBlue + "88")
    gradient.addColorStop(0.7, palette.skyBlue + "22")
    gradient.addColorStop(1, "transparent")
    ctx.beginPath()
    ctx.arc(glowX, glowY, glowRadius, 0, Math.PI * 2)
    ctx.fillStyle = gradient
    ctx.fill()

    // Draw orbits and satellites
    orbits.forEach((orbit, orbitIndex) => {
      ctx.save()
      ctx.translate(glowX, glowY)
      ctx.rotate(orbit.rotation)
      const major = orbit.major * width
      const minor = orbit.minor * height
      // Draw orbit
      ctx.beginPath()
      ctx.ellipse(0, 0, major, minor, 0, 0, Math.PI * 2)
      ctx.strokeStyle = orbit.color + "B0"
      ctx.lineWidth = 1
      ctx.shadowColor = orbit.color
      ctx.shadowBlur = 4
      ctx.stroke()
      // Draw satellites for this orbit
      satellitesConfig[orbitIndex].forEach(satellite => {
        const satelliteTime = time * satellite.speed + satellite.offset
        const x = major * Math.cos(satelliteTime)
        const y = minor * Math.sin(satelliteTime)
        ctx.beginPath()
        ctx.arc(x, y, satellite.size * Math.max(width, height), 0, Math.PI * 2)
        ctx.fillStyle = orbit.color
        ctx.shadowColor = orbit.color
        ctx.shadowBlur = 8
        ctx.fill()
      })
      ctx.restore()
    })
  }, [dimensions, time])

  return (
    <div ref={containerRef} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", zIndex: 0, overflow: "hidden" }}>
      <canvas ref={canvasRef} style={{ display: "block", width: "100%", height: "100%" }} />
    </div>
  )
}

export default OrbitBackground 