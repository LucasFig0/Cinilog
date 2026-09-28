/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                brand: {
                    dark: " #14181c",
                    surface: "#1f252d",
                    card: "#2c3440",
                    border: "#445566",
                    accent: "#00e054",
                    muted: "#9ab",
                },
            },
        },
    },
    plugins: [],
}