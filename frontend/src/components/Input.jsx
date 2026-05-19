export function Input({ label, hint, ...props }) {
  return (
    <label className="field">
      <div className="field__label">{label}</div>
      <input className="input" {...props} />
      {hint ? <div className="field__hint">{hint}</div> : null}
    </label>
  );
}

