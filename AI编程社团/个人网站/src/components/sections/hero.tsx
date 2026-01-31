"use client"

import { Button } from "@/components/ui/button"
import { ArrowDown, Code2 } from "lucide-react"
import { motion } from "framer-motion"
import Image from "next/image"

export function HeroSection() {
  return (
    <section
      id="hero"
      className="relative min-h-screen flex items-center justify-center overflow-hidden"
    >
      {/* 渐变背景 */}
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-50 via-white to-purple-50" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-purple-200/50 via-transparent to-transparent" />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        {/* 代码装饰符号 */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-sm font-mono text-purple-600 mb-4 code-decoration"
        >
          &lt; / &gt; 你好，我是 AI编程社团 &lt; / &gt;
        </motion.div>

        {/* 标题 */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6"
        >
          全栈开发者 <span className="text-purple-600">·</span> AI爱好者{" "}
          <span className="text-purple-600">·</span> 创作者
        </motion.h1>

        {/* 头像 */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mb-8"
        >
          <div className="relative w-32 h-32 mx-auto">
            <div className="absolute inset-0 bg-gradient-to-br from-purple-500 to-indigo-500 rounded-full opacity-20 animate-pulse" />
            <Image
              src="/pic/avatar.jpg"
              alt="AI编程社团头像"
              fill
              className="rounded-full object-cover border-4 border-white shadow-xl"
            />
          </div>
        </motion.div>

        {/* 标签 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="flex flex-wrap justify-center gap-3 mb-10"
        >
          {["React", "Next.js", "TypeScript", "Node.js", "AI/ML"].map((tag) => (
            <span
              key={tag}
              className="px-4 py-1.5 bg-white border border-gray-200 rounded-full text-sm font-medium text-gray-600 shadow-sm"
            >
              {tag}
            </span>
          ))}
        </motion.div>

        {/* CTA 按钮 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="flex flex-col sm:flex-row gap-4 justify-center"
        >
          <Button asChild size="lg" className="text-base">
            <a href="#projects">
              <Code2 className="mr-2 h-4 w-4" />
              查看作品集
            </a>
          </Button>
          <Button asChild size="lg" variant="outline" className="text-base">
            <a href="#contact">联系我</a>
          </Button>
        </motion.div>
      </div>

      {/* 向下滚动提示 */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1, duration: 0.6 }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2"
      >
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ repeat: Infinity, duration: 2 }}
        >
          <ArrowDown className="h-6 w-6 text-gray-400" />
        </motion.div>
      </motion.div>
    </section>
  )
}
