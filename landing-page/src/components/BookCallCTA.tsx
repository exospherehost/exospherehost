import { pattanakarn, darkerGrotesque } from "@/lib/fonts"


export default function BookCallCTA() {
  return (
    <div className="relative w-full py-30 px-4 bg-gradient-to-b from-[#031035] to-transparent">
     
      <div className="max-w-4xl mx-auto text-center">
        <h2 className={`text-4xl md:text-5xl text-white mb-6 ${pattanakarn.className}`}>
          plug into exosphere
        </h2>
        <p className={`text-xl text-[#B3D6FF] mb-8 max-w-2xl mx-auto ${darkerGrotesque.className}`}>
        Offload autoscaling, branching logic, and state storage. Exosphere keeps every agent running reliably from your first prototype to millions of tasks.

        </p>
        <button className="relative inline-flex  h-14 overflow-hidden rounded-xl p-[1px] focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 focus:ring-offset-slate-50 pointer-events-auto"
              onClick={() => {
                window.open('https://calendly.com/nikita-exosphere/exosphere-intro', '_blank');
              }}
            >
              <span className="absolute  Z-200 inset-[-1000%] animate-[spin_2s_linear_infinite] bg-[conic-gradient(from_90deg_at_50%_50%,#8bdfff_0%,#e4587d_50%,#66d1b5_100%)]" />
              <span className="inline-flex h-full w-full p-2 cursor-pointer items-center justify-center rounded-xl bg-slate-950 px-6 py-2 text-base font-medium text-white backdrop-blur-3xl">
                Book a call
              </span>
            </button>
      </div>
    </div>
  )
} 