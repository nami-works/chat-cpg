import { createApp } from "@shopify/app-bridge";
import { Provider } from "@shopify/app-bridge-react";
import { AppProvider } from "@shopify/polaris";
import "@shopify/polaris/build/esm/styles.css";
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { translations } from "./locales";

// Initialize App Bridge
const app = createApp({
  apiKey: process.env.SHOPIFY_API_KEY,
  host: new URLSearchParams(location.search).get("host"),
  forceRedirect: true,
});

function AppWrapper() {
  return (
    <Provider config={app}>
      <AppProvider i18n={translations}>
        <App />
      </AppProvider>
    </Provider>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<AppWrapper />);
