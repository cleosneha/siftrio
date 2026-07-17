import { HeroSection } from "@/components/landing-page/HeroSection"
import { ProductSection } from "@/components/landing-page/ProductSection"
import { AuthRedirect } from "@/components/landing-page/AuthRedirect"

export default function Home() {
  return (
    <>
      <AuthRedirect />
      <HeroSection />
      <ProductSection />
    </>
  )
}
