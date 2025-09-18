import { useAppBridge } from '@shopify/app-bridge-react';
import { useMemo } from 'react';

export function useAuthenticatedFetch() {
  const app = useAppBridge();

  return useMemo(() => {
    return async (uri, options = {}) => {
      const response = await fetch(uri, {
        ...options,
        headers: {
          ...options.headers,
          'Authorization': `Bearer ${app.sessionToken}`,
        },
      });

      return response;
    };
  }, [app.sessionToken]);
}
