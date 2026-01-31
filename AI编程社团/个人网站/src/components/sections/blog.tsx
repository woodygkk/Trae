"use client"

import { Card, CardContent } from "@/components/ui/card"
import { motion } from "framer-motion"
import { Calendar, Clock, ArrowRight } from "lucide-react"
import Link from "next/link"

interface BlogPost {
  slug: string
  title: string
  excerpt: string
  date: string
  readTime: string
  category: string
}

const blogPosts: BlogPost[] = [
  {
    slug: "how-to-build-ai-web-app",
    title: "如何构建AI驱动的Web应用",
    excerpt: "本文将介绍如何利用大语言模型API构建一个智能问答应用，从环境搭建到部署上线的完整流程。",
    date: "2024-01-13",
    readTime: "15min",
    category: "编程",
  },
  {
    slug: "tech-stack-philosophy",
    title: "我的技术栈选择哲学",
    excerpt: "为什么我选择 React + TypeScript + Next.js 作为主要技术栈？这篇文章分享我的思考过程。",
    date: "2024-01-10",
    readTime: "8min",
    category: "随笔",
  },
  {
    slug: "react-server-components",
    title: "React Server Components 详解",
    excerpt: "深入理解 React Server Components 的工作原理，以及它如何改变我们构建应用的方式。",
    date: "2024-01-05",
    readTime: "12min",
    category: "技术",
  },
]

export function BlogSection() {
  return (
    <section
      id="blog"
      className="min-h-screen flex items-center justify-center py-20 bg-gradient-to-br from-indigo-50 via-white to-purple-50"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 标题 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            博客
          </h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            分享技术心得和实践经验，期待与大家一起成长
          </p>
          <div className="w-20 h-1 bg-gradient-to-r from-purple-500 to-indigo-500 mx-auto rounded-full mt-4" />
        </motion.div>

        {/* 博客文章列表 */}
        <div className="max-w-4xl mx-auto space-y-4">
          {blogPosts.map((post, index) => (
            <motion.div
              key={post.slug}
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <Link href={`/blog/${post.slug}`}>
                <Card className="hover:shadow-lg transition-all duration-300 group cursor-pointer border-0">
                  <CardContent className="p-6">
                    <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-6">
                      {/* 日期信息 */}
                      <div className="flex items-center gap-4 text-sm text-gray-500 sm:w-40">
                        <span className="flex items-center gap-1">
                          <Calendar className="h-4 w-4" />
                          {post.date}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="h-4 w-4" />
                          {post.readTime}
                        </span>
                      </div>

                      {/* 文章内容 */}
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">
                            {post.category}
                          </span>
                        </div>
                        <h3 className="text-lg font-semibold text-gray-900 group-hover:text-purple-600 transition-colors">
                          {post.title}
                        </h3>
                        <p className="text-gray-600 text-sm mt-1 line-clamp-1">
                          {post.excerpt}
                        </p>
                      </div>

                      {/* 箭头 */}
                      <div className="hidden sm:block">
                        <ArrowRight className="h-5 w-5 text-gray-300 group-hover:text-purple-600 group-hover:translate-x-1 transition-all" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            </motion.div>
          ))}
        </div>

        {/* 查看更多 */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          viewport={{ once: true }}
          className="text-center mt-10"
        >
          <Link
            href="/blog"
            className="inline-flex items-center gap-2 text-purple-600 hover:text-purple-700 font-medium transition-colors"
          >
            查看所有文章
            <ArrowRight className="h-4 w-4" />
          </Link>
        </motion.div>
      </div>
    </section>
  )
}
