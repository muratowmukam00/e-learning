// src/theme.ts

export const getDesignTokens = (mode: "light" | "dark") => ({
    palette: {
        mode,
        ...(mode === "light"
            ? {
                // Light Mode
                primary: { main: "#f44336" }, // gyzyl
                background: { default: "#f0f0f0", paper: "#ffffff" },
                text: { primary: "#000000", secondary: "#555555" },
            }
            : {
                // Dark Mode
                primary: { main: "#f44336" },
                background: { default: "#121212", paper: "#1e1e1e" },
                text: { primary: "#ffffff", secondary: "#cccccc" },
            }),
    },
    typography: {
        fontFamily: "'Roboto', sans-serif",
        h1: {
            fontSize: "2.5rem",
            fontWeight: 700,
        },
        body1: {
            fontSize: "1rem",
        },
    },
});
