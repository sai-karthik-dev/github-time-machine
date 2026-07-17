import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import crypto from "crypto";

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get("code");
  const state = searchParams.get("state");
  const clientId = process.env.GITHUB_CLIENT_ID;
  const clientSecret = process.env.GITHUB_CLIENT_SECRET;
  const redirectUri = `${origin}/api/auth/github`;

  if (code) {
    const cookieStore = await cookies();
    const storedState = cookieStore.get("oauth_state")?.value;
    cookieStore.delete("oauth_state");

    if (state && storedState && state !== storedState) {
      return NextResponse.redirect(new URL("/login?error=csrf_mismatch", origin));
    }

    if (!clientId || !clientSecret) {
      return NextResponse.redirect(new URL("/repo/275bed80-a451-481c-886c-457f436c0050", origin));
    }
    try {
      const tokenResponse = await fetch("https://github.com/login/oauth/access_token", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({
          client_id: clientId,
          client_secret: clientSecret,
          code,
          redirect_uri: redirectUri,
        }),
      });
      const tokenData = await tokenResponse.json();
      if (tokenData.error) throw new Error(tokenData.error_description || tokenData.error);
      return NextResponse.redirect(new URL("/repo/275bed80-a451-481c-886c-457f436c0050", origin));
    } catch (e: any) {
      return NextResponse.redirect(new URL(`/login?error=${encodeURIComponent(e.message || "auth_failed")}`, origin));
    }
  }

  if (!clientId) {
    return NextResponse.redirect(new URL("/login?error=github_not_configured", origin));
  }

  const oauthState = crypto.randomBytes(16).toString("hex");
  const url = new URL("https://github.com/login/oauth/authorize");
  url.searchParams.set("client_id", clientId);
  url.searchParams.set("redirect_uri", redirectUri);
  url.searchParams.set("scope", "read:user repo");
  url.searchParams.set("state", oauthState);

  const response = NextResponse.redirect(url.toString());
  response.cookies.set("oauth_state", oauthState, {
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    maxAge: 600,
    path: "/",
  });
  return response;
}
