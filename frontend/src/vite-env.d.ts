/// <reference types="vite/client" />

// Augment known environment variables for better IntelliSense
interface ImportMetaEnv {
  readonly VITE_API_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}