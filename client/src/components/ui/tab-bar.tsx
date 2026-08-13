"use client";

import { useId } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";

export interface TabItem {
  value: string;
  label: string;
}

interface TabBarProps {
  tabs: TabItem[];
  activeTab: string;
  onTabChange: (value: string) => void;
  className?: string;
}

export function TabBar({ tabs, activeTab, onTabChange, className }: TabBarProps) {
  const layoutId = useId();

  return (
    <div className={`flex gap-1 rounded-lg border p-1 ${className ?? ""}`}>
      {tabs.map((tab) => (
        <Button
          key={tab.value}
          variant="ghost"
          size="sm"
          onClick={() => onTabChange(tab.value)}
          className="relative flex-1 rounded-md"
        >
          {activeTab === tab.value && (
            <motion.div
              layoutId={layoutId}
              className="absolute inset-0 rounded-md bg-primary"
              transition={{ type: "spring", bounce: 0.2, duration: 0.5 }}
            />
          )}
          <span
            className={`relative z-10 ${
              activeTab === tab.value ? "text-primary-foreground" : ""
            }`}
          >
            {tab.label}
          </span>
        </Button>
      ))}
    </div>
  );
}
