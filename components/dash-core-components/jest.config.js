module.exports = {
    preset: 'ts-jest',
    testEnvironment: 'jsdom',
    roots: ['<rootDir>/tests'],
    testMatch: ['**/__tests__/**/*.{ts,tsx}', '**/?(*.)+(spec|test).{ts,tsx}'],
    transform: {
        '^.+\\.(ts|tsx)$': [
            'ts-jest',
            {
                tsconfig: {
                    jsx: 'react',
                    esModuleInterop: true,
                    allowSyntheticDefaultImports: true,
                    types: ['jest', '@testing-library/jest-dom'],
                },
            },
        ],
        '^.+\\.js$': [
            'ts-jest',
            {
                tsconfig: {
                    allowJs: true,
                },
            },
        ],
    },
    collectCoverageFrom: ['src/**/*.{ts,tsx}', '!src/**/*.d.ts'],
    moduleNameMapper: {
        '^@/(.*)$': '<rootDir>/src/$1',
        '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    },
    setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
    // Disable caching to ensure TypeScript type changes are always picked up
    cache: false,
    // Limit workers in CI to prevent out-of-memory errors
    maxWorkers: 2,
};
