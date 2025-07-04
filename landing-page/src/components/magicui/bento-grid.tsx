import { ComponentPropsWithoutRef, ReactNode } from "react";

import { cn } from "@/lib/utils";
import { pattanakarn, darkerGrotesque } from "@/lib/fonts";


interface BentoGridProps extends ComponentPropsWithoutRef<"div"> {
  children: ReactNode;
  className?: string;
}

interface BentoCardProps extends ComponentPropsWithoutRef<"div"> {
  name: string;
  className: string;
  background: ReactNode;
  Icon: React.ElementType;
  description: string;
  href: string;
  cta: string;
  hoverBorderColor?: string;
}

const BentoGrid = ({ children, className, ...props }: BentoGridProps) => {
  return (
    <div
      className={cn(
        "grid w-full auto-rows-[22rem] grid-cols-3 gap-4 relative",
        "before:absolute before:inset-0 before:bg-gradient-to-r before:from-[#7FD6FF]/10 before:to-[#66d1b5]/10 before:blur-3xl before:-z-10",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
};

const BentoCard = ({
  name,
  className,
  background,
  Icon,
  description,
  href,
  cta,
  hoverBorderColor = "#66d1b5",
  ...props
}: BentoCardProps) => (
  <div
    key={name}
    className={cn(
      "group relative col-span-3 flex flex-col justify-between overflow-hidden rounded-xl border border-[#7FD6FF] transition-colors duration-300",
      "transform-gpu  [border:1px_solid_rgba(218,245,255,.3)]",
      className,
    )}
    style={{
      '--hover-border-color': hoverBorderColor,
    } as any}
    {...props}
  >
    <div>{background}</div>
    <div className="pointer-events-none z-10 flex transform-gpu flex-col gap-1 p-6 transition-all duration-300">
      <Icon className="h-12 w-12 origin-left transform-gpu text-white transition-all duration-300 ease-in-out group-hover:scale-75" />
      <h3 className={`${pattanakarn.className} text-xl text-white lowercase`}>
        {name}
      </h3>
      <p className={`${darkerGrotesque.className} max-w-lg text-[#8bdfff]`}>{description}</p>
    </div>

    
    <div className="pointer-events-none absolute inset-0 transform-gpu transition-all duration-300 group-hover:bg-black/[.03] group-hover:dark:bg-neutral-800/10" />
    <style jsx>{`
      .group:hover {
        border-color: var(--hover-border-color) !important;
      }
    `}</style>
  </div>
);

export { BentoCard, BentoGrid };
