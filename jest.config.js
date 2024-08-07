module.exports = {
    preset: 'ts-jest',
    testEnvironment: 'jsdom',
    moduleNameMapper: {
      '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    },
    testMatch: ['<rootDir>/src/tests/**/*.(test|spec).(ts|tsx|js|jsx)'],
    testSequencer: './src/tests/alphabeticalSequencer.js',
    setupFiles: ['./src/tests/mocks/localStorageMock.js']
  };