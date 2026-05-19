import { useMemo, useState } from "react";
import { getStats } from "../lib/api";
import { getShortCodeFromInput, formatDateTime } from "../lib/format";
import { Card } from "../components/Card";
import { Input } from "../components/Input";
import { Button } from "../components/Button";
import { Toast } from "../components/Toast";
import { KeyValue } from "../components/KeyValue";

function Buckets({ title, buckets }) {
  if (!buckets?.length) return null;
  return (
    <div className="bucket">
      <div className="bucket__title">{title}</div>
      <div className="bucket__list">
        {buckets.map((b) => (
          <div key={b.label} className="bucket__item">
            <span className="bucket__label">{b.label}</span>
            <span className="bucket__count">{b.count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function StatsCard() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [stats, setStats] = useState(null);

  const shortCode = useMemo(() => getShortCodeFromInput(input), [input]);

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setStats(null);
    setLoading(true);
    try {
      const data = await getStats(shortCode);
      setStats(data);
    } catch (err) {
      setError(err?.message || "Failed to fetch stats");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card title="URL Stats" subtitle="Fetch analytics for a short code.">
      <form className="stack" onSubmit={onSubmit}>
        <Input
          label="Short code (or full short URL)"
          placeholder="portfolio  —  or  http://localhost:8000/portfolio"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          required
        />

        <div className="row">
          <Button type="submit" disabled={loading || !shortCode}>
            {loading ? "Loading..." : "Get Stats"}
          </Button>
          <div className="muted">{shortCode ? `Using: ${shortCode}` : " "}</div>
        </div>

        {error ? <Toast kind="error">{error}</Toast> : null}

        {stats ? (
          <div className="stack">
            <div className="result">
              <KeyValue label="Original URL" value={stats.original_url} mono />
              <KeyValue label="Short URL" value={stats.short_url} mono />
              <KeyValue label="Total clicks" value={String(stats.total_clicks)} />
              <KeyValue label="Created at" value={formatDateTime(stats.created_at)} />
              <KeyValue label="Expires at" value={formatDateTime(stats.expires_at)} />
            </div>

            {stats.analytics ? (
              <div className="grid2">
                <Buckets title="Top referrers" buckets={stats.analytics.top_referrers} />
                <Buckets title="Countries" buckets={stats.analytics.clicks_by_country} />
                <Buckets title="Browsers" buckets={stats.analytics.clicks_by_browser} />
                <Buckets title="Operating systems" buckets={stats.analytics.clicks_by_os} />
                <Buckets title="Devices" buckets={stats.analytics.clicks_by_device} />
              </div>
            ) : null}

            {stats.recent_clicks?.length ? (
              <div className="table">
                <div className="table__title">Recent clicks</div>
                <div className="table__head">
                  <div>Time</div>
                  <div>IP</div>
                  <div className="hide-sm">Referrer</div>
                  <div className="hide-sm">User-Agent</div>
                </div>
                {stats.recent_clicks.map((c, idx) => (
                  <div key={idx} className="table__row">
                    <div>{formatDateTime(c.clicked_at)}</div>
                    <div>{c.ip_address || "—"}</div>
                    <div className="hide-sm truncate">{c.referrer || "direct"}</div>
                    <div className="hide-sm truncate">{c.user_agent || "—"}</div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="muted">No recent click events yet.</div>
            )}
          </div>
        ) : null}
      </form>
    </Card>
  );
}

