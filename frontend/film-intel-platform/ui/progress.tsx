"use client";

import * as React from "react";
import * as ProgressPrimitive from "@radix-ui/react-progress";
import { tv } from "tailwind-variants";

const progress = tv({
  base: "relative overflow-hidden bg-gray-200 rounded-full w-full",
  variants: {
    size: {
      default: "h-2",
      sm: "h-1",
      lg: "h-3",
    },
  },
  defaultVariants: {
    size: "default",
  },
});

interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value: number;
}

export function Progress({ className, value, ...props }: ProgressProps) {
  return (
    <ProgressPrimitive.Root
      className={progress({ className })}
      value={value}
      {...props}
    >
      <ProgressPrimitive.Indicator
        className="bg-blue-600 h-full transition-all"
        style={{ transform: `translateX(-${100 - value}%)` }}
      />
    </ProgressPrimitive.Root>
  );
}
