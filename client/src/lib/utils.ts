import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDistanceToNow(date: Date): string {
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffSec = Math.floor(diffMs / 1000)
  const diffMin = Math.floor(diffSec / 60)
  const diffHr = Math.floor(diffMin / 60)
  const diffDay = Math.floor(diffHr / 24)

  if (diffDay > 30) return `${Math.floor(diffDay / 30)}mo`
  if (diffDay > 0) return `${diffDay}d`
  if (diffHr > 0) return `${diffHr}h`
  if (diffMin > 0) return `${diffMin}m`
  return `${diffSec}s`
}
