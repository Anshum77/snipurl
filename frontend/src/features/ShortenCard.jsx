import { useState } from "react";
import { shortenUrl } from "../lib/api";
import { Card } from "../components/Card";
import { Input } from "../components/Input";
import { Button } from "../components/Button";
import { CopyButton } from "../components/CopyButton";
import { Toast } from "../components/Toast";
import { KeyValue } from "../components/KeyValue";

export function ShortenCard() {
  const [url, setUrl] = useState("");
  const [customAlias, setCustomAlias] = useState("");
  const [expiresInDays, setExpiresInDays] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setResult(null);
    setLoading(true);
    try {
      const data = await shortenUrl({ url, customAlias, expiresInDays });
      setResult(data);
    } catch (err) {
      setError(err?.message || "Failed to shorten URL");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card
      title="Shorten URL"
      subtitle="Create a short link with an optional custom alias."
      right={result?.short_url ? <CopyButton text={result.short_url} /> : null}
    >
      <form className="stack" onSubmit={onSubmit}>
        <Input
          label="Long URL"
          placeholder="https://example.com/some/long/path"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          required
        />

        <div className="grid2">
          <Input
            label="Custom alias (optional)"
            placeholder="portfolio"
            value={customAlias}
            onChange={(e) => setCustomAlias(e.target.value)}
          />
          <Input
            label="Expires in days (optional)"
            placeholder="7"
            inputMode="numeric"
            value={expiresInDays}
            onChange={(e) => setExpiresInDays(e.target.value)}
          />
        </div>

        <div className="row">
          <Button type="submit" disabled={loading}>
            {loading ? "Shortening..." : "Shorten URL"}
          </Button>
          <div className="muted">
            {loading ? "Talking to API..." : " "}
          </div>
        </div>

        {error ? <Toast kind="error">{error}</Toast> : null}

        {result ? (
          <div className="result">
            <KeyValue label="Short URL" value={result.short_url} mono />
            <KeyValue label="Short code" value={result.short_code} mono />
            <KeyValue label="Original URL" value={result.original_url} mono />
            <KeyValue label="Expires at" value={result.expires_at || "—"} mono />
          </div>
        ) : null}
      </form>
    </Card>
  );
}

