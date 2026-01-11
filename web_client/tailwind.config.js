/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                voca: {
                    bg: '#131313',
                    sidebar: '#272727',
                    text: '#CCCCCC',
                    border: '#CCCCCC',
                    red: '#FF4444', // Accent for recording
                    cyan: '#00E5FF', // Accent for AI
                }
            },
            fontFamily: {
                serif: ['Playfair Display', 'serif'],
                sans: ['Inter', 'sans-serif'],
            }
        },
    },
    plugins: [],
}
