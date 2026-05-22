import type { Metadata } from "next";
import "./globals.css";
import Nav from "@/components/Nav";
import { I18nProvider } from "@/i18n/context";

export const metadata: Metadata = {
  title: "VocabFusion",
  description: "Context-aware root-semantic vocabulary learning",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body>
        <I18nProvider>
          <Nav />
          <main>{children}</main>
        </I18nProvider>
      </body>
    </html>
  );
}
