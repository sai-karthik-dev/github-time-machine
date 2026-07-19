import Link from "next/link";
import { ArrowLeftIcon, ArrowRightIcon, CheckIcon, CircleStackIcon, LockClosedIcon, SparklesIcon } from "@heroicons/react/24/outline";
import { ToastNotification } from "../components/ExperienceEnhancements";
import { Suspense } from "react";

function GitHubMark() { 
  return (
    <svg viewBox="0 0 24 24" className="w-full h-full" aria-hidden="true">
      <path fill="currentColor" d="M12 .7a11.3 11.3 0 0 0-3.57 22.02c.56.1.77-.24.77-.54v-2.1c-3.13.68-3.8-1.33-3.8-1.33-.5-1.3-1.25-1.65-1.25-1.65-1.02-.7.08-.69.08-.69 1.13.08 1.72 1.16 1.72 1.16 1 1.71 2.63 1.22 3.27.94.1-.73.39-1.22.71-1.5-2.5-.29-5.13-1.25-5.13-5.57 0-1.23.44-2.23 1.16-3.02-.12-.28-.5-1.43.11-2.98 0 0 .95-.3 3.1 1.15A10.7 10.7 0 0 1 12 6.9c.96 0 1.93.13 2.83.38 2.16-1.46 3.1-1.15 3.1-1.15.62 1.55.23 2.7.12 2.98.72.8 1.16 1.8 1.16 3.02 0 4.33-2.64 5.27-5.15 5.55.4.35.76 1.03.76 2.08v2.99c0 .3.2.65.78.54A11.3 11.3 0 0 0 12 .7Z"/>
    </svg>
  ); 
}

export default function LoginPage() {
  return (
    <main className="min-h-screen grid grid-cols-1 md:grid-cols-12 bg-[#090D1A] font-sans antialiased text-white selection:bg-indigo-500 selection:text-white select-none">
      
      {/* LEFT COLUMN: DEEP DARK MODE SIDE */}
      <aside className="md:col-span-5 bg-[#090D1A] border-b-4 border-black md:border-b-0 md:border-r-4 md:border-black p-8 md:p-12 flex flex-col justify-between relative overflow-hidden">
        
        {/* Background Grid Pattern for Neobrutalist Depth */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-20 pointer-events-none" />

        {/* Logo/Branding Header */}
        <div className="relative z-10">
          <Link href="/" className="inline-flex items-center gap-2.5 font-mono text-xs font-black tracking-widest text-indigo-300 bg-indigo-950/45 border-2 border-indigo-500/40 p-2.5 shadow-[3px_3px_0px_0px_#6366F1] hover:translate-x-[-1px] hover:translate-y-[-1px] hover:shadow-[4px_4px_0px_0px_#6366F1] active:translate-x-[1px] active:translate-y-[1px] transition-all">
            <span className="text-indigo-400 font-bold text-sm">⌁</span>GITHUB <em className="text-slate-400 font-normal font-sans not-italic">TIME MACHINE</em>
          </Link>
        </div>

        {/* Story & Branding */}
        <div className="my-auto py-10 relative z-10 flex flex-col gap-6">
          <div className="inline-flex items-center gap-1.5 bg-violet-950/50 border-2 border-violet-400/40 px-3 py-1.5 text-[9px] font-mono font-bold tracking-widest text-violet-300 shadow-[2px_2px_0px_0px_rgba(139,92,246,0.3)] w-fit uppercase">
            <SparklesIcon className="w-3.5 h-3.5 text-violet-400" /> Repository Intelligence
          </div>
          
          <h2 className="text-4xl lg:text-5xl font-black tracking-tight leading-none text-white uppercase border-b-4 border-indigo-500/10 pb-4">
            Every pull request<br/>
            has a <span className="text-indigo-400 font-serif italic font-normal lowercase">past.</span>
          </h2>
          
          <p className="text-xs md:text-sm text-slate-400 leading-relaxed max-w-sm font-medium">
            Turn thousands of commits into the context your team needs to make its next move.
          </p>

          {/* Repository Preview Card: Hard Neobrutalist design */}
          <div className="mt-4 bg-[#0D1326] border-4 border-indigo-500 p-6 rounded-none shadow-[8px_8px_0px_0px_#6366F1] flex flex-col gap-5 relative group">
            
            {/* Top row */}
            <div className="flex items-center justify-between border-b-2 border-indigo-950/60 pb-3">
              <span className="flex items-center gap-2 text-xs font-mono font-bold text-indigo-200">
                <span className="w-4 h-4 text-indigo-400"><GitHubMark /></span>
                octo-labs / <strong className="font-extrabold text-white">atlas</strong>
              </span>
              <span className="bg-emerald-950/90 border-2 border-emerald-400 text-emerald-300 rounded-none px-2 py-0.5 text-[9px] font-mono font-black flex items-center gap-1.5 shadow-[2px_2px_0px_0px_#10B981]">
                <i className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_8px_#34d399] animate-pulse" />
                Analysis ready
              </span>
            </div>

            {/* Branch info */}
            <div className="text-[10px] font-mono text-indigo-300 flex items-center gap-2 bg-indigo-950/30 px-3 py-1.5 border border-indigo-900/40 w-fit">
              <span className="w-1.5 h-1.5 rounded-full border border-emerald-400 bg-transparent inline-block" />
              main <span className="text-indigo-600">·</span> 1,248 commits mapped
            </div>

            {/* Architecture Map Stat */}
            <div className="bg-[#111A35] border-2 border-indigo-500 p-4 flex items-center justify-between gap-3 shadow-[4px_4px_0px_0px_rgba(99,102,241,0.25)] transition-transform group-hover:translate-x-[-1px] group-hover:translate-y-[-1px]">
              <div className="flex items-center gap-3">
                <CircleStackIcon className="w-5 h-5 text-indigo-400 flex-shrink-0" />
                <div className="text-left font-mono">
                  <span className="text-[11px] font-black text-indigo-200 block uppercase tracking-wider">Architecture map</span>
                  <span className="text-[10px] text-slate-400 block mt-0.5">86 modules · 312 dependencies</span>
                </div>
              </div>
              <ArrowRightIcon className="w-4 h-4 text-indigo-400" />
            </div>

            {/* Neobrutalist custom loading progress overlay */}
            <div className="border-2 border-indigo-950 bg-[#070B16] p-4 flex flex-col gap-2.5 font-mono">
              <div className="flex justify-between items-center text-[10px]">
                <span className="text-slate-400 uppercase font-black tracking-widest text-[9px]">Repository analysis</span>
                <span className="text-indigo-400 font-bold bg-indigo-950 border border-indigo-800 px-1.5 py-0.5 shadow-[1.5px_1.5px_0px_0px_#6366F1]">72%</span>
              </div>
              <div className="h-3.5 w-full bg-[#121A30] border border-indigo-950 relative overflow-hidden">
                <div className="absolute top-0 left-0 bottom-0 bg-indigo-500 border-r-2 border-indigo-400 shadow-[0_0_10px_rgba(99,102,241,0.5)]" style={{ width: "72%" }} />
              </div>
              <div className="flex items-center gap-2 text-[9px] text-indigo-300/80 mt-1">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <span>Mapping commit history and dependencies</span>
              </div>
            </div>

          </div>
        </div>

        {/* Security / Access Badge */}
        <div className="relative z-10 flex items-center gap-2 text-[10px] font-mono text-slate-500 tracking-wide mt-8 border-t border-indigo-950/60 pt-4">
          <LockClosedIcon className="w-3.5 h-3.5 text-indigo-500/80" /> 
          Read-only access. You decide which repositories to analyze.
        </div>
      </aside>

      {/* RIGHT COLUMN: CLEAN LIGHT MODE SIDE */}
      <section className="md:col-span-7 bg-[#F9FAFB] text-slate-900 p-8 md:p-16 flex flex-col justify-between min-h-screen relative">
        
        {/* Back navigation */}
        <div>
          <Link 
            href="/" 
            className="inline-flex items-center gap-2 text-xs font-mono font-bold text-slate-800 hover:text-black border-2 border-black bg-white px-3.5 py-1.5 shadow-[3px_3px_0px_0px_#000] hover:shadow-[4px_4px_0px_0px_#000] hover:translate-x-[-1px] hover:translate-y-[-1px] active:translate-x-[1px] active:translate-y-[1px] transition-all w-fit"
          >
            <ArrowLeftIcon className="w-4 h-4" /> Back to home
          </Link>
        </div>

        {/* Git Auth Form content */}
        <div className="max-w-md my-auto flex flex-col gap-6 py-12 md:py-0 text-left">
          
          <div className="text-indigo-600 text-[10px] tracking-[0.25em] font-mono font-black uppercase bg-indigo-100 border-2 border-indigo-200 px-3 py-1.5 w-fit shadow-[2px_2px_0px_0px_#6366F1]">
            Welcome to GitHub Time Machine
          </div>
          
          <h1 className="text-4xl lg:text-5xl font-black text-slate-900 tracking-tight leading-none uppercase border-b-4 border-slate-900 pb-4">
            Start with your<br/>
            <span className="text-indigo-600 font-serif italic lowercase font-normal">repository&apos;s story.</span>
          </h1>
          
          <p className="text-sm text-slate-600 leading-relaxed font-semibold">
            Connect your GitHub account to trace the decisions, dependencies, and hidden context behind your codebase.
          </p>

          {/* Neobrutalist GitHub Auth Button */}
          <div className="w-full">
            <a 
              href="/api/auth/github" 
              className="inline-flex items-center justify-between bg-black hover:bg-slate-950 text-white font-bold py-4.5 px-6 border-3 border-black rounded-none shadow-[6px_6px_0px_0px_#6366F1] hover:shadow-[8px_8px_0px_0px_#6366F1] hover:translate-x-[-2px] hover:translate-y-[-2px] active:translate-x-[1px] active:translate-y-[1px] transition-all group w-full"
            >
              <div className="flex items-center gap-3">
                <span className="w-5 h-5 flex-shrink-0 text-white"><GitHubMark /></span>
                <span className="text-xs font-mono tracking-wider uppercase font-black text-white">Continue with GitHub</span>
              </div>
              <ArrowRightIcon className="w-4 h-4 text-white group-hover:translate-x-1 transition-transform" />
            </a>
            
            <p className="text-[10px] text-slate-500 font-mono tracking-wide mt-3 text-center">
              You&apos;ll be securely redirected to GitHub to authorize access.
            </p>
          </div>

          {/* Scope Access Permissions List */}
          <div className="border-2 border-black bg-white p-5 rounded-none shadow-[4px_4px_0px_0px_rgba(0,0,0,0.15)] flex flex-col gap-3.5">
            <span className="text-[10px] font-mono font-black text-slate-800 uppercase tracking-widest border-b border-slate-100 pb-2">
              What GitHub Time Machine can access
            </span>
            <div className="flex flex-col gap-3">
              <p className="flex items-start gap-2.5 text-[11px] font-semibold text-slate-700">
                <span className="bg-emerald-100 border border-emerald-400 p-0.5 text-emerald-600 flex-shrink-0 mt-0.5"><CheckIcon className="w-3.5 h-3.5 font-bold" /></span>
                <span>Repositories you explicitly choose</span>
              </p>
              <p className="flex items-start gap-2.5 text-[11px] font-semibold text-slate-700">
                <span className="bg-emerald-100 border border-emerald-400 p-0.5 text-emerald-600 flex-shrink-0 mt-0.5"><CheckIcon className="w-3.5 h-3.5 font-bold" /></span>
                <span>Commit history, branches, and pull requests</span>
              </p>
              <p className="flex items-start gap-2.5 text-[11px] font-semibold text-slate-700">
                <span className="bg-emerald-100 border border-emerald-400 p-0.5 text-emerald-600 flex-shrink-0 mt-0.5"><CheckIcon className="w-3.5 h-3.5 font-bold" /></span>
                <span>Read-only code and repository metadata</span>
              </p>
            </div>
          </div>

          {/* Legal / Policy Links */}
          <div className="text-[10px] text-slate-500 font-medium font-mono leading-relaxed border-t-2 border-slate-200 pt-4 mt-2">
            By continuing, you agree to our <a href="#" className="underline text-slate-700 hover:text-black font-bold">Terms of service</a> and <a href="#" className="underline text-slate-700 hover:text-black font-bold">Privacy policy</a>.
          </div>

        </div>

        {/* Decorative corner branding */}
        <div className="absolute bottom-6 right-8 w-6 h-6 text-slate-300 font-mono text-xl select-none pointer-events-none">
          &lt;/&gt;
        </div>
      </section>

      {/* Toast popup notifications */}
      <Suspense fallback={null}>
        <ToastNotification />
      </Suspense>
    </main>
  );
}
