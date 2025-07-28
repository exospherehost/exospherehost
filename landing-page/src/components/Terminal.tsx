import {
    AnimatedSpan,
    Terminal,
    TypingAnimation,
  } from "@/components/magicui/terminal";
  
  export function TerminalDemo() {
    return (
      <Terminal>
        <TypingAnimation>&gt; pnpm dlx shadcn@latest init</TypingAnimation>
        
        <AnimatedSpan delay={500} className="text-[#e4587d]">
          <span>✔ Preflight checks.</span>
        </AnimatedSpan>
  
        <AnimatedSpan delay={800} className="text-[#e4587d]">
          <span>✔ Verifying framework. Found Next.js.</span>
        </AnimatedSpan>
  
        <AnimatedSpan delay={1100} className="text-[#e4587d]">
          <span>✔ Validating Tailwind CSS.</span>
        </AnimatedSpan>
  
        <AnimatedSpan delay={1400} className="text-[#e4587d]">
          <span>✔ Validating import alias.</span>
        </AnimatedSpan>
  
        <AnimatedSpan delay={1700} className="text-[#e4587d]">
          <span>✔ Writing components.json.</span>
        </AnimatedSpan>
  
        <AnimatedSpan delay={2000} className="text-[#e4587d]">
          <span>✔ Checking registry.</span>
        </AnimatedSpan>
  
        <AnimatedSpan delay={2300} className="text-[#e4587d]">
          <span>✔ Updating tailwind.config.ts</span>
        </AnimatedSpan>
  
        <AnimatedSpan delay={2600} className="text-[#e4587d]">
          <span>✔ Updating app/globals.css</span>
        </AnimatedSpan>
  
        <AnimatedSpan delay={2900} className="text-[#e4587d]">
          <span>✔ Installing dependencies.</span>
        </AnimatedSpan>
  
        <AnimatedSpan delay={3200} className="text-[#e4587d]">
          <span>ℹ Updated 1 file:</span>
          <span className="pl-2">- lib/utils.ts</span>
        </AnimatedSpan>
  
        <TypingAnimation delay={3500} className="text-[#66d1b5]">
          Success! Project initialization completed.
        </TypingAnimation>
  
        <TypingAnimation delay={3800} className="text-[#66d1b5]">
          You may now add components.
        </TypingAnimation>
      </Terminal>
    );
  }
  