// Jest setup file
// This file is loaded before every test file
import '@testing-library/jest-dom';

// Mock window.dash_component_api for components that use Dash context
global.window = global.window || {};
global.window.dash_component_api = {
    useDashContext: () => ({
        useLoading: () => false,
    }),
};