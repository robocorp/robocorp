import { useMutation } from '@tanstack/react-query';

export type ActionRunPayload = {
  actionPackageName: string;
  actionName: string;
  args: object;
  apiKey?: string;
};

export const useActionRunMutation = () => {
  return useMutation({
    mutationFn: async ({ actionPackageName, args, actionName, apiKey }: ActionRunPayload) => {
      const request = await fetch(`/api/actions/${actionPackageName}/${actionName}/run`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${apiKey}`,
        },
        body: JSON.stringify(args),
      });

      const runId = request.headers.get('X-Action-Server-Run-Id') || '';
      let response = '';

      try {
        const json = await request.json();
        response = JSON.stringify(json, null, 2);
      } catch {
        response = await request.text();
      }

      return {
        runId,
        response,
      };
    },
  });
};
