import { Header } from "@/components/header"
import { HeroSection } from "@/components/sections/hero"
import { AboutSection } from "@/components/sections/about"
import { ProjectsSection } from "@/components/sections/projects"
import { SkillsSection } from "@/components/sections/skills"
import { BlogSection } from "@/components/sections/blog"
import { ContactSection } from "@/components/sections/contact"
import { Footer } from "@/components/footer"

export default function Home() {
  return (
    <>
      <Header />
      <main>
        <HeroSection />
        <AboutSection />
        <ProjectsSection />
        <SkillsSection />
        <BlogSection />
        <ContactSection />
      </main>
      <Footer />
    </>
  )
}
