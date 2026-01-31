import { Github, Linkedin, Mail, Twitter } from "lucide-react"
import Link from "next/link"

export function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-400 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          {/* 版权信息 */}
          <div className="text-sm">
            &copy; {new Date().getFullYear()} AI编程社团. All rights reserved.
          </div>

          {/* 社交链接 */}
          <div className="flex items-center gap-4">
            <Link
              href="https://github.com/yourname"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-white transition-colors"
            >
              <Github className="h-5 w-5" />
              <span className="sr-only">GitHub</span>
            </Link>
            <Link
              href="https://linkedin.com/in/yourname"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-white transition-colors"
            >
              <Linkedin className="h-5 w-5" />
              <span className="sr-only">LinkedIn</span>
            </Link>
            <Link
              href="https://twitter.com/yourname"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-white transition-colors"
            >
              <Twitter className="h-5 w-5" />
              <span className="sr-only">Twitter</span>
            </Link>
            <Link
              href="mailto:contact@example.com"
              className="hover:text-white transition-colors"
            >
              <Mail className="h-5 w-5" />
              <span className="sr-only">Email</span>
            </Link>
          </div>
        </div>

        {/* 备案信息 */}
        <div className="text-center text-xs mt-4 text-gray-600">
          <a
            href="https://beian.miit.gov.cn/"
            target="_blank"
            rel="noopener noreferrer"
          >
            粤ICP备XXXXXXXX号
          </a>
        </div>
      </div>
    </footer>
  )
}
