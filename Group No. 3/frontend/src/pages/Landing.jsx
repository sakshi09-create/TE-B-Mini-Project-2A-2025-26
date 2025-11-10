import React from "react";
import {
  SignedIn,
  SignedOut,
  SignInButton,
  UserButton,
} from "@clerk/clerk-react";
import Navbar from "../components/navbar";
import { useTheme } from "../context/ThemeContext";
import BlurText from "@/components/Blurtext";
import { useState } from "react";
import { Liquid } from "@/components/liquid-gradient";
import { Star, Github } from "lucide-react";
import { GridBeams } from "@/components/magicui/grid-beams";
import { Button } from "@/components/ui/button";
import { ShimmerButton } from "@/components/magicui/shimmer-button";
import { useUser } from "@clerk/clerk-react";

const COLORS = {
  color1: "#FFFFFF",
  color2: "#1E10C5",
  color3: "#9089E2",
  color4: "#FCFCFE",
  color5: "#F9F9FD",
  color6: "#B2B8E7",
  color7: "#0E2DCB",
  color8: "#0017E9",
  color9: "#4743EF",
  color10: "#7D7BF4",
  color11: "#0B06FC",
  color12: "#C5C1EA",
  color13: "#1403DE",
  color14: "#B6BAF6",
  color15: "#C1BEEB",
  color16: "#290ECB",
  color17: "#3F4CC0",
};

const Landing = () => {
  const { colors, isDark } = useTheme();
  const [isHovered, setIsHovered] = useState(false);
  const { user } = useUser();

  return (
    <div className="min-h-screen">
      <div className="absolute inset-0 -z-10">
        <GridBeams
          gridSize={0}
          gridColor="rgba(255, 255, 255, 0.2)"
          rayCount={20}
          rayOpacity={0.55}
          raySpeed={1.5}
          rayLength="40vh"
          gridFadeStart={5}
          gridFadeEnd={90}
          className="h-full w-full"
        />
      </div>

      {/* Navbar */}
      <Navbar />

      {/* Main Content */}
      <main className="relative overflow-hidden">
        <div className="container mx-auto px-20 w-full">
          {/* Hero Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center min-h-[calc(100vh-4rem)]">
            {/* Left Content */}
            <div className="space-y-8 text-center lg:text-left">
              {/* Heading */}
              <h1
                className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight tracking-tight"
                style={{ color: colors.text.primary }}
              >
                <BlurText
                  text="Secure your"
                  delay={150}
                  animateBy="letter"
                  direction="top"
                  className="text-7xl mb-8"
                />
                <BlurText
                  text="Digital World"
                  delay={150}
                  animateBy="letter"
                  direction="top"
                  className="text-6xl text-[#BDA7FF] mb-8"
                />
              </h1>

              {/* Subtitle */}
              <p
                className="text-lg sm:text-xl max-w-md mx-auto lg:mx-0 leading-relaxed"
                style={{ color: colors.text.secondary }}
              >
                Empower your family with AI-driven security monitoring to stay
                ahead of online threats in real time.
              </p>

              {/* CTA Button */}
              <div className="pt-6">
                <SignedOut>
                  <SignInButton mode="modal">
                    <ShimmerButton className="shadow-2xl">
                      <span className="whitespace-pre-wrap text-center text-sm font-medium leading-none tracking-tight text-white dark:from-white dark:to-slate-900/10 lg:text-lg">
                        Dive In
                      </span>
                    </ShimmerButton>
                  </SignInButton>
                </SignedOut>
                <SignedIn>
                  <div
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "12px",
                      padding: "12px 24px",
                      borderRadius: "50px",
                      border: `2px solid ${colors.border.primary || "#4B5EAA"}`,
                      background: `linear-gradient(135deg, ${colors.bg.secondary || "#2A2F4F"} 0%, ${
                        colors.bg.primary || "#1C2526"
                      } 100%)`,
                      boxShadow: "0 4px 12px rgba(0, 0, 0, 0.2)",
                      transition: "all 0.3s ease-in-out",
                      cursor: "pointer",
                    }}
                    onMouseOver={(e) => {
                      e.currentTarget.style.transform = "translateY(-2px)";
                      e.currentTarget.style.boxShadow = "0 6px 16px rgba(0, 0, 0, 0.3)";
                    }}
                    onMouseOut={(e) => {
                      e.currentTarget.style.transform = "translateY(0)";
                      e.currentTarget.style.boxShadow = "0 4px 12px rgba(0, 0, 0, 0.2)";
                    }}
                    role="button"
                    aria-label="User greeting"
                    tabIndex={0}
                  >
                    <span
                      style={{
                        fontSize: "16px",
                        fontWeight: "500",
                        color: colors.text.primary || "#E0E1DD",
                        letterSpacing: "0.5px",
                        textTransform: "uppercase",
                      }}
                    >
                      Welcome Back
                    </span>
                    <span
                      style={{
                        fontSize: "16px",
                        fontWeight: "600",
                        color: "#F4D35E",
                        background: colors.border.primary || "#4B5EAA",
                        padding: "4px 12px",
                        borderRadius: "16px",
                        transition: "background 0.3s ease",
                      }}
                      onMouseOver={(e) => (e.currentTarget.style.background = "#5D72CC")}
                      onMouseOut={(e) => (e.currentTarget.style.background = colors.border.primary || "#4B5EAA")}
                    >
                      {user?.username || user?.firstName || user?.fullName || "User"}
                    </span>
                  </div>
                </SignedIn>
              </div>
            </div>

            {/* Right Image */}
            <div className="flex justify-center lg:justify-end">
              <div className="relative max-w-md w-full">
                <img
                  src="/welcome2.png"
                  alt="Security Illustration"
                  className="relative min-w-2xl h-auto rounded-2xl right-40 bottom-10"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Background Decorations */}
        <div
          className="absolute bottom-0 left-0 w-96 h-96 rounded-full opacity-10 pointer-events-none"
          style={{
            background: `radial-gradient(circle, ${colors.status.success}, transparent)`,
            transform: "translate(-30%, 30%)",
          }}
        />
      </main>
    </div>
  );
};

export default Landing;