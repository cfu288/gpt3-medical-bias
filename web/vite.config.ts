import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  if (mode === "development") {
    return {
      plugins: [react()],
    };
  } else {
    return {
      plugins: [react()],
      base: "/gpt3-medical-bias/",
    };
  }
});
