"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { getToken } from "@/lib/api";
import { useI18n } from "@/i18n/context";

export default function Home() {
  const router = useRouter();
  const { t } = useI18n();

  useEffect(() => {
    router.replace(getToken() ? "/dashboard" : "/login");
  }, [router]);

  return <div className="container">{t("common.loading")}</div>;
}
