import Link from "next/link";
import { ArrowLeftIcon, ArrowRightIcon, CheckIcon, CircleStackIcon, CodeBracketIcon, LockClosedIcon, SparklesIcon } from "@heroicons/react/24/outline";
import { AnalysisProgress, ToastNotification } from "../components/ExperienceEnhancements";
import { Suspense } from "react";

function GitHubMark() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 .7a11.3 11.3 0 0 0-3.57 22.02c.56.1.77-.24.77-.54v-2.1c-3.13.68-3.8-1.33-3.8-1.33-.5-1.3-1.25-1.65-1.25-1.65-1.02-.7.08-.69.08-.69 1.13.08 1.72 1.16 1.72 1.16 1 1.71 2.63 1.22 3.27.94.1-.73.39-1.22.71-1.5-2.5-.29-5.13-1.25-5.13-5.57 0-1.23.44-2.23 1.16-3.02-.12-.28-.5-1.43.11-2.98 0 0 .95-.3 3.1 1.15A10.7 10.7 0 0 1 12 6.9c.96 0 1.93.13 2.83.38 2.16-1.46 3.1-1.15 3.1-1.15.62 1.55.23 2.7.12 2.98.72.8 1.16 1.8 1.16 3.02 0 4.33-2.64 5.27-5.15 5.55.4.35.76 1.03.76 2.08v2.99c0 .3.2.65.78.54A11.3 11.3 0 0 0 12 .7Z"/></svg> }

export default function LoginPage() {
  return <main className="login-page">
    <aside className="login-brand">
      <Link href="/" className="brand"><span className="brand-mark">⌁</span>GITHUB <em>TIME MACHINE</em></Link>
      <div className="login-story"><div className="story-chip"><SparklesIcon/> REPOSITORY INTELLIGENCE</div><h2>Every pull request<br/>has a <i>past.</i></h2><p>Turn thousands of commits into the context your team needs to make its next move.</p></div>
      <div className="repo-preview"><div className="repo-preview-top"><span><GitHubMark/> octo-labs / <b>atlas</b></span><span className="analysis-status"><i/> Analysis ready</span></div><div className="branch-line"><span className="branch-dot"/>main <span>·</span> 1,248 commits mapped</div><div className="repo-stat"><CircleStackIcon/><div><b>Architecture map</b><span>86 modules · 312 dependencies</span></div><ArrowRightIcon/></div><AnalysisProgress/></div>
      <div className="security-note"><LockClosedIcon/> Read-only access. You decide which repositories to analyze.</div>
    </aside>
    <section className="login-panel"><Link className="back" href="/"><ArrowLeftIcon/> Back to home</Link><div className="login-content"><div className="small-caps">WELCOME TO GITHUB TIME MACHINE</div><h1>Start with your<br/><i>repository&apos;s story.</i></h1><p>Connect your GitHub account to trace the decisions, dependencies, and hidden context behind your codebase.</p><a className="github-button" href="/api/auth/github"><GitHubMark/>Continue with GitHub <ArrowRightIcon/></a><p className="signin-note">You&apos;ll be securely redirected to GitHub to authorize access.</p><div className="permissions"><span>What GitHub Time Machine can access</span><p><CheckIcon/> Repositories you explicitly choose</p><p><CheckIcon/> Commit history, branches, and pull requests</p><p><CheckIcon/> Read-only code and repository metadata</p></div><div className="terms">By continuing, you agree to our <a href="#">Terms of service</a> and <a href="#">Privacy policy</a>.</div></div><CodeBracketIcon className="corner-code"/></section>
  <Suspense fallback={null}><ToastNotification /></Suspense></main>;
}
