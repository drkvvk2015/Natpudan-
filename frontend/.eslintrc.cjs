module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    'eslint:recommended',
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
    'no-unused-vars': 'warn',
  },
  overrides: [
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
