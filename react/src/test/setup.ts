// Runs before each test file. See "test.setupFiles" in vite.config.ts.
import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach, vi } from 'vitest'

afterEach(() => {
  // Unmount React trees and undo vi.stubGlobal() between tests.
  cleanup()
  vi.unstubAllGlobals()
})
