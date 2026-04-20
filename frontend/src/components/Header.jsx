function Header() {
  return (
    <header className="header">
      <div className="header-container">
        <div className="logo">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
          </svg>
          <span className="logo-text">DocuMind</span>
        </div>
        <div className="header-actions">
          <span className="version-badge">v1.0</span>
        </div>
      </div>
    </header>
  );
}

export default Header;