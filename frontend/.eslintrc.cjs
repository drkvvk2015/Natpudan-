module.exports = {
  root: true,
  ignorePatterns: ['dist', 'src/pages/OAuthCallback_old.tsx', 'src/components/ImageViewer.tsx', 'src/pages/RegisterPage.tsx'],
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint', 'react-hooks', 'react-refresh'],
  extends: [
    'eslint:recommended',
    'plugin:react-hooks/recommended',
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  rules: {
    'no-inline-styles': 'off',
    'react/no-inline-styles': 'off',
    'jsx-a11y/no-invalid-aria-role': 'off',
    'jsx-a11y/aria-role': 'off',
    'no-unused-vars': 'off',
    '@typescript-eslint/no-unused-vars': 'off',
    'react-hooks/exhaustive-deps': 'off',
    'react-refresh/only-export-components': 'off',
  },
  overrides: [
    {
      files: ['src/**/*.{ts,tsx}'],
      rules: {
        'no-undef': 'off',
      },
    },
    {
      files: ['src/pages/RegisterPage.tsx', 'src/components/ImageViewer.tsx'],
      rules: {
        'jsx-a11y/no-invalid-aria-role': 'off',
        'jsx-a11y/aria-role': 'off',
        'no-inline-styles': 'off',
      },
    },
  ],
};
