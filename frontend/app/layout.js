import "./globals.css";

export const metadata = {
  title: "ClipMind AI",
  description: "AI-powered video learning platform"
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}