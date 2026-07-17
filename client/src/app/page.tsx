import { HeroSection } from "@/components/landing-page/HeroSection"
import { ProductSection } from "@/components/landing-page/ProductSection"
import { AiAssistantSection } from "@/components/landing-page/AiAssistantSection"
import { McpSection } from "@/components/landing-page/McpSection"
import { Footer } from "@/components/landing-page/Footer"
import { AuthRedirect } from "@/components/landing-page/AuthRedirect"

export default function Home() {
  return (
    <>
      <AuthRedirect />
      <HeroSection />
      <ProductSection />
      <AiAssistantSection />
      <McpSection />
      <Footer />
    </>
  )
}
