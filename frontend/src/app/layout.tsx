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
}) {  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        {/*
         * Inline script runs synchronously before first paint — reads
         * localStorage and applies `class="dark"` with zero flash.
         * Falls back to dark when no preference is stored.
         */}
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var t=localStorage.getItem('theme');if(t!=='light')document.documentElement.classList.add('dark');}catch(e){}})();`,
          }}
        />
      </head>
      <body className="font-sans antialiased" suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
