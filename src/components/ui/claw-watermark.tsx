import * as React from "react";

export function ClawWatermark({ className }: { className?: string }) {
  return (
    <svg aria-hidden viewBox="0 0 400 400" className={className} fill="none">
      <g transform="rotate(-18 200 200)" opacity="0.5">
        <rect x="60" y="0" width="26" height="400" rx="13" fill="url(#clawGrad)" />
        <rect x="140" y="-20" width="26" height="400" rx="13" fill="url(#clawGrad)" />
        <rect x="220" y="10" width="26" height="400" rx="13" fill="url(#clawGrad)" />
      </g>
      <defs>
        <linearGradient id="clawGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#D4AF37" stopOpacity="0" />
          <stop offset="50%" stopColor="#D4AF37" stopOpacity="0.5" />
          <stop offset="100%" stopColor="#D4AF37" stopOpacity="0" />
        </linearGradient>
      </defs>
    </svg>
  );
}

export default ClawWatermark;
