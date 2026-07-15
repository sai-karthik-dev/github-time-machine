"use client";

import { CheckCircleIcon, ExclamationCircleIcon, XMarkIcon } from "@heroicons/react/24/outline";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

export function ToastNotification() {
  const params = useSearchParams();
  const [visible, setVisible] = useState(false);
  const hasError = params.get("error") === "github_not_configured";
  useEffect(() => { setVisible(true); const timeout = setTimeout(() => setVisible(false), hasError ? 7000 : 4000); return () => clearTimeout(timeout); }, [hasError]);
  if (!visible) return null;
  return <div className={`toast ${hasError ? "toast-error" : "toast-success"}`} role="status"><div>{hasError ? <ExclamationCircleIcon/> : <CheckCircleIcon/>}</div><p><b>{hasError ? "GitHub isn’t configured yet" : "You’re ready to connect"}</b><span>{hasError ? "Add your GitHub client ID and redirect URI, then try again." : "Choose a repository to begin its analysis."}</span></p><button onClick={() => setVisible(false)} aria-label="Dismiss notification"><XMarkIcon/></button></div>;
}

export function AnalysisProgress() {
  return <div className="analysis-progress"><div><span>Repository analysis</span><b>72%</b></div><div className="progress-track"><i/></div><p><span className="pulse-dot"/> Mapping commit history and dependencies</p></div>;
}

export function SkeletonAnalysis() {
  return <div className="skeleton-analysis" aria-label="Analysis data loading"><div className="skeleton-line short"/><div className="skeleton-line"/><div className="skeleton-line medium"/></div>;
}
