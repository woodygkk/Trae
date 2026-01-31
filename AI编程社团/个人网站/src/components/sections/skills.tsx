"use client"

import { motion } from "framer-motion"

interface Skill {
  name: string
  level: number // 1-5
  category: string
}

interface SkillCategory {
  name: string
  icon: string
  skills: Skill[]
  color: string
}

const skillCategories: SkillCategory[] = [
  {
    name: "前端",
    icon: "🎨",
    color: "from-blue-500 to-cyan-500",
    skills: [
      { name: "React", level: 5, category: "frontend" },
      { name: "Next.js", level: 5, category: "frontend" },
      { name: "TypeScript", level: 4, category: "frontend" },
      { name: "Vue", level: 4, category: "frontend" },
      { name: "Tailwind CSS", level: 5, category: "frontend" },
    ],
  },
  {
    name: "后端",
    icon: "⚙️",
    color: "from-green-500 to-emerald-500",
    skills: [
      { name: "Node.js", level: 4, category: "backend" },
      { name: "Python", level: 4, category: "backend" },
      { name: "Go", level: 3, category: "backend" },
      { name: "PostgreSQL", level: 4, category: "backend" },
      { name: "MongoDB", level: 3, category: "backend" },
    ],
  },
  {
    name: "工具",
    icon: "🛠️",
    color: "from-orange-500 to-amber-500",
    skills: [
      { name: "Git", level: 5, category: "tools" },
      { name: "Docker", level: 3, category: "tools" },
      { name: "Linux", level: 4, category: "tools" },
      { name: "AWS", level: 3, category: "tools" },
      { name: "Figma", level: 3, category: "tools" },
    ],
  },
]

function SkillBar({ skill, delay }: { skill: Skill; delay: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, width: 0 }}
      whileInView={{ opacity: 1, width: "100%" }}
      transition={{ duration: 0.5, delay }}
      viewport={{ once: true }}
      className="mb-4"
    >
      <div className="flex justify-between items-center mb-1">
        <span className="text-sm font-medium text-gray-700">{skill.name}</span>
        <span className="text-xs text-gray-500">
          {"●".repeat(skill.level)}{"○".repeat(5 - skill.level)}
        </span>
      </div>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          whileInView={{ width: `${(skill.level / 5) * 100}%` }}
          transition={{ duration: 0.8, delay: delay + 0.2 }}
          viewport={{ once: true }}
          className="h-full bg-gradient-to-r from-purple-500 to-indigo-500 rounded-full"
        />
      </div>
    </motion.div>
  )
}

export function SkillsSection() {
  return (
    <section
      id="skills"
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
            技能栈
          </h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            技术是我改变世界的武器，以下是我掌握的主要技能
          </p>
          <div className="w-20 h-1 bg-gradient-to-r from-purple-500 to-indigo-500 mx-auto rounded-full mt-4" />
        </motion.div>

        {/* 技能卡片 */}
        <div className="grid md:grid-cols-3 gap-8">
          {skillCategories.map((category, categoryIndex) => (
            <motion.div
              key={category.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: categoryIndex * 0.1 }}
              viewport={{ once: true }}
              className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-2xl p-6"
            >
              {/* 分类标题 */}
              <div className="flex items-center gap-3 mb-6">
                <span className="text-2xl">{category.icon}</span>
                <h3 className="text-xl font-semibold text-gray-900">
                  {category.name}
                </h3>
              </div>

              {/* 技能列表 */}
              <div>
                {category.skills.map((skill, skillIndex) => (
                  <SkillBar
                    key={skill.name}
                    skill={skill}
                    delay={categoryIndex * 0.1 + skillIndex * 0.05}
                  />
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
