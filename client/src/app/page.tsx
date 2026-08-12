import { HeroSection } from "@/components/landing-page/HeroSection"
import { HowSiftrioWorks } from "@/components/landing-page/HowSiftrioWorks"
import { ProductSection } from "@/components/landing-page/ProductSection"
import { AiAssistantSection } from "@/components/landing-page/AiAssistantSection"
import { McpSection } from "@/components/landing-page/McpSection"
import { Footer } from "@/components/landing-page/Footer"

export default function Home() {
  return (
    <>
      <HeroSection />
      <HowSiftrioWorks />
      <ProductSection />
      <AiAssistantSection />
      <McpSection />
      <Footer />
    </>
  )
}
