"use client";

import React, { forwardRef, useRef } from "react";

import { cn } from "@/lib/utils";
import { AnimatedBeam } from "@/components/magicui/animated-beam";

const Circle = forwardRef<
  HTMLDivElement,
  { className?: string; children?: React.ReactNode }
>(({ className, children }, ref) => {
  return (
    <div
      ref={ref}
      className={cn(
        "z-10 flex size-12 items-center justify-center rounded-full border-1 border-[#daf5ff] bg-[#031035] backdrop-blur-2xl p-3 shadow-[0_0_20px_-12px_rgba(0,0,0,0.8)]",
        className,
      )}
    >
      {children}
    </div>
  );
});

Circle.displayName = "Circle";

export function Workflow({
  className,
}: {
  className?: string;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const div1Ref = useRef<HTMLDivElement>(null);
  const div2Ref = useRef<HTMLDivElement>(null);
  const div3Ref = useRef<HTMLDivElement>(null);
  const div4Ref = useRef<HTMLDivElement>(null);
  const div5Ref = useRef<HTMLDivElement>(null);
  const div6Ref = useRef<HTMLDivElement>(null);
  const div7Ref = useRef<HTMLDivElement>(null);
  const div8Ref = useRef<HTMLDivElement>(null);
  const div9Ref = useRef<HTMLDivElement>(null);
  const div10Ref = useRef<HTMLDivElement>(null);

  return (
    <div
      className={cn(
        "relative flex h-[500px] w-full items-center justify-center overflow-hidden p-10",
        className,
      )}
      ref={containerRef}
    >
      <div className="flex size-full max-w-5xl flex-row items-stretch justify-between gap-10">
        {/* Input Sources */}
        <div className="flex flex-col justify-center gap-2">
          <Circle ref={div1Ref}>
            <Icons.sheets />
          </Circle>
          <Circle ref={div2Ref}>
            <Icons.s3 />
          </Circle>
          <Circle ref={div3Ref}>
            <Icons.sqs />
          </Circle>
          <Circle ref={div4Ref}>
            <Icons.drive />
          </Circle>
          <Circle ref={div5Ref}>
            <Icons.mongodb />
          </Circle>
        </div>

        {/* Initial Processing Step */}
        <div className="flex flex-col justify-center">
          <Circle ref={div6Ref} className="size-16 shadow-[0_0_30px_0_rgba(218,245,255,0.3)]">
            <Icons.exosphere />
          </Circle>
        </div>

        {/* Parallel Processing Steps */}
        <div className="flex flex-col justify-center gap-8">
          <Circle ref={div8Ref} className="size-16">
            <Icons.llama />
          </Circle>
          <Circle ref={div10Ref} className="size-16">
            <Icons.deepseek />
          </Circle>
        </div>

        {/* Final Output */}
        <div className="flex flex-col justify-center">
          <Circle ref={div9Ref}>
            <Icons.user />
          </Circle>
        </div>
      </div>

      {/* Input to Processing Connections */}
      <AnimatedBeam
        containerRef={containerRef}
        fromRef={div1Ref}
        toRef={div6Ref}
      />
      <AnimatedBeam
        containerRef={containerRef}
        fromRef={div2Ref}
        toRef={div6Ref}
      />
      <AnimatedBeam
        containerRef={containerRef}
        fromRef={div3Ref}
        toRef={div6Ref}
      />
      <AnimatedBeam
        containerRef={containerRef}
        fromRef={div4Ref}
        toRef={div6Ref}
      />
      <AnimatedBeam
        containerRef={containerRef}
        fromRef={div5Ref}
        toRef={div6Ref}
      />

      {/* Processing to Parallel Steps Connections */}
      <AnimatedBeam
        containerRef={containerRef}
        fromRef={div6Ref}
        toRef={div8Ref}
      />
      <AnimatedBeam
        containerRef={containerRef}
        fromRef={div6Ref}
        toRef={div10Ref}
      />

      {/* Parallel Steps to Final Output Connections */}
      <AnimatedBeam
        containerRef={containerRef}
        fromRef={div8Ref}
        toRef={div9Ref}
      />
      <AnimatedBeam
        containerRef={containerRef}
        fromRef={div10Ref}
        toRef={div9Ref}
      />
    </div>
  );
}

const Icons = {
  sheets: () => (
    <img src="/workflowicons/sheets.png" alt="Google Sheets" width="24" height="24" />
  ),
  s3: () => (
    <img src="/workflowicons/s3.png" alt="AWS S3" width="24" height="24" />
  ),
  sqs: () => (
    <img src="/workflowicons/sqs.png" alt="AWS SQS" width="24" height="24" />
  ),
  drive: () => (
    <img src="/workflowicons/drive.png" alt="Google Drive" width="24" height="24" />
  ),
  mongodb: () => (
    <img src="/workflowicons/mongodb.png" alt="MongoDB" width="24" height="24" />
  ),
  exosphere: () => (
    <img src="/exospheresmall.png" alt="MongoDB" width="30" height="30" />
  ),
  deepseek: () => (
    <img src="/workflowicons/deepseek.png" alt="MongoDB" width="24" height="24" />
  ),
  llama: () => (
    <img src="/workflowicons/llama.png" alt="MongoDB" width="24" height="24" />
  ),
  user: () => (
    <svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="#daf5ff"
      strokeWidth="2"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
      <circle cx="12" cy="7" r="4" />
    </svg>
  ),
};
