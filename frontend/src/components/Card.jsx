export function Card({ title, subtitle, children, right }) {
  return (
    <section className="card">
      <header className="card__header">
        <div>
          <h2 className="card__title">{title}</h2>
          {subtitle ? <p className="card__subtitle">{subtitle}</p> : null}
        </div>
        {right ? <div className="card__right">{right}</div> : null}
      </header>
      <div className="card__body">{children}</div>
    </section>
  );
}

