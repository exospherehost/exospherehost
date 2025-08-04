import { Waypoints, FileStack, CloudCog, SquareCode, CircleDollarSign   } from "lucide-react";
import Image from "next/image";

import { cn } from "@/lib/utils";
import { Workflow } from "@/components/Workflow";
import { Jobs } from "@/components/Jobs";
import { BentoCard, BentoGrid } from "@/components/magicui/bento-grid";
import { Marquee } from "@/components/magicui/marquee";
import { Ripple } from "./magicui/ripple";
import { pattanakarn } from "@/lib/fonts";

const files = [
  {
    name: "model_weights.pt",
    body: "PyTorch model weights containing the trained parameters of a deep learning model for natural language processing.",
  },
  {
    name: "training_data.csv",
    body: "Dataset containing labeled examples used for training machine learning models, including features and target variables.",
  },
  {
    name: "config.yaml",
    body: "Configuration file defining hyperparameters, model architecture, and training settings for AI model deployment.",
  },
  {
    name: "api_docs.md",
    body: "Documentation for the API endpoints and their usage, including request parameters, response formats, and examples.",
  },
  {
    name: "model_metrics.json",
    body: "Performance metrics and evaluation results of AI models, including accuracy, precision, recall, and F1 scores.",
  },
];

const features = [
  {
    Icon: Waypoints,
    name: "Create Multi Step AI Workflows",
    description: "Chain tools, models, and APIs into a single DAG. Exosphere automatically batches and streams inputs to every step so GPUs stay saturated.",
    href: "#",
    cta: "Learn more",
    className: "col-span-3 lg:col-span-3",
    background: (
      <Workflow className="absolute right-2 top-4 h-[300px] border-none transition-all duration-300 ease-out [mask-image:linear-gradient(to_top,transparent_10%,#000_60%)] group-hover:scale-105" />
    ),
  },
  {
    Icon: FileStack,
    name: "Plug in your data store and get started",
    description: "Drag-and-drop 10 K PDFs, 200 M-row CSVs, or entire S3 buckets. Exosphere chunks and feeds them to your agents without memory bottlenecks.",
    href: "#",
    cta: "Learn more",
    className: "col-span-3 lg:col-span-1",
    background: (
      <Marquee
        pauseOnHover
        className="absolute top-10 [--duration:20s] [mask-image:linear-gradient(to_top,transparent_40%,#000_100%)] "
      >
        {files.map((f, idx) => (
          <figure
            key={idx}
            className={cn(
              "relative w-32 cursor-pointer overflow-hidden rounded-xl border p-4",
              "border-gray-950/[.1] bg-gray-950/[.01] hover:bg-gray-950/[.05]",
              "dark:border-gray-50/[.1] dark:bg-gray-50/[.10] dark:hover:bg-gray-50/[.15]",
              "transform-gpu blur-[1px] transition-all duration-300 ease-out hover:blur-none",
            )}
          >
            <div className="flex flex-row items-center gap-2">
              <div className="flex flex-col">
                <figcaption className="text-sm font-medium dark:text-white ">
                  {f.name}
                </figcaption>
              </div>
            </div>
            <blockquote className="mt-2 text-xs">{f.body}</blockquote>
          </figure>
        ))}
      </Marquee>
    ),
  },
  {
    Icon: CloudCog,
    name: "Set Deadlines, We Schedule",
    description: "Pick a deadline. Our scheduler will batch and schedule your jobs to hit it.",
    href: "#",
    cta: "Learn more",
    className: "col-span-3 lg:col-span-2",
    background: (
      <Jobs className="absolute right-2 top-4 h-[300px] w-full scale-75 border-none transition-all duration-300 ease-out [mask-image:linear-gradient(to_top,transparent_10%,#000_100%)] group-hover:scale-90" />
    ),
  }, 
  {
    Icon: SquareCode,
    name: "open-source sdk for async ai jobs",
    description: "Define Python functions. Orbit handles retries, scaling, and orchestration.",
    href: "#",
    cta: "Learn more",
    className: "col-span-3 lg:col-span-2",
    background: (
      <div className="absolute right-2 top-4 h-[300px] w-full flex items-center justify-center overflow-hidden transition-all duration-300 ease-out [mask-image:linear-gradient(to_top,transparent_10%,#000_50%)] group-hover:scale-105">
        <p className={`${pattanakarn.className} whitespace-pre-wrap text-center text-5xl font-medium tracking-tighter text-white`}>
          orbit sdk
        </p>
        <Ripple />
      </div>
    ),
  },
  {
    Icon: CircleDollarSign,
    name: "Higher SLAs = Lower Costs",
    description: "Trade off latency for price. Define SLAs and let Exosphere optimize cost.",
    href: "#",
    cta: "Learn more",
    className: "col-span-3 lg:col-span-1",
    background: (
      <div className="absolute right-2 top-4 h-[300px] w-full flex items-center justify-center overflow-hidden transition-all duration-300 ease-out [mask-image:linear-gradient(to_top,transparent_10%,#000_50%)] group-hover:scale-105">
        <Image
          src="/dollar.gif"
          alt="Dollar sign animation"
          width={700}
          height={700}
          className="transform-gpu transition-all duration-300 ease-out group-hover:blur-none group-hover:scale-110"
        />
      </div>
    ),
  },
];

export function Features() {
  return (
    <BentoGrid className="gap-8">
      {features.map((feature, idx) => (
        <BentoCard
          key={idx}
          {...feature}
          className={
            `${feature.className} bg-[#031035]/80 border-[#7FD6FF]/30 shadow-xl backdrop-blur-lg transition-all duration-300 group-hover:scale-[1.03] group-hover:shadow-2xl` // Exosphere card style
          }
          hoverBorderColor="#7FD6FF"
        >
          <div className="absolute inset-0 z-0 bg-gradient-to-br from-[#031035]/80 via-[#2A1A3A]/60 to-[#7FD6FF]/10 pointer-events-none" />
        </BentoCard>
      ))}
    </BentoGrid>
  );
}
