"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowRightIcon } from "@heroicons/react/24/outline";
import DesertTimeMachineScroll from "./components/DesertTimeMachineScroll";

export default function Home() {
  const router = useRouter();

  // WIRING UP EVENT HANDLERS TO ORIGINAL SITE DESTINATIONS
  const handleConnectRepository = () => {
    router.push("/login");
  };

  const handleExplorePlatform = () => {
    // Smooth scroll down to the last page (100% scroll depth / Panel 3)
    if (typeof window !== "undefined") {
      window.scrollTo({
        top: window.innerHeight * 8,
        behavior: "smooth",
      });
    }
  };

  const handleTraceDecision = () => {
    // Smooth scroll down to Panel 2 (Platform Feature Trio)
    // 87.5% of 900vh is roughly 7.0 * Viewport Height
    if (typeof window !== "undefined") {
      window.scrollTo({
        top: window.innerHeight * 7.0,
        behavior: "smooth",
      });
    }
  };

  const handleExploreFeature = (index: number) => {
    // Smooth scroll down to the last page (100% scroll depth / Panel 3)
    if (typeof window !== "undefined") {
      window.scrollTo({
        top: window.innerHeight * 8,
        behavior: "smooth",
      });
    }
  };

  const handleConnectGithub = () => {
    router.push("/login");
  };

  const handleMapSystem = () => {
    router.push("/login");
  };

  const handleBuildContext = () => {
    router.push("/login");
  };

  // Nav bar scroll shortcuts
  const handleNavPlatform = (e: React.MouseEvent) => {
    e.preventDefault();
    if (typeof window !== "undefined") {
      window.scrollTo({
        top: window.innerHeight * 7.8,
        behavior: "smooth",
      });
    }
  };

  const handleNavHowItWorks = (e: React.MouseEvent) => {
    e.preventDefault();
    if (typeof window !== "undefined") {
      window.scrollTo({
        top: window.innerHeight * 9,
        behavior: "smooth",
      });
    }
  };

  return (
    <main className="bg-[#0A0A0B] min-h-screen text-white/90 font-sans tracking-tight antialiased selection:bg-white selection:text-black">
      
      {/* Sleek Vercel/Linear-inspired floating glass header */}
      <header className="fixed top-0 left-0 right-0 h-20 flex items-center justify-between px-8 md:px-16 z-50 backdrop-blur-md bg-[#0A0A0B]/20 border-b border-white/10">
        <Link href="/" className="flex items-center gap-2 font-mono text-xs font-bold tracking-widest text-white">
          <span className="flex items-center justify-center w-6 h-6 border border-white/20 rounded text-sm text-white/90">⌁</span>
          GITHUB <span className="text-white/50 font-light">TIME MACHINE</span>
        </Link>
        <nav className="flex items-center gap-8">
          <a 
            href="#platform" 
            onClick={handleNavPlatform}
            className="text-xs text-white/60 hover:text-white transition-colors font-mono tracking-wider"
          >
            PLATFORM
          </a>
          <a 
            href="#how-it-works" 
            onClick={handleNavHowItWorks}
            className="text-xs text-white/60 hover:text-white transition-colors font-mono tracking-wider"
          >
            HOW IT WORKS
          </a>
          <Link 
            href="/login" 
            className="inline-flex items-center gap-1.5 bg-white/5 hover:bg-white/10 text-white text-xs px-4 py-2 rounded-full transition-all border border-white/10 font-mono"
          >
            SIGN IN <ArrowRightIcon className="w-3 h-3" />
          </Link>
        </nav>
      </header>

      {/* Synchronized Canvas Image Scrollytelling visual flow */}
      <DesertTimeMachineScroll 
        onConnectRepository={handleConnectRepository}
        onExplorePlatform={handleExplorePlatform}
        onTraceDecision={handleTraceDecision}
        onExploreFeature={handleExploreFeature}
        onConnectGithub={handleConnectGithub}
        onMapSystem={handleMapSystem}
        onBuildContext={handleBuildContext}
      />

      {/* Restyled Vercel/Linear-inspired Minimalist Footer */}
      <footer className="w-full bg-[#0A0A0B] py-10 px-8 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between gap-4 z-20 relative font-mono text-[10px] text-white/40">
        <div className="flex items-center gap-2">
          <span className="flex items-center justify-center w-5 h-5 border border-white/10 rounded text-[10px]">⌁</span>
          <span>GITHUB TIME MACHINE</span>
        </div>
        <span>Built for engineers who inherit the future.</span>
      </footer>
    </main>
  );
}
