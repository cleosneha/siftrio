export function getMcpUrl(): string {
  const backendUrl =
    process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000/api";
  const base = backendUrl.replace(/\/api\/?$/, "");
  return `${base}/mcp`;
}
