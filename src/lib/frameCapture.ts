export function getYouTubeThumbnailUrl(videoId: string, timestamp?: number): string {
  return `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`;
}

export async function imageUrlToBase64(imageUrl: string): Promise<string> {
  try {
    const response = await fetch(imageUrl);
    const blob = await response.blob();
    
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = reader.result as string;
        const base64Data = base64.split(',')[1] || base64;
        resolve(base64Data);
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  } catch (error) {
    console.error('Error converting image to base64:', error);
    throw error;
  }
}

export async function captureYouTubeFrame(videoId: string, timestamp: number): Promise<string> {
  try {
    const thumbnailUrl = getYouTubeThumbnailUrl(videoId, timestamp);
    const base64 = await imageUrlToBase64(thumbnailUrl);
    return base64;
  } catch (error) {
    console.error('Error capturing YouTube frame:', error);
    return '';
  }
}

export function createPlaceholderFrame(width: number = 640, height: number = 360): string {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');
  
  if (ctx) {
    const gradient = ctx.createLinearGradient(0, 0, width, height);
    gradient.addColorStop(0, '#1a472a');
    gradient.addColorStop(1, '#0d2818');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);
    
    ctx.fillStyle = '#ffffff';
    ctx.font = '24px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Video Frame', width / 2, height / 2);
  }
  
  return canvas.toDataURL('image/jpeg', 0.8).split(',')[1];
}
