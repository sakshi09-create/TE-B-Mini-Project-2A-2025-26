// src/components/navbar.jsx
import React, { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  Github,
  Linkedin,
  Twitter,
  Menu,
  X,
  Shield,
  Home,
  Info,
  Mail,
  Settings,
} from "lucide-react";
import { useTheme } from "../context/ThemeContext";
import ThemeToggle from "./ThemeToggle";
import {
  SignedIn,
  SignedOut,
  SignInButton,
  UserButton,
} from "@clerk/clerk-react";

export default function Navbar() {
  const { colors, isDark } = useTheme();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const location = useLocation();

  // Handle scroll effect
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 0);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Close mobile menu when route changes
  useEffect(() => {
    setIsMenuOpen(false);
  }, [location]);

  const navItems = [
    { name: "Dashboard", path: "/dashboard", icon: Home },
  ];
  

  const socialLinks = [
    { icon: Github, href: "https://github.com", label: "GitHub" },
    { icon: Twitter, href: "https://twitter.com", label: "Twitter" },
    { icon: Linkedin, href: "https://linkedin.com", label: "LinkedIn" },
  ];

  return (
    <header
      className={`w-full mt-4 sticky top-0 z-50 transition-all duration-300 `}
      style={{
        borderColor: isScrolled ? colors.border.primary : "transparent",
        backgroundColor: isScrolled ? undefined : "transparent",
      }}
    >
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link
            to="/"
            className="flex items-center space-x-2 text-xl font-bold hover:opacity-80 transition-all duration-200 group"
            style={{ color: colors.text.primary }}
          >
            <img src="/shield.png" className="w-6 h-6 group-hover:rotate-12 transition-transform duration-200" />
            <span>ParentShield AI</span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8"></nav>

          {/* Right Section */}
          <div className="flex items-center space-x-3">
            {/* Social Links - Desktop */}
            <div className="hidden lg:flex items-center space-x-2">
              {/* Separator */}
            </div>

            {/* Auth Section */}
            <div className="flex items-center space-x-2">
              <SignedOut>
                {/* <SignInButton mode="modal">
                  <button
                    className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 hover:scale-105 ${
                      isDark
                        ? "bg-blue-600 hover:bg-blue-700 text-white"
                        : "bg-blue-500 hover:bg-blue-600 text-white"
                    }`}
                  >
                    Sign In
                  </button>
                </SignInButton> */}
              </SignedOut>

              <SignedIn>
                <div className="flex items-center space-x-2">
                  {navItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = location.pathname === item.path;

                    return (
                      <Link
                        key={item.name}
                        to={item.path}
                        className={`flex items-center space-x-1 px-3 py-2 rounded-lg transition-all duration-200 hover:scale-105 ${
                          isActive
                            ? `font-semibold ${
                                isDark
                                  ? "bg-blue-900/30 text-blue-400"
                                  : "bg-blue-100 text-blue-600"
                              }`
                            : "hover:bg-opacity-10 hover:bg-gray-500"
                        }`}
                        style={{
                          color: isActive ? undefined : colors.text.secondary,
                        }}
                      >
                        <Icon className="w-4 h-4" />
                        <span>{item.name}</span>
                      </Link>
                    );
                  })}
                  <div
                    className="w-px h-6 mx-3"
                    style={{ backgroundColor: colors.border.primary }}
                  />
                  <UserButton
                    appearance={{
                      elements: {
                        avatarBox:
                          "w-8 h-8 hover:scale-110 transition-transform duration-200",
                      },
                    }}
                  />
                </div>
              </SignedIn>
            </div>

            {/* Theme Toggle */}
            {/* <ThemeToggle /> */}

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden p-2 rounded-lg hover:bg-opacity-10 hover:bg-gray-500 transition-all duration-200"
              style={{ color: colors.text.primary }}
              aria-label="Toggle menu"
            >
              {isMenuOpen ? (
                <X className="w-5 h-5" />
              ) : (
                <Menu className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div
            className="md:hidden border-t mt-2 pt-4 pb-6 animate-in slide-in-from-top-5 duration-200"
            style={{ borderColor: colors.border.primary }}
          >
            <nav className="flex flex-col space-y-2">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;

                return (
                  <Link
                    key={item.name}
                    to={item.path}
                    className={`flex items-center space-x-2 px-4 py-3 rounded-lg transition-all duration-200 ${
                      isActive
                        ? `font-semibold ${
                            isDark
                              ? "bg-blue-900/30 text-blue-400"
                              : "bg-blue-100 text-blue-600"
                          }`
                        : "hover:bg-opacity-10 hover:bg-gray-500"
                    }`}
                    style={{
                      color: isActive ? undefined : colors.text.secondary,
                    }}
                  >
                    <Icon className="w-5 h-5" />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
            </nav>

            {/* Mobile Social Links */}
            <div
              className="flex items-center justify-center space-x-4 mt-6 pt-4 border-t"
              style={{ borderColor: colors.border.primary }}
            >
              {socialLinks.map((social) => {
                const Icon = social.icon;
                return (
                  <a
                    key={social.label}
                    href={social.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 rounded-full hover:bg-opacity-10 hover:bg-gray-500 transition-all duration-200"
                    style={{ color: colors.text.secondary }}
                    aria-label={social.label}
                  >
                    <Icon className="w-5 h-5" />
                  </a>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
