import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function proxy(request: NextRequest) {
  if (!request.cookies.has("access_token")) {
    return NextResponse.redirect(new URL("/", request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/meetings/:path*",
    "/projects/:path*",
    "/clients/:path*",
    "/workspaces/:path*",
    "/settings/:path*",
    "/assistant/:path*",
  ],
};
