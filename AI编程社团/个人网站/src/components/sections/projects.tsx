"use client"

import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ExternalLink, Github } from "lucide-react"
import { motion } from "framer-motion"
import Image from "next/image"

interface Project {
  id: number
  title: string
  description: string
  tags: string[]
  image: string
  demoUrl?: string
  repoUrl?: string
}

const projects: Project[] = [
  {
    id: 1,
    title: "AI 助手应用",
    description: "基于大语言模型的智能助手，支持多轮对话、代码生成和文档解读。",
    tags: ["React", "TypeScript", "OpenAI API"],
    image: "/pic/projects/project-1.png",
    demoUrl: "#",
    repoUrl: "#",
  },
  {
    id: 2,
    title: "博客系统",
    description: "功能完整的博客平台，支持 Markdown、语法高亮和阅读统计。",
    tags: ["Next.js", "MDX", "Tailwind"],
    demoUrl: "#",
    repoUrl: "#",
    image: "/pic/projects/project-2.svg",
  },
  {
    id: 3,
    title: "电商平台",
    description: "完整的电商解决方案，包含购物车、支付和订单管理功能。",
    tags: ["React", "Node.js", "MongoDB"],
    demoUrl: "#",
    repoUrl: "#",
    image: "/pic/projects/project-3.svg",
  },
]

export function ProjectsSection() {
  return (
    <section
      id="projects"
      className="min-h-screen flex items-center justify-center py-20 bg-gradient-to-br from-gray-50 to-indigo-50"
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
            作品集
          </h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            这里展示了我的一些项目作品，每个项目都经过精心打磨
          </p>
          <div className="w-20 h-1 bg-gradient-to-r from-purple-500 to-indigo-500 mx-auto rounded-full mt-4" />
        </motion.div>

        {/* 项目卡片 */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {projects.map((project, index) => (
            <motion.div
              key={project.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <Card className="h-full overflow-hidden hover:shadow-xl transition-all duration-300 group border-0">
                {/* 项目截图 */}
                <div className="relative h-48 bg-gray-100 overflow-hidden">
                  <Image
                    src={project.image}
                    alt={project.title}
                    fill
                    className="object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                </div>

                <CardContent className="p-5">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {project.title}
                  </h3>
                  <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                    {project.description}
                  </p>
                  {/* 标签 */}
                  <div className="flex flex-wrap gap-2">
                    {project.tags.map((tag) => (
                      <span
                        key={tag}
                        className="px-2.5 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </CardContent>

                <CardFooter className="p-5 pt-0 flex gap-3">
                  {project.demoUrl && (
                    <Button asChild size="sm" variant="default">
                      <a href={project.demoUrl} target="_blank" rel="noopener noreferrer">
                        <ExternalLink className="mr-1.5 h-3.5 w-3.5" />
                        在线演示
                      </a>
                    </Button>
                  )}
                  {project.repoUrl && (
                    <Button asChild size="sm" variant="outline">
                      <a href={project.repoUrl} target="_blank" rel="noopener noreferrer">
                        <Github className="mr-1.5 h-3.5 w-3.5" />
                        源码
                      </a>
                    </Button>
                  )}
                </CardFooter>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
