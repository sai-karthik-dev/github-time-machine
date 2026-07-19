"use client";

import { useEffect, useRef, useState } from "react";
import { useScroll, useSpring, useTransform, useMotionValueEvent, motion } from "framer-motion";
import Link from "next/link";
import { 
  ArrowRightIcon, 
  ArrowDownIcon,
  BoltIcon, 
  CubeTransparentIcon, 
  ChartBarIcon, 
  ShieldCheckIcon 
} from "@heroicons/react/24/outline";

// PROP TYPES EXPOSED FOR BACKEND WIRING
interface DesertTimeMachineScrollProps {
  onConnectRepository?: () => void;
  onExplorePlatform?: () => void;
  onTraceDecision?: () => void;
  onExploreFeature?: (featureIndex: number) => void;
  onConnectGithub?: () => void;
  onMapSystem?: () => void;
  onBuildContext?: () => void;
}

const TOTAL_FRAMES = 50;

export default function DesertTimeMachineScroll({
  onConnectRepository,
  onExplorePlatform,
  onTraceDecision,
  onExploreFeature,
  onConnectGithub,
  onMapSystem,
  onBuildContext
}: DesertTimeMachineScrollProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  const [images, setImages] = useState<HTMLImageElement[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [loadedPercent, setLoadedPercent] = useState(0);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  // 1. SCROLL PHYSICS LOGIC (Awwwards-level lerp and spring)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"],
  });

  const smoothProgress = useSpring(scrollYProgress, {
    damping: 30,
    stiffness: 150,
    restDelta: 0.0005,
  });

  // Track the frame index inside a mutable ref for resizing redraws
  const frameRef = useRef(0);

  // 2. CHECKPOINT ANIMATION TRANSLATIONS (Fade-in/hold/fade-out mappings)
  
  // 0% Scroll: Landing view. Centered title "GitHub Time Machine"
  const opacity0 = useTransform(smoothProgress, [0, 0.08, 0.12], [1, 1, 0]);
  const y0 = useTransform(smoothProgress, [0, 0.12], [0, -30]);

  // 12.5% Scroll: "Engineering intelligence for evolving codebases"
  const opacity12_5 = useTransform(smoothProgress, [0.08, 0.12, 0.18, 0.22], [0, 1, 1, 0]);
  const y12_5 = useTransform(smoothProgress, [0.08, 0.125, 0.22], [20, 0, -20]);

  // 25% Scroll: Left-aligned "Know your codebase."
  const opacity25 = useTransform(smoothProgress, [0.18, 0.22, 0.30, 0.34], [0, 1, 1, 0]);
  const y25 = useTransform(smoothProgress, [0.18, 0.25, 0.34], [20, 0, -20]);

  // 37.5% Scroll: Right-aligned "Across time."
  const opacity37_5 = useTransform(smoothProgress, [0.30, 0.34, 0.42, 0.46], [0, 1, 1, 0]);
  const y37_5 = useTransform(smoothProgress, [0.30, 0.375, 0.46], [20, 0, -20]);

  // 50% Scroll: Centered text subhead
  const opacity50 = useTransform(smoothProgress, [0.42, 0.46, 0.55, 0.59], [0, 1, 1, 0]);
  const y50 = useTransform(smoothProgress, [0.42, 0.50, 0.59], [20, 0, -20]);

  // 62.5% Scroll: Frosted-glass Panel 1 (Code panel & Memory card)
  const opacity62_5 = useTransform(smoothProgress, [0.55, 0.59, 0.70, 0.75], [0, 1, 1, 0]);
  const y62_5 = useTransform(smoothProgress, [0.55, 0.625, 0.75], [30, 0, -30]);
  const pointerEvents62_5 = useTransform(smoothProgress, [0.55, 0.59, 0.70, 0.75], ["none", "auto", "auto", "none"]);

  // 87.5% Scroll: Frosted-glass Panel 2 (Features Platform trio)
  const opacity87_5 = useTransform(smoothProgress, [0.80, 0.84, 0.92, 0.95], [0, 1, 1, 0]);
  const y87_5 = useTransform(smoothProgress, [0.80, 0.875, 0.95], [30, 0, -30]);
  const pointerEvents87_5 = useTransform(smoothProgress, [0.80, 0.84, 0.92, 0.95], ["none", "auto", "auto", "none"]);

  // 100% Scroll: Frosted-glass Panel 3 (How it works list)
  const opacity100 = useTransform(smoothProgress, [0.92, 0.96, 1.0], [0, 1, 1]);
  const y100 = useTransform(smoothProgress, [0.92, 1.0], [30, 0]);
  const pointerEvents100 = useTransform(smoothProgress, [0.92, 0.96, 1.0], ["none", "auto", "auto"]);

  // Check user media preferences for motion
  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    setPrefersReducedMotion(mediaQuery.matches);
    const handler = (e: MediaQueryListEvent) => setPrefersReducedMotion(e.matches);
    mediaQuery.addEventListener("change", handler);
    return () => mediaQuery.removeEventListener("change", handler);
  }, []);

  // Preloading image sequence sequence
  useEffect(() => {
    if (prefersReducedMotion) {
      setLoaded(true);
      return;
    }

    const loadedImages: HTMLImageElement[] = [];
    let loadedCount = 0;

    for (let i = 1; i <= TOTAL_FRAMES; i++) {
      const img = new Image();
      const frameNum = String(i).padStart(3, '0');
      img.src = `/ezgif-454/ezgif-frame-${frameNum}.jpg`;
      img.onload = () => {
        loadedCount++;
        setLoadedPercent(Math.floor((loadedCount / TOTAL_FRAMES) * 100));
        if (loadedCount === TOTAL_FRAMES) {
          setImages(loadedImages);
          setLoaded(true);
        }
      };
      img.onerror = () => {
        console.error(`Error preloading frame ${frameNum}`);
        loadedCount++;
        if (loadedCount === TOTAL_FRAMES) {
          setImages(loadedImages);
          setLoaded(true);
        }
      };
      loadedImages.push(img);
    }
  }, [prefersReducedMotion]);

  // Helper to resize canvas (call on resize or initial load)
  const resizeCanvas = (canvas: HTMLCanvasElement) => {
    const parent = canvas.parentElement;
    if (!parent) return;

    const width = parent.clientWidth;
    const height = parent.clientHeight;
    
    // Scale canvas dimensions to handle high-DPI screens
    canvas.width = width * window.devicePixelRatio;
    canvas.height = height * window.devicePixelRatio;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
  };

  // Helper to draw the frame centered with cover-fit (no sizing/resets)
  const drawCanvasImage = (canvas: HTMLCanvasElement, img: HTMLImageElement) => {
    if (!img) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Cover Fit scaling math
    const imgRatio = img.width / img.height;
    const canvasRatio = canvas.width / canvas.height;

    let drawWidth = canvas.width;
    let drawHeight = canvas.height;
    let offsetX = 0;
    let offsetY = 0;

    if (imgRatio < canvasRatio) {
      drawHeight = canvas.width / imgRatio;
      offsetY = (canvas.height - drawHeight) / 2;
    } else {
      drawWidth = canvas.height * imgRatio;
      offsetX = (canvas.width - drawWidth) / 2;
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Near-black dark background color behind canvas
    ctx.fillStyle = "#0A0A0B";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = "high";
    ctx.drawImage(img, offsetX, offsetY, drawWidth, drawHeight);
  };

  // 3. CANVAS SCROLL TICK EVENT (Pure draw loop, no canvas resizing resets)
  useMotionValueEvent(smoothProgress, "change", (latest) => {
    if (prefersReducedMotion || images.length < TOTAL_FRAMES) return;

    // Linear mapping scroll 0..1 to index 0..(TOTAL_FRAMES-1) clamped for spring physics overshooting
    const index = Math.max(0, Math.min(Math.floor(latest * TOTAL_FRAMES), TOTAL_FRAMES - 1));
    frameRef.current = index;

    const canvas = canvasRef.current;
    if (!canvas) return;

    drawCanvasImage(canvas, images[index]);
  });

  // Handle page resizing and initial image rendering
  useEffect(() => {
    if (!loaded || images.length === 0 || prefersReducedMotion) return;
    const canvas = canvasRef.current;
    if (!canvas) return;

    const handleResize = () => {
      resizeCanvas(canvas);
      drawCanvasImage(canvas, images[frameRef.current]);
    };

    window.addEventListener("resize", handleResize);
    handleResize(); // Initial draw

    return () => window.removeEventListener("resize", handleResize);
  }, [loaded, images, prefersReducedMotion]);

  // REDUCED MOTION STATIC RENDER FALLBACK
  if (prefersReducedMotion) {
    return (
      <div className="relative w-full bg-[#0A0A0B] text-white py-24 px-6 md:px-16 flex flex-col gap-32">
        {/* Simple fade-in static representation of content stacked in flow */}
        
        {/* Hero Section */}
        <section className="text-center max-w-4xl mx-auto py-16">
          <span className="text-[10px] tracking-[0.25em] font-mono text-white/40 uppercase mb-4 block font-bold">
            ⌁ GITHUB TIME MACHINE
          </span>
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tighter mb-6 leading-none">
            Know your codebase.<br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-violet-400 font-serif italic font-normal">
              Across time.
            </span>
          </h1>
          <p className="text-white/50 text-base max-w-2xl mx-auto mb-10 leading-relaxed">
            GitHub Time Machine turns repository history into architectural understanding—so your team can change software with confidence.
          </p>
        </section>

        {/* Panel 1 */}
        <section className="bg-white/[0.04] backdrop-blur-md border border-white/10 rounded-2xl p-6 md:p-10 max-w-5xl mx-auto w-full">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6 mb-10">
            <div className="text-left">
              <span className="text-[10px] tracking-[0.25em] font-mono text-white/40 uppercase mb-2 block font-bold">
                CONNECTIVITY
              </span>
              <h2 className="text-2xl md:text-3xl font-bold tracking-tight">Index repository structure</h2>
            </div>
            <div className="flex items-center gap-4">
              <button 
                onClick={onConnectRepository}
                className="bg-gradient-to-r from-pink-500 to-indigo-600 hover:from-pink-600 hover:to-indigo-700 text-white font-medium text-sm px-6 py-3 rounded-full flex items-center gap-2 transition-all"
              >
                Connect your repository <ArrowRightIcon className="w-4 h-4" />
              </button>
              <button 
                onClick={onExplorePlatform}
                className="text-white/50 hover:text-white transition-colors text-sm font-medium"
              >
                Explore platform
              </button>
            </div>
          </div>
          
          {/* Static code layout */}
          <div className="grid grid-cols-1 lg:grid-cols-3 border border-white/10 rounded-xl overflow-hidden bg-black/40">
            <div className="lg:col-span-2 border-r border-white/10 p-6 font-mono text-xs text-white/70 leading-relaxed">
              <div className="flex items-center gap-2 mb-4 border-b border-white/5 pb-2">
                <span className="w-2.5 h-2.5 rounded-full bg-white/10" />
                <span className="w-2.5 h-2.5 rounded-full bg-white/10" />
                <span className="w-2.5 h-2.5 rounded-full bg-white/10" />
                <span className="text-white/40 text-[10px] ml-2">analysis / architecture.ts</span>
              </div>
              <p className="text-white/40">01 <span className="text-indigo-300">import</span> &#123; <span className="text-white">history</span> &#125; <span className="text-indigo-300">from</span> <span className="text-emerald-300">&apos;@github/time-machine&apos;</span></p>
              <p className="text-white/30">02 <span className="text-white/30">// Every decision has a story.</span></p>
              <p className="text-white/40">03 <span className="text-indigo-300">const</span> system = history.<span className="bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded-md font-semibold border border-indigo-500/30">understand</span>(repository)</p>
              <p className="text-white/40">04 <span className="text-indigo-300">await</span> system.<span className="bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded-md font-semibold border border-indigo-500/30">predict</span>(change)</p>
            </div>
            <div className="p-6 bg-white/[0.02]">
              <div className="flex items-center gap-2 mb-3 text-indigo-400 font-mono text-[9px] tracking-wider uppercase font-bold">
                <BoltIcon className="w-3.5 h-3.5" /> ARCHITECT&apos;S MEMORY
              </div>
              <p className="text-xs text-white/70 leading-relaxed mb-4">
                Authentication changed 14 times. The current boundary was introduced to isolate billing.
              </p>
              <button 
                onClick={onTraceDecision}
                className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors inline-flex items-center gap-1 font-semibold"
              >
                Trace the decision <ArrowRightIcon className="w-3 h-3" />
              </button>
            </div>
          </div>
        </section>

        {/* Panel 2 */}
        <section className="bg-white/[0.04] backdrop-blur-md border border-white/10 rounded-2xl p-6 md:p-10 max-w-5xl mx-auto w-full">
          <div className="flex flex-col md:flex-row justify-between items-start gap-4 mb-8">
            <div>
              <span className="text-[10px] tracking-[0.25em] font-mono text-white/40 uppercase mb-2 block font-bold">
                THE PLATFORM
              </span>
              <h2 className="text-3xl font-black tracking-tight text-white/90">From code history to engineering clarity.</h2>
            </div>
            <p className="text-white/50 text-sm max-w-xs md:text-right">
              Give every engineer the context of the people and decisions that came before them.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-black/30 border border-white/5 rounded-xl p-6 relative">
              <span className="absolute top-4 right-4 text-xs font-mono text-white/20">01</span>
              <CubeTransparentIcon className="w-8 h-8 text-indigo-400 mb-6" />
              <h3 className="text-base font-bold text-white mb-2">Software DNA</h3>
              <p className="text-xs text-white/50 leading-relaxed mb-4">
                See the structure, ownership, churn, and complexity that shape every module.
              </p>
              <button 
                onClick={() => onExploreFeature?.(0)}
                className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors font-semibold"
              >
                Explore &rarr;
              </button>
            </div>
            
            <div className="bg-black/30 border border-white/10 rounded-xl p-6 relative shadow-xl shadow-indigo-500/5">
              <span className="absolute top-4 right-4 text-xs font-mono text-white/20">02</span>
              <ChartBarIcon className="w-8 h-8 text-indigo-400 mb-6" />
              <h3 className="text-base font-bold text-white mb-2">Architecture timeline</h3>
              <p className="text-xs text-white/50 leading-relaxed mb-4">
                Travel through commits to understand when—and why—your system changed.
              </p>
              <button 
                onClick={() => onExploreFeature?.(1)}
                className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors font-semibold"
              >
                Explore &rarr;
              </button>
            </div>

            <div className="bg-black/30 border border-white/5 rounded-xl p-6 relative">
              <span className="absolute top-4 right-4 text-xs font-mono text-white/20">03</span>
              <ShieldCheckIcon className="w-8 h-8 text-indigo-400 mb-6" />
              <h3 className="text-base font-bold text-white mb-2">Change intelligence</h3>
              <p className="text-xs text-white/50 leading-relaxed mb-4">
                Know what breaks before it does with graph-powered impact analysis.
              </p>
              <button 
                onClick={() => onExploreFeature?.(2)}
                className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors font-semibold"
              >
                Explore &rarr;
              </button>
            </div>
          </div>
        </section>

        {/* Panel 3 */}
        <section className="bg-white/[0.04] backdrop-blur-md border border-white/10 rounded-2xl p-6 md:p-10 max-w-5xl mx-auto w-full mb-16">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
            <div>
              <span className="text-[10px] tracking-[0.25em] font-mono text-white/40 uppercase mb-2 block font-bold">
                HOW IT WORKS
              </span>
              <h2 className="text-4xl font-extrabold tracking-tight">
                Your repository,<br/>
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-violet-400 font-serif italic font-normal">
                  remembered.
                </span>
              </h2>
            </div>

            <div className="flex flex-col gap-6">
              <div className="border-b border-white/5 pb-4 cursor-pointer" onClick={onConnectGithub}>
                <span className="text-[10px] font-mono text-indigo-400 font-bold block mb-1">01</span>
                <h4 className="text-sm font-bold mb-1">Connect GitHub</h4>
                <p className="text-xs text-white/50">Securely select the repository your team wants to understand.</p>
              </div>
              <div className="border-b border-white/5 pb-4 cursor-pointer" onClick={onMapSystem}>
                <span className="text-[10px] font-mono text-indigo-400 font-bold block mb-1">02</span>
                <h4 className="text-sm font-bold mb-1">Map the system</h4>
                <p className="text-xs text-white/50">We connect code, dependencies, commits, and decisions into one living graph.</p>
              </div>
              <div className="pb-2 cursor-pointer" onClick={onBuildContext}>
                <span className="text-[10px] font-mono text-indigo-400 font-bold block mb-1">03</span>
                <h4 className="text-sm font-bold mb-1">Build with context</h4>
                <p className="text-xs text-white/50">Ask questions, simulate changes, and navigate the future with confidence.</p>
              </div>
            </div>
          </div>
        </section>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="relative h-[900vh] bg-[#0A0A0B] select-none">
      {/* Loading Overlay */}
      {!loaded && (
        <div className="fixed inset-0 flex flex-col items-center justify-center bg-[#0A0A0B] z-50">
          <div className="w-16 h-16 relative mb-6">
            <div className="absolute inset-0 rounded-full border-2 border-white/5" />
            <div className="absolute inset-0 rounded-full border-t-2 border-indigo-500 animate-spin" />
          </div>
          <span className="text-[10px] tracking-[0.25em] font-mono text-white/40 uppercase">
            PRELOADING TIMELINE ({loadedPercent}%)
          </span>
        </div>
      )}

      {/* STICKY RENDERED VIEWPORT CONTAINER */}
      <div className="sticky top-0 h-screen w-full flex items-center justify-center overflow-hidden z-0">
        <canvas ref={canvasRef} className="block pointer-events-none" />
        
        {/* Continuous Soft Dark Vignette Gradient Layer for Text Legibility */}
        <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(circle_at_center,rgba(10,10,11,0.2)_10%,#0A0A0B_95%)] bg-[#0A0A0B]/20" />
        
        {/* Noise overlay for depth */}
        <div className="absolute inset-0 pointer-events-none opacity-[0.02] bg-noise" />

        {/* SYNCED CHECKPOINT LAYERS */}
        <div className="absolute inset-0 z-10 pointer-events-none">
          
          {/* Checkpoint 0%: Centered Title */}
          <motion.div 
            style={{ opacity: opacity0, y: y0 }}
            className="absolute inset-0 flex items-center justify-center flex-col text-center px-6 pointer-events-none"
          >
            <span className="text-[10px] tracking-[0.25em] font-mono text-white/40 uppercase mb-4 block font-bold">
              ⌁ ARCHITECTURAL TIMELINE
            </span>
            <h1 className="text-6xl md:text-8xl font-black tracking-tighter text-white/90 leading-none">
              GitHub<br/>
              <span className="text-white/60 font-serif italic font-normal">time machine.</span>
            </h1>
          </motion.div>

          {/* Checkpoint 12.5%: Centered Text */}
          <motion.div 
            style={{ opacity: opacity12_5, y: y12_5 }}
            className="absolute inset-0 flex items-center justify-center text-center px-6 pointer-events-none"
          >
            <h2 className="text-3xl md:text-5xl font-black tracking-tight text-white/90 max-w-3xl leading-tight">
              Engineering intelligence for evolving codebases
            </h2>
          </motion.div>

          {/* Checkpoint 25%: Left-aligned "Know your codebase." */}
          <motion.div 
            style={{ opacity: opacity25, y: y25 }}
            className="absolute inset-0 flex items-center justify-start px-8 md:px-24 pointer-events-none"
          >
            <h2 className="text-4xl md:text-6xl font-black tracking-tight text-white/90">
              Know your codebase.
            </h2>
          </motion.div>

          {/* Checkpoint 37.5%: Right-aligned "Across time." */}
          <motion.div 
            style={{ opacity: opacity37_5, y: y37_5 }}
            className="absolute inset-0 flex items-center justify-end px-8 md:px-24 text-right pointer-events-none"
          >
            <h2 className="text-4xl md:text-6xl font-black tracking-tight text-white/90">
              Across time.
            </h2>
          </motion.div>

          {/* Checkpoint 50%: Centered text */}
          <motion.div 
            style={{ opacity: opacity50, y: y50 }}
            className="absolute inset-0 flex items-center justify-center text-center px-6 pointer-events-none"
          >
            <p className="text-lg md:text-xl text-white/70 max-w-2xl leading-relaxed font-medium">
              GitHub Time Machine turns repository history into architectural understanding—so your team can change software with confidence.
            </p>
          </motion.div>

          {/* Checkpoint 62.5%: Frosted-Glass Panel 1 */}
          <motion.div 
            style={{ opacity: opacity62_5, y: y62_5, pointerEvents: pointerEvents62_5 }}
            className="absolute inset-0 flex items-center justify-center p-6"
          >
            <div className="bg-white/[0.06] backdrop-blur-lg border border-white/15 rounded-2xl p-6 md:p-8 w-full max-w-4xl shadow-2xl pointer-events-auto">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
                <div>
                  <span className="text-[10px] tracking-[0.2em] font-mono text-indigo-400 uppercase font-bold block mb-1">CONNECTIVITY</span>
                  <h3 className="text-xl font-extrabold text-white">Index codebase structure</h3>
                </div>
                <div className="flex items-center gap-4">
                  <button 
                    onClick={onConnectRepository}
                    className="bg-gradient-to-r from-pink-500 to-indigo-600 hover:from-pink-600 hover:to-indigo-700 text-white font-medium text-xs px-6 py-3 rounded-full flex items-center gap-2 transition-all shadow-lg shadow-indigo-500/20 active:scale-95"
                  >
                    Connect your repository <ArrowRightIcon className="w-3.5 h-3.5" />
                  </button>
                  <button 
                    onClick={onExplorePlatform}
                    className="text-white/50 hover:text-white transition-colors text-xs font-medium inline-flex items-center gap-1"
                  >
                    Explore the platform <ArrowDownIcon className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {/* Vercel Terminal Mockup */}
              <div className="grid grid-cols-1 lg:grid-cols-3 border border-white/10 rounded-xl overflow-hidden bg-black/50">
                <div className="lg:col-span-2 border-r border-white/10 p-5 font-mono text-xs text-white/60 leading-relaxed">
                  <div className="flex items-center justify-between mb-4 border-b border-white/5 pb-2">
                    <div className="flex items-center gap-1.5">
                      <span className="w-2.5 h-2.5 rounded-full bg-white/10" />
                      <span className="w-2.5 h-2.5 rounded-full bg-white/10" />
                      <span className="w-2.5 h-2.5 rounded-full bg-white/10" />
                      <span className="text-white/40 text-[9px] ml-2">analysis / architecture.ts</span>
                    </div>
                    <span className="flex items-center gap-1.5 text-[9px] text-emerald-400/90 font-bold uppercase tracking-wider">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" /> Live intelligence
                    </span>
                  </div>
                  <p className="mb-1"><span className="text-white/30">01</span> <span className="text-indigo-400">import</span> &#123; <span className="text-white">history</span> &#125; <span className="text-indigo-400">from</span> <span className="text-emerald-400">&apos;@github/time-machine&apos;</span></p>
                  <p className="mb-1 text-white/30"><span className="text-white/30">02</span> // Every decision has a story.</p>
                  <p className="mb-1"><span className="text-white/30">03</span> <span className="text-indigo-400">const</span> system = history.<span className="bg-indigo-500/30 text-indigo-300 px-2 py-0.5 rounded border border-indigo-500/20 font-semibold">understand</span>(repository)</p>
                  <p className="mb-1"><span className="text-white/30">04</span> <span className="text-indigo-400">await</span> system.<span className="bg-indigo-500/30 text-indigo-300 px-2 py-0.5 rounded border border-indigo-500/20 font-semibold">predict</span>(change)</p>
                </div>
                <div className="p-5 flex flex-col justify-between bg-white/[0.01]">
                  <div>
                    <div className="flex items-center gap-1.5 text-indigo-400 font-mono text-[9px] tracking-wider uppercase font-bold mb-3">
                      <BoltIcon className="w-3.5 h-3.5" /> ARCHITECT&apos;S MEMORY
                    </div>
                    <p className="text-xs text-white/70 leading-relaxed mb-4">
                      Authentication changed 14 times. The current boundary was introduced to isolate billing.
                    </p>
                    <button 
                      onClick={onTraceDecision}
                      className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors inline-flex items-center gap-1 font-semibold"
                    >
                      Trace the decision <ArrowRightIcon className="w-3 h-3" />
                    </button>
                  </div>
                  <div className="mt-4 flex flex-col gap-2">
                    <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                      <div className="h-full bg-white/10 w-3/4 rounded-full" />
                    </div>
                    <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                      <div className="h-full bg-white/10 w-1/2 rounded-full" />
                    </div>
                    <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                      <div className="h-full bg-white/10 w-1/4 rounded-full" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Checkpoint 87.5%: Frosted-Glass Panel 2 */}
          <motion.div 
            style={{ opacity: opacity87_5, y: y87_5, pointerEvents: pointerEvents87_5 }}
            className="absolute inset-0 flex items-center justify-center p-6"
          >
            <div className="bg-white/[0.06] backdrop-blur-lg border border-white/15 rounded-2xl p-6 md:p-8 w-full max-w-4xl shadow-2xl pointer-events-auto">
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
                <div>
                  <span className="text-[10px] tracking-[0.2em] font-mono text-indigo-400 uppercase font-bold block mb-1">THE PLATFORM</span>
                  <h3 className="text-2xl md:text-3xl font-black text-white leading-tight">From code history to engineering clarity.</h3>
                </div>
                <p className="text-white/50 text-xs max-w-xs md:text-right leading-relaxed">
                  Give every engineer the context of the people and decisions that came before them.
                </p>
              </div>

              {/* Features trio cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                <div className="bg-black/30 border border-white/5 rounded-xl p-5 relative group hover:border-white/20 transition-all">
                  <span className="absolute top-4 right-4 text-xs font-mono text-white/15">01</span>
                  <CubeTransparentIcon className="w-8 h-8 text-indigo-400/90 mb-5" />
                  <h4 className="text-sm font-bold text-white mb-1.5">Software DNA</h4>
                  <p className="text-xs text-white/50 leading-relaxed mb-4">
                    See the structure, ownership, churn, and complexity that shape every module.
                  </p>
                  <button 
                    onClick={() => onExploreFeature?.(0)}
                    className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold inline-flex items-center gap-1 transition-colors"
                  >
                    Explore &rarr;
                  </button>
                </div>

                {/* Emphasized Middle Card */}
                <div className="bg-black/40 border border-white/15 rounded-xl p-5 relative group hover:border-white/25 transition-all shadow-xl shadow-indigo-500/5 ring-1 ring-white/5">
                  <span className="absolute top-4 right-4 text-xs font-mono text-white/25">02</span>
                  <ChartBarIcon className="w-8 h-8 text-indigo-400 mb-5" />
                  <h4 className="text-sm font-bold text-white mb-1.5">Architecture timeline</h4>
                  <p className="text-xs text-white/50 leading-relaxed mb-4">
                    Travel through commits to understand when—and why—your system changed.
                  </p>
                  <button 
                    onClick={() => onExploreFeature?.(1)}
                    className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold inline-flex items-center gap-1 transition-colors"
                  >
                    Explore &rarr;
                  </button>
                </div>

                <div className="bg-black/30 border border-white/5 rounded-xl p-5 relative group hover:border-white/20 transition-all">
                  <span className="absolute top-4 right-4 text-xs font-mono text-white/15">03</span>
                  <ShieldCheckIcon className="w-8 h-8 text-indigo-400/90 mb-5" />
                  <h4 className="text-sm font-bold text-white mb-1.5">Change intelligence</h4>
                  <p className="text-xs text-white/50 leading-relaxed mb-4">
                    Know what breaks before it does with graph-powered impact analysis.
                  </p>
                  <button 
                    onClick={() => onExploreFeature?.(2)}
                    className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold inline-flex items-center gap-1 transition-colors"
                  >
                    Explore &rarr;
                  </button>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Checkpoint 100%: Frosted-Glass Panel 3 (Final state) */}
          <motion.div 
            style={{ opacity: opacity100, y: y100, pointerEvents: pointerEvents100 }}
            className="absolute inset-0 flex items-center justify-center p-6"
          >
            <div className="bg-white/[0.06] backdrop-blur-lg border border-white/15 rounded-2xl p-6 md:p-10 w-full max-w-4xl shadow-2xl pointer-events-auto">
              <div className="grid grid-cols-1 md:grid-cols-5 gap-8 items-center">
                <div className="md:col-span-2">
                  <span className="text-[10px] tracking-[0.2em] font-mono text-indigo-400 uppercase font-bold block mb-2">HOW IT WORKS</span>
                  <h3 className="text-3xl md:text-4xl font-extrabold text-white leading-tight">
                    Your repository,<br/>
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-violet-400 font-serif italic font-normal">
                      remembered.
                    </span>
                  </h3>
                </div>

                {/* Vertical Steps */}
                <div className="md:col-span-3 flex flex-col gap-5">
                  <div 
                    onClick={onConnectGithub}
                    className="border-b border-white/5 pb-4 cursor-pointer group"
                  >
                    <span className="text-[10px] font-mono text-indigo-400 font-bold block mb-1 group-hover:translate-x-1 transition-transform">01</span>
                    <h4 className="text-sm font-bold text-white mb-1 group-hover:text-indigo-300 transition-colors">Connect GitHub</h4>
                    <p className="text-xs text-white/50 leading-relaxed">Securely select the repository your team wants to understand.</p>
                  </div>
                  
                  <div 
                    onClick={onMapSystem}
                    className="border-b border-white/5 pb-4 cursor-pointer group"
                  >
                    <span className="text-[10px] font-mono text-indigo-400 font-bold block mb-1 group-hover:translate-x-1 transition-transform">02</span>
                    <h4 className="text-sm font-bold text-white mb-1 group-hover:text-indigo-300 transition-colors">Map the system</h4>
                    <p className="text-xs text-white/50 leading-relaxed">We connect code, dependencies, commits, and decisions into one living graph.</p>
                  </div>

                  <div 
                    onClick={onBuildContext}
                    className="cursor-pointer group"
                  >
                    <span className="text-[10px] font-mono text-indigo-400 font-bold block mb-1 group-hover:translate-x-1 transition-transform">03</span>
                    <h4 className="text-sm font-bold text-white mb-1 group-hover:text-indigo-300 transition-colors">Build with context</h4>
                    <p className="text-xs text-white/50 leading-relaxed">Ask questions, simulate changes, and navigate the future with confidence.</p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>

        </div>
      </div>
    </div>
  );
}
