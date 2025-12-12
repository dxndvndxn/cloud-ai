import { toaster } from '@snack-uikit/toaster';

export interface HttpProps {
  api: string;
  method?: 'GET' | 'POST';
  body?: any;
  isFile?: boolean;
}

export const http = async <T>({ api, body, method = 'GET', isFile }: HttpProps) => {
  try {
    const uri = `http://${import.meta.env.VITE_APP_API || 'http://localhost:8000'}/api/v1/${api}`;

    const response: Response = await fetch(uri, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    let json;

    if (isFile) {
      json = await response.blob();
    } else {
      json = await response.json();
    }

    if (response.status === 422 || response.status === 500 || response.status === 400) {
      if (json?.detail || json?.message) {
        return await toaster.systemEvent.error({
          title: 'Error',
          description: json?.detail || json?.message,
        });
      }

      throw new Error(json?.detail || json);
    }

    return json as T;
  } catch (e) {
    await toaster.systemEvent.error({
      title: 'Error',
      description: e?.toString(),
    });

    return Promise.reject(e);
  }
};
