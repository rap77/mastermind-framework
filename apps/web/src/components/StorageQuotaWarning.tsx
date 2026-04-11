import { useMessageStore } from '@/stores/messageStore'

export function StorageQuotaWarning() {
  const localStorageError = useMessageStore((state) => state.localStorageError)
  const clearOldDrafts = useMessageStore((state) => state.clearOldDrafts)

  if (!localStorageError) return null

  return (
    <div className="fixed bottom-4 right-4 max-w-md z-50 bg-yellow-50 border border-yellow-200 rounded-lg p-4 shadow-lg">
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <svg
            className="h-5 w-5 text-yellow-400"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
        </div>
        <div className="ml-3 flex-1">
          <h3 className="text-sm font-medium text-yellow-800">
            Storage Almost Full
          </h3>
          <div className="mt-2 text-sm text-yellow-700">
            <p>
              Drafts are being saved locally only. Some data may be lost if you close this
              tab.
            </p>
          </div>
          <div className="mt-3">
            <button
              type="button"
              onClick={clearOldDrafts}
              className="inline-flex items-center px-3 py-2 border border-yellow-300 text-sm leading-4 font-medium rounded-md text-yellow-700 bg-white hover:bg-yellow-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500"
            >
              Clear Old Drafts
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
