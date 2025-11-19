// SSE connection handler
export const connectToProgressStream = (taskId, onProgress, onComplete, onError) => {
  const eventSource = new EventSource(
    `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/progress/${taskId}`
  );

  eventSource.addEventListener('progress', (event) => {
    try {
      const data = JSON.parse(event.data);
      onProgress(data);

      if (data.state === 'SUCCESS' || data.state === 'FAILURE') {
        eventSource.close();
        if (data.state === 'SUCCESS') {
          onComplete(data);
        } else {
          onError(data);
        }
      }
    } catch (error) {
      console.error('Error parsing SSE data:', error);
      onError(error);
      eventSource.close();
    }
  });

  eventSource.addEventListener('error', (event) => {
    console.error('SSE Error:', event);
    onError(event);
    eventSource.close();
  });

  return eventSource;
};
