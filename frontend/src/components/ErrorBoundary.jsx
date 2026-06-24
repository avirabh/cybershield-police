import React from "react";

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error("CyberShield UI error:", error, info);
  }

  render() {
    if (this.state.error) {
      return (
        <div className="fatal-screen">
          <div className="fatal-panel">
            <span className="eyebrow">Frontend Error</span>
            <h1>CyberShield Police could not render</h1>
            <p>{this.state.error.message || "A browser-side error stopped the app from loading."}</p>
            <p>Stop both servers, run the start scripts again, and refresh the browser with Ctrl + F5.</p>
            <button className="button button-primary" type="button" onClick={() => window.location.reload()}>
              Refresh App
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
