"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Github, Linkedin, Mail, MapPin, Twitter } from "lucide-react"
import { motion } from "framer-motion"

const contactMethods = [
  {
    icon: Mail,
    label: "邮箱",
    value: "contact@example.com",
    href: "mailto:contact@example.com",
    color: "bg-rose-100 text-rose-600",
  },
  {
    icon: Github,
    label: "GitHub",
    value: "github.com/yourname",
    href: "https://github.com/yourname",
    color: "bg-gray-100 text-gray-700",
  },
  {
    icon: Linkedin,
    label: "LinkedIn",
    value: "linkedin.com/in/yourname",
    href: "https://linkedin.com/in/yourname",
    color: "bg-blue-100 text-blue-600",
  },
  {
    icon: Twitter,
    label: "Twitter",
    value: "@yourname",
    href: "https://twitter.com/yourname",
    color: "bg-sky-100 text-sky-500",
  },
]

export function ContactSection() {
  return (
    <section
      id="contact"
      className="min-h-screen flex items-center justify-center py-20 bg-gray-900 text-white"
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
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">联系我</h2>
          <p className="text-gray-400 max-w-2xl mx-auto">
            无论是有趣的项目合作、技术交流还是其他任何事情，
            <br className="hidden sm:block" />
            都欢迎通过以下方式联系我
          </p>
          <div className="w-20 h-1 bg-gradient-to-r from-purple-500 to-indigo-500 mx-auto rounded-full mt-4" />
        </motion.div>

        {/* 联系卡片 */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto mb-12">
          {contactMethods.map((method, index) => (
            <motion.div
              key={method.label}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <a href={method.href} target="_blank" rel="noopener noreferrer">
                <Card className="bg-gray-800 border-gray-700 hover:bg-gray-750 hover:border-gray-600 transition-all duration-300 group cursor-pointer h-full">
                  <CardContent className="p-6 text-center">
                    <div
                      className={`w-14 h-14 ${method.color} rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform`}
                    >
                      <method.icon className="h-7 w-7" />
                    </div>
                    <h3 className="font-medium text-gray-300 mb-1">
                      {method.label}
                    </h3>
                    <p className="text-sm text-gray-500 group-hover:text-gray-300 transition-colors">
                      {method.value}
                    </p>
                  </CardContent>
                </Card>
              </a>
            </motion.div>
          ))}
        </div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          viewport={{ once: true }}
          className="text-center"
        >
          <p className="text-gray-400 mb-6">
            或者直接发送邮件给我，我会尽快回复
          </p>
          <Button asChild size="lg" className="bg-purple-600 hover:bg-purple-700">
            <a href="mailto:contact@example.com">发送邮件</a>
          </Button>
        </motion.div>

        {/* 位置信息 */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.7 }}
          viewport={{ once: true }}
          className="flex items-center justify-center gap-2 mt-12 text-gray-500"
        >
          <MapPin className="h-4 w-4" />
          <span className="text-sm">中国 · 北京</span>
        </motion.div>
      </div>
    </section>
  )
}
