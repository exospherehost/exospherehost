"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import PulsatingGradient from "@/components/PulsatingGradient";
import Stars from "@/components/Stars";
import { ArrowLeft } from "lucide-react";
import { darkerGrotesque, pattanakarn } from "@/lib/fonts";
import Navbar from "@/components/Navbar";
export default function NotFound() {
  return (
    <div className="relative min-h-screen flex flex-col items-center overflow-hidden bg-black text-white p-4">
      {/* Background elements */}
      <div className="absolute inset-0 z-0">
        <Stars />
      </div>
      <div className="absolute inset-0 z-0 opacity-50">
        <PulsatingGradient />
      </div>

      <div className="relative z-100">
        <Navbar />
      </div>
      
      {/* Content */}
      <div className="z-10 text-center justify-center pt-20 max-w-3xl mx-auto">
        <h1 className={`text-9xl font-bold text-transparent bg-clip-text bg-gradient-to-br from-[#66d1b5] via-[#8bdfff] to-[#e4587d] mb-4 ${darkerGrotesque.className}`}>
          404
        </h1>
        <h2 className={`text-4xl font-bold mb-6 ${pattanakarn.className}`}>page not found</h2>
        <p className={`text-xl text-gray-400 mb-8 ${darkerGrotesque.className}`}>
          The page you're looking for doesn't exist or has been moved to another location.
        </p>
        <Link href="/">
          <Button 
            className={`${darkerGrotesque.className} inline-flex h-14 items-center justify-center rounded-full bg-slate-950 px-6 py-2 text-base font-medium text-white backdrop-blur-3xl border border-transparent hover:border-blue-600/30 transition-colors`}
          >
            <ArrowLeft size={18} />
            Back to Home
          </Button>
        </Link>
      </div>
    </div>
  );
} 