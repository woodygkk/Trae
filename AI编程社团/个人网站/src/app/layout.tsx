import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AI编程社团 - 个人作品集",
  description: "全栈开发者 | AI爱好者 | 创作者",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN" className="scroll-smooth">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
