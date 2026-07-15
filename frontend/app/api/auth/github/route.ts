import { NextResponse } from "next/server";

export function GET() {
  const clientId = process.env.GITHUB_CLIENT_ID;
  const redirectUri = process.env.NEXT_PUBLIC_GITHUB_REDIRECT_URI;
  if (!clientId || !redirectUri) return NextResponse.redirect(new URL("/login?error=github_not_configured", process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000"));
  const github = new URL("https://github.com/login/oauth/authorize");
  github.searchParams.set("client_id", clientId);
  github.searchParams.set("redirect_uri", redirectUri);
  github.searchParams.set("scope", "read:user repo");
  return NextResponse.redirect(github);
}
