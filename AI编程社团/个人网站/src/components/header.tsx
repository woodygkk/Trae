"use client"

import Link from "next/link"
import { Menu, X, Code2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import React from "react"
import { cn } from "@/lib/utils"

const navItems = [
  { name: "首页", href: "#hero" },
  { name: "关于", href: "#about" },
  { name: "作品集", href: "#projects" },
  { name: "技能", href: "#skills" },
  { name: "博客", href: "#blog" },
  { name: "联系", href: "#contact" },
]

export function Header() {
  const [menuOpen, setMenuOpen] = React.useState(false)
  const [scrolled, setScrolled] = React.useState(false)

  React.useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50)
    }
    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  return (
    <header
      className={cn(
        "fixed top-0 left-0 right-0 z-50 transition-all duration-300",
        scrolled
          ? "bg-white/80 backdrop-blur-md border-b border-gray-200 shadow-sm"
          : "bg-transparent"
      )}
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <Code2 className="h-8 w-8 text-primary" />
            <span className="font-bold text-xl">AI编程社团</span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              <Button key={item.name} asChild variant="ghost" size="sm">
                <Link href={item.href} className="text-sm">
                  {item.name}
                </Link>
              </Button>
            ))}
          </nav>

          {/* CTA Button (Desktop) */}
          <div className="hidden md:block">
            <Button asChild size="sm">
              <Link href="#contact">联系我</Link>
            </Button>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="md:hidden p-2"
            aria-label={menuOpen ? "关闭菜单" : "打开菜单"}
          >
            {menuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Navigation */}
      {menuOpen && (
        <div className="md:hidden absolute top-full left-0 right-0 bg-white border-b border-gray-200 shadow-lg">
          <nav className="flex flex-col p-4 gap-2">
            {navItems.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                onClick={() => setMenuOpen(false)}
                className="py-3 px-4 text-sm font-medium hover:bg-gray-100 rounded-lg"
              >
                {item.name}
              </Link>
            ))}
            <Button asChild className="mt-2">
              <Link href="#contact" onClick={() => setMenuOpen(false)}>
                联系我
              </Link>
            </Button>
          </nav>
        </div>
      )}
    </header>
  )
}
