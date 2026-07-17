import { HeroSection } from "@/components/landing-page/HeroSection"
import { AuthRedirect } from "@/components/landing-page/AuthRedirect"

export default function Home() {
  return (
    <>
      <AuthRedirect />
      <HeroSection />
    </>
  )
}
