import { FC } from 'react';
import { useLoaderData } from 'react-router-dom';
import { baseUrl } from '~/lib/requestData';

export async function actionRunLogLoader(args: any) {
  const params = args.params;
  return { id: params.id };
}

export const ActionRunLog: FC<{}> = () => {
  const data = useLoaderData() as any;
  const runId = data.id;

  // const [loadedArtifacts, setLoadedActions] = useState<LoadedArtifacts>({
  //   isPending: true,
  //   data: [],
  //   errorMessage: undefined,
  // });
  //
  // Commented code would be a path forward to doing on-the-fly updates
  // of what's happening in the server or work on crashed cases where
  // the log.html is not produced (left as future work for now).
  // const iframeRef = useRef<HTMLIFrameElement>(null);
  // useEffect(() => {
  //   console.log('mount');
  //   // Check if the iframe reference exists
  //   if (iframeRef && iframeRef.current) {
  //     // Access the contentWindow and execute JavaScript code inside the iframe
  //     const iframeWindow = iframeRef.current.contentWindow;
  //     if (iframeWindow) {
  //       // Example: Execute a simple alert inside the iframe
  //       iframeWindow.setContents({
  //         "initialContents": '',
  //       });
  //     }
  //   }
  //   return () => {
  //     // Your code here
  //     console.log('unmount');
  //   };
  // }, []);
  //
  //   console.log('request artifacts for run', runId);
  //   collectRunArtifacts(runId, loadedArtifacts, setLoadedActions, {
  //     artifact_name_regexp: '.*\\.robolog',
  //   });
  //
  // return <iframe src={`${baseUrl}/base_log.html`} id="logIframe" ref={iframeRef} />;

  return <iframe src={`${baseUrl}/api/runs/${runId}/log.html`} id="logIframe" />;
};
