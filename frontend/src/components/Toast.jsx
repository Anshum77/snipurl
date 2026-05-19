export function Toast({ kind = "info", children }) {
  return <div className={`toast toast--${kind}`}>{children}</div>;
}

