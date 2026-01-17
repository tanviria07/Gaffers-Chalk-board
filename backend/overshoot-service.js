import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { RealtimeVision } from '@overshoot/sdk';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const envPath = join(__dirname, '..', 'agent', '.env');
console.log(`[OVERSHOOT] Loading .env from: ${envPath}`);
const result = dotenv.config({ path: envPath });
if (result.error) {
  console.warn(`[OVERSHOOT] Error loading .env: ${result.error.message}`);
} else {
  console.log(`[OVERSHOOT] .env loaded successfully`);
}

const app = express();
const PORT = process.env.OVERSHOOT_SERVICE_PORT || 3002;

app.use(cors());
app.use(express.json());

const API_URL = 'https://cluster1.overshoot.ai/api/v0.2';
const API_KEY = process.env.OVERSHOOT_API_KEY;

const activeVisions = new Map();

app.post('/get-frame-window', async (req, res) => {
  try {
    const { videoUrl, currentTime, windowSize = 5.0 } = req.body;

    if (!videoUrl) {
      return res.status(400).json({
        success: false,
        error: 'videoUrl is required'
      });
    }

    if (!API_KEY) {
      return res.status(503).json({
        success: false,
        error: 'OVERSHOOT_API_KEY not set in environment'
      });
    }

    console.log(`[OVERSHOOT] Getting frames for ${videoUrl} at ${currentTime}s`);

    const requestId = `${videoUrl}_${Date.now()}`;
    
    const results = [];
    let visionInstance = null;

    try {
      visionInstance = new RealtimeVision({
        apiUrl: API_URL,
        apiKey: API_KEY,
        prompt: 'You are a soccer commentator. Describe the key action happening in this video window. Use soccer vocabulary. Keep it under 15 words. Do not mention NFL.',
        source: { 
          type: 'url',
          url: videoUrl 
        },
        onResult: (result) => {
          results.push({
            text: result.result,
            timestamp: result.timestamp || currentTime,
            confidence: result.confidence
          });
          console.log(`[OVERSHOOT] Result: ${result.result?.substring(0, 50)}...`);
        }
      });

      await visionInstance.start();
      
      await new Promise(resolve => setTimeout(resolve, Math.min(windowSize * 1000, 5000)));
      
      await visionInstance.stop();

      if (results.length > 0) {
        const latestResult = results[results.length - 1];
        
        return res.json({
          success: true,
          commentary: latestResult.text,
          rawAction: latestResult.text,
          timestamp: latestResult.timestamp || currentTime,
          allResults: results.map(r => r.text)
        });
      } else {
        return res.json({
          success: false,
          error: 'No results from Overshoot',
          message: 'Overshoot processed but returned no results'
        });
      }

    } catch (overshootError) {
      console.error('[OVERSHOOT] Error:', overshootError);
      
      if (visionInstance) {
        try {
          await visionInstance.stop();
        } catch (e) {
        }
      }

      if (overshootError.message?.includes('source') || overshootError.message?.includes('url')) {
        return res.status(400).json({
          success: false,
          error: 'Invalid video source format',
          details: overshootError.message,
          hint: 'Overshoot might need different source format for YouTube URLs'
        });
      }

      return res.status(500).json({
        success: false,
        error: 'Overshoot processing failed',
        details: overshootError.message
      });
    }

  } catch (error) {
    console.error('[OVERSHOOT] Service error:', error);
    return res.status(500).json({
      success: false,
      error: 'Internal server error',
      details: error.message
    });
  }
});

app.post('/start-stream', async (req, res) => {
  try {
    const { videoUrl, prompt } = req.body;

    if (!videoUrl || !API_KEY) {
      return res.status(400).json({
        success: false,
        error: 'videoUrl and API_KEY required'
      });
    }

    const streamId = `stream_${Date.now()}`;
    
    const vision = new RealtimeVision({
      apiUrl: API_URL,
      apiKey: API_KEY,
      prompt: prompt || 'Describe what you see in soccer terms',
      source: { type: 'url', url: videoUrl },
      onResult: (result) => {
        if (!activeVisions.has(streamId)) {
          activeVisions.set(streamId, []);
        }
        activeVisions.get(streamId).push(result);
      }
    });

    await vision.start();
    activeVisions.set(streamId, { vision, results: [] });

    res.json({
      success: true,
      streamId,
      message: 'Stream started'
    });

  } catch (error) {
    return res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'overshoot-service',
    has_api_key: !!API_KEY,
    api_url: API_URL
  });
});

app.listen(PORT, () => {
  console.log(`Overshoot Service: http://localhost:${PORT}`);
  console.log(`API Key: ${API_KEY ? 'Set ✓' : 'Not set ✗'}`);
  if (API_KEY) {
    console.log(`API Key (first 10 chars): ${API_KEY.substring(0, 10)}...`);
  }
  console.log(`API URL: ${API_URL}`);
  console.log(`Environment: OVERSHOOT_API_KEY=${process.env.OVERSHOOT_API_KEY ? 'SET' : 'NOT SET'}`);
});
