"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { getToken, clearToken } from "@/lib/api";
import { useI18n } from "@/i18n/context";
import LanguageSwitcher from "./LanguageSwitcher";

export default function Nav() {
  const pathname = usePathname();
  const { t } = useI18n();
  const [token, setTokenState] = useState<string | null>(null);

  useEffect(() => {
    setTokenState(getToken());
  }, [pathname]);
  const isAuth = pathname === "/login" || pathname === "/register";

  if (isAuth) return null;

  const links = [
    { href: "/dashboard", label: t("nav.dashboard") },
    { href: "/learn", label: t("nav.learn") },
    { href: "/games", label: t("nav.games") },
    { href: "/profile", label: t("nav.profile") },
  ];

  return (
    <nav className="nav">
      <strong style={{ marginRight: "auto" }}>{t("app.title")}</strong>
      <LanguageSwitcher />
      {token ? (
        <>
          {links.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className={pathname === l.href ? "active" : ""}
            >
              {l.label}
            </Link>
          ))}
          <button
            className="btn btn-secondary"
            style={{ padding: "0.4rem 0.8rem" }}
            onClick={() => {
              clearToken();
              window.location.href = "/login";
            }}
          >
            {t("nav.logout")}
          </button>
        </>
      ) : (
        <Link href="/login">{t("nav.login")}</Link>
      )}
    </nav>
  );
}
