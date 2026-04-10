import type { Metadata } from "next";
import { DM_Sans, Lato } from "next/font/google";
import "./globals.css";
import { Header } from "@/components/layout/Header";
import { MobileHeader } from "@/components/layout/MobileHeader";

const dmSans = DM_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "700", "800"],
  variable: "--font-dm-sans",
  display: "swap",
});

const lato = Lato({
  subsets: ["latin"],
  weight: ["400", "700"],
  variable: "--font-lato",
  display: "swap",
});

export const metadata: Metadata = {
  icons: {
    icon: "/favicon.ico",
    apple: "/apple-touch-icon.png",
  },
  title: "Rushmore — Build Your NBA Mt. Rushmore",
  description:
    "Every NBA fan has an opinion. Build your all-time Top 5, settle the debate, and share it on your socials.",
  openGraph: {
    title: "Rushmore — Build Your NBA Mt. Rushmore",
    description:
      "Every NBA fan has an opinion. Build your all-time Top 5, settle the debate, and share it on your socials.",
    url: "https://rushmore.cards",
    siteName: "Rushmore",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "Rushmore — NBA Top 5 Card Builder",
      },
    ],
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Rushmore — Build Your NBA Mt. Rushmore",
    description:
      "Every NBA fan has an opinion. Build your all-time Top 5, settle the debate, and share it on your socials.",
    images: ["/og-image.png"],
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${dmSans.variable} ${lato.variable}`}>
      <body>
        <div className="flex flex-col overflow-hidden" style={{ height: "100dvh" }}>
          {/* Mobile header (hamburger) */}
          <MobileHeader />
          <Header />
          <main className="flex min-h-0 flex-1 flex-col overflow-y-auto">
            {children}
            <footer className="shrink-0 border-t border-border-subtle px-6 py-3 text-center text-[11px] text-text-tertiary">
              Not affiliated with or endorsed by the NBA. All team logos and player data are property of the NBA.
            </footer>
          </main>
        </div>
      </body>
    </html>
  );
}
