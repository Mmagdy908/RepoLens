import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RepoLens",
  description: "AI-powered repository analysis and architecture insights",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="font-sans antialiased" suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
