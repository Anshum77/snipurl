export function KeyValue({ label, value, mono = false }) {
  return (
    <div className="kv">
      <div className="kv__label">{label}</div>
      <div className={`kv__value ${mono ? "kv__value--mono" : ""}`}>{value}</div>
    </div>
  );
}

