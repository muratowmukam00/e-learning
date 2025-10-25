<<<<<<< HEAD
# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
=======
# Play - Free Tailwind CSS Template for Startup, Apps and SaaS

Play is an open-source and free Tailwind CSS template co-created by TailGrids and UIdeck. This template specially crafted for SaaS, startup, business and software website.
Play crafted in a way that you can use with almost all sort of web project. This is Tailwind CSS template built using [TailGrids](https://tailgrids.com/) components.

### This template crafted using 🥞 [TailGrids](https://tailgrids.com/) UI components

### [🚀 View Demo](https://play-tailwind.tailgrids.com/)

### [⬇️ Download Now](https://links.tailgrids.com/play-download)

[![play-tailwind](https://cdn.tailgrids.com/play-tailwind.jpg)](https://play-tailwind.tailgrids.com/)

## 📃 License

Play is an open-source template, you can use it with your personal or commercial projects without any attribution or backlink.

## 💙 Support

You can always support this project by [Starring🌟 This Repository](https://github.com/tailgrids/play-tailwind)
and sharing with friends. Also open an issue if you find bug or feel free to contribute by pull requests after fixing any issue or adding more values.

### Update Logs: 2.0 - Nov 2023
- Design refresh
- New marketing section
- Dark mode support
- Code and performance optimization
- Updated dependencies
>>>>>>> 8ec01fd (fixed index.html & deleted front & then created again without tailwindcss)
