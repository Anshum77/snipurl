import { useState } from "react";
import { Button } from "./Button";

export function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);

  async function onCopy() {
    if (!text) return;
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1200);
    } catch {
      setCopied(false);
    }
  }

  return (
    <Button type="button" variant="secondary" onClick={onCopy} disabled={!text}>
      {copied ? "Copied" : "Copy"}
    </Button>
  );
}

