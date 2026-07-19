"use client";

import { useEffect, useRef, useState } from "react";
import { useScroll, useSpring, useTransform, useMotionValueEvent, motion } from "framer-motion";
import Link from "next/link";
import { ArrowRightIcon } from "@heroicons/react/24/outline";

export default function Desert() {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  const [images, setImages] = useState<HTMLImageElement[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [loadedPercent, setLoadedPercent] = useState(0);

  // useScroll tracks scroll progress of the container
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"],
  });

  // Smooth the scroll progress to ensure jitter-free interpolations
  const smoothProgress = useSpring(scrollYProgress, {
    damping: 35,
    stiffness: 180,
    restDelta: 0.0005,
  });

  // Track current frame ref for resize redrawing
  const frameRef = useRef(0);

  // Map scroll progress to text overlay opacities and offsets
  const opacity0 = useTransform(smoothProgress, [0, 0.08, 0.14, 0.18], [1, 1, 0, 0]);
  const y0 = useTransform(smoothProgress, [0, 0.18], [0, -40]);

  const opacity30 = useTransform(smoothProgress, [0.18, 0.25, 0.38, 0.45], [0, 1, 1, 0]);
  const y30 = useTransform(smoothProgress, [0.18, 0.45], [30, -30]);

  const opacity60 = useTransform(smoothProgress, [0.45, 0.52, 0.68, 0.75], [0, 1, 1, 0]);
  const y60 = useTransform(smoothProgress, [0.45, 0.75], [30, -30]);

  const opacity90 = useTransform(smoothProgress, [0.75, 0.85, 1], [0, 1, 1]);
  const y90 = useTransform(smoothProgress, [0.75, 1], [30, 0]);

  // Preload images on client mount
  useEffect(() => {
    const loadedImages: HTMLImageElement[] = [];
    let loadedCount = 0;
    const totalImages = 50;

    for (let i = 1; i <= totalImages; i++) {
      const img = new Image();
      const numStr = String(i).padStart(3, '0');
      img.src = `/images/ezgif-454/ezgif-frame-${numStr}.jpg`;
      img.onload = () => {
        loadedCount++;
        setLoadedPercent(Math.floor((loadedCount / totalImages) * 100));
        if (loadedCount === totalImages) {
          setImages(loadedImages);
          setLoaded(true);
        }
      };
      loadedImages.push(img);
    }
  }, []);

  // Helper function to resize canvas using device pixel ratio
  const resizeCanvas = (canvas: HTMLCanvasElement) => {
    const parent = canvas.parentElement;
    if (!parent) return;
    const width = parent.clientWidth;
    const height = parent.clientHeight;
    
    canvas.width = width * window.devicePixelRatio;
    canvas.height = height * window.devicePixelRatio;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
  };

  // Helper to draw image contained centered with a background matching fill
  const drawImageContained = (
    ctx: CanvasRenderingContext2D,
    img: HTMLImageElement,
    canvas: HTMLCanvasElement
  ) => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Calculate aspect ratios
    const imgRatio = img.width / img.height;
    const canvasRatio = canvas.width / canvas.height;

    let drawWidth = canvas.width;
    let drawHeight = canvas.height;
    let offsetX = 0;
    let offsetY = 0;

    // Standard Contain Fit logic
    if (imgRatio > canvasRatio) {
      // Image is wider than canvas
      drawHeight = canvas.width / imgRatio;
      offsetY = (canvas.height - drawHeight) / 2;
    } else {
      // Image is taller than canvas
      drawWidth = canvas.height * imgRatio;
      offsetX = (canvas.width - drawWidth) / 2;
    }

    // Set page matching dark background behind image bounds
    ctx.fillStyle = "#050505";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Enable high-quality rendering
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = "high";

    ctx.drawImage(img, offsetX, offsetY, drawWidth, drawHeight);
  };

  // Canvas drawing handler reacting to scroll ticks directly
  useMotionValueEvent(smoothProgress, "change", (latest) => {
    if (images.length < 50) return;
    
    // Map latest progress 0..1 to index 0..49
    const index = Math.min(Math.floor(latest * 50), 49);
    frameRef.current = index;

    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    drawImageContained(ctx, images[index], canvas);
  });

  // Canvas sizing and initial rendering on resize/load
  useEffect(() => {
    if (!loaded || images.length === 0) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const handleResize = () => {
      resizeCanvas(canvas);
      drawImageContained(ctx, images[frameRef.current], canvas);
    };

    window.addEventListener("resize", handleResize);
    handleResize(); // Initial draw

    return () => window.removeEventListener("resize", handleResize);
  }, [loaded, images]);

  return (
    <div ref={containerRef} className="relative h-[400vh] bg-[#050505] select-none">
      {/* Loading overlay */}
      {!loaded && (
        <div className="fixed inset-0 flex flex-col items-center justify-center bg-[#050505] z-50">
          <div className="w-16 h-16 relative">
            <div className="absolute inset-0 rounded-full border-2 border-white/5" />
            <div className="absolute inset-0 rounded-full border-t-2 border-white animate-spin" />
          </div>
          <span className="text-[10px] tracking-[0.25em] font-mono text-white/50 uppercase mt-6">
            Loading Time Machine ({loadedPercent}%)
          </span>
        </div>
      )}

      {/* Sticky Screen Layer containing the canvas, vignette, and text overlays */}
      <div className="sticky top-0 h-screen w-full flex items-center justify-center overflow-hidden z-0">
        <canvas ref={canvasRef} className="block pointer-events-none" />
        
        {/* Vignette Overlay for perfect seamless blending into #050505 page background */}
        <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(circle_at_center,transparent_30%,#050505_95%)]" />
        
        {/* Text overlays layered absolutely over the canvas inside the sticky container */}
        <div className="absolute inset-0 z-10 pointer-events-none">
          
          {/* 0% Scroll Text Overlay */}
          <motion.div 
            style={{ opacity: opacity0, y: y0 }}
            className="absolute inset-0 flex items-center justify-center flex-col text-center px-6"
          >
            <span className="text-[10px] tracking-[0.25em] uppercase text-white/40 block mb-4 font-mono font-bold">
              ⌁ GITHUB TIME MACHINE
            </span>
            <h1 className="text-6xl md:text-8xl font-black tracking-tighter text-white/90 leading-none">
              Github<br/><span className="text-white/60 font-serif italic font-normal">time machine</span>
            </h1>
            <p className="mt-6 text-white/40 text-sm md:text-base max-w-md mx-auto">
              Travel through repository history. Map developer ownership, files, and architecture over time.
            </p>
          </motion.div>

          {/* 30% Scroll Text Overlay */}
          <motion.div 
            style={{ opacity: opacity30, y: y30 }}
            className="absolute inset-0 flex items-center justify-start px-8 md:px-24"
          >
            <div className="max-w-xl text-left">
              <span className="text-[10px] tracking-[0.25em] uppercase text-white/40 block mb-3 font-mono font-bold">
                01 / EVOLVING SYSTEMS
              </span>
              <h2 className="text-4xl md:text-6xl font-black tracking-tight text-white/90 leading-tight">
                Engineering intelligence for evolving codebases
              </h2>
              <p className="mt-4 text-white/40 text-sm md:text-base">
                Identify code churn, map structural patterns, and understand the structural evolution of complex codebases.
              </p>
            </div>
          </motion.div>

          {/* 60% Scroll Text Overlay */}
          <motion.div 
            style={{ opacity: opacity60, y: y60 }}
            className="absolute inset-0 flex items-center justify-end px-8 md:px-24"
          >
            <div className="max-w-xl text-right">
              <span className="text-[10px] tracking-[0.25em] uppercase text-white/40 block mb-3 font-mono font-bold">
                02 / CODE SEARCH
              </span>
              <h2 className="text-4xl md:text-6xl font-black tracking-tight text-white/90 leading-tight">
                Know your codebase.
              </h2>
              <p className="mt-4 text-white/40 text-sm md:text-base">
                Instantly decode why, when, and who introduced every single abstraction in your system.
              </p>
            </div>
          </motion.div>

          {/* 90% Scroll Text Overlay */}
          <motion.div 
            style={{ opacity: opacity90, y: y90 }}
            className="absolute inset-0 flex items-center justify-center flex-col text-center px-6"
          >
            <span className="text-[10px] tracking-[0.25em] uppercase text-white/40 block mb-4 font-mono font-bold">
              03 / INSTANT INSIGHT
            </span>
            <h2 className="text-5xl md:text-7xl font-black tracking-tighter text-white/90 leading-none mb-6">
              Any Time.
            </h2>
            <p className="text-white/40 text-sm md:text-base max-w-md mb-8">
              Connect your repository and unlock a deep intelligence timeline of your product development history.
            </p>
            <div className="flex flex-col sm:flex-row items-center gap-4 pointer-events-auto">
              <Link
                href="/login"
                className="inline-flex items-center gap-2 bg-white text-black hover:bg-white/90 px-8 py-4 rounded-full font-medium transition-all shadow-xl hover:translate-y-[-2px] active:translate-y-0"
              >
                Connect your repository <ArrowRightIcon className="w-4 h-4" />
              </Link>
              <Link
                href="/login"
                className="text-white/50 hover:text-white text-sm font-medium transition-colors"
              >
                Explore platform
              </Link>
            </div>
          </motion.div>

        </div>
      </div>
    </div>
  );
}
