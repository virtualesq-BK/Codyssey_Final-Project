import type { ReactNode } from "react";

export const metadata = {
  title: "AI 비지니스 의사결정 Copilot",
  description: "여러 전문 AI Agent가 사업 아이디어를 분석합니다.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
