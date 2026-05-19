import { ShortenCard } from "./features/ShortenCard";
import { StatsCard } from "./features/StatsCard";
import "./styles.css";

export default function App() {
  return (
    <div className="page">
      <header className="top">
        <div>
          <h1 className="top__title">SnipURL</h1>
        </div>
      </header>

      <main className="layout">
        <ShortenCard />
        <StatsCard />
      </main>
    </div>
  );
}
