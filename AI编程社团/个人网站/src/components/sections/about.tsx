"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Lightbulb, Target, Sparkles } from "lucide-react"
import { motion } from "framer-motion"

const aboutItems = [
  {
    icon: Target,
    title: "使命",
    description: "用技术创造价值，用产品改变世界",
    color: "text-blue-600",
    bg: "bg-blue-100",
  },
  {
    icon: Lightbulb,
    title: "经历",
    description: "3年+全栈开发经验，专注于Web和AI应用",
    color: "text-amber-600",
    bg: "bg-amber-100",
  },
  {
    icon: Sparkles,
    title: "理念",
    description: "相信技术应该服务于人，让世界更美好",
    color: "text-purple-600",
    bg: "bg-purple-100",
  },
]

export function AboutSection() {
  return (
    <section
      id="about"
      className="min-h-screen flex items-center justify-center py-20 bg-white"
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
            关于我
          </h2>
          <div className="w-20 h-1 bg-gradient-to-r from-purple-500 to-indigo-500 mx-auto rounded-full" />
        </motion.div>

        {/* 内容卡片 */}
        <div className="grid md:grid-cols-3 gap-8">
          {aboutItems.map((item, index) => (
            <motion.div
              key={item.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <Card className="h-full hover:shadow-lg transition-shadow duration-300 border-0 shadow-md">
                <CardContent className="p-6 text-center">
                  <div
                    className={`w-16 h-16 ${item.bg} rounded-2xl flex items-center justify-center mx-auto mb-4`}
                  >
                    <item.icon className={`h-8 w-8 ${item.color}`} />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {item.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed">
                    {item.description}
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* 详细介绍 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          viewport={{ once: true }}
          className="mt-16 max-w-4xl mx-auto"
        >
          <Card className="border-0 shadow-md">
            <CardContent className="p-8">
              <p className="text-gray-600 leading-loose text-lg">
                我是一个热爱探索的开发者，专注于全栈开发和人工智能应用。
                相信技术可以改变世界，致力于用产品思维解决实际问题。
                空闲时喜欢写技术博客，分享学习心得和经验。
              </p>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </section>
  )
}
