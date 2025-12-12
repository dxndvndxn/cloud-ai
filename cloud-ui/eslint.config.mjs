import baseConfig from '@cloud-ru/eslint-config';

export default [
  ...baseConfig,
  {
    rules: {
      '@typescript-eslint/no-namespace': 'off',
      'prettier/prettier': 'off',
    },
  },
  {
    files: [
      'lint-staged.config.mjs',
      'stylelint.config.cjs',
      'vitest.config.ts',
      'vite.config.ts',
      'prettier.config.cjs',
    ],
    rules: {
      'import/no-default-export': 'off',
      '@typescript-eslint/no-var-requires': 'off',
    },
  },
];
