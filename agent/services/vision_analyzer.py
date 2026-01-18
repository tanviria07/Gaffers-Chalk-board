
import anthropic
import os
import httpx
import base64
import asyncio
from typing import Optional, Dict, Any, List
from utils.image_processor import compress_image
from services.object_detector import ObjectDetector
from services.pose_estimator import PoseEstimator


class VisionAnalyzer:
    
    
    def __init__(self, api_key: Optional[str] = None, use_enhanced: bool = True):

        self.azure_key = os.getenv("AZURE_OPENAI_KEY")
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

        self.azure_deployment = os.getenv("AZURE_OPENAI_VISION_DEPLOYMENT", "gpt-4o-mini")
        self.azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-07-01-preview")
        

        self.anthropic_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
        self.azure_client = None
        self.claude_client = None
        self.provider = None
        

        self.use_enhanced = use_enhanced
        self.object_detector = None
        self.pose_estimator = None
        
        if self.use_enhanced:
            try:
                self.object_detector = ObjectDetector()
                print(f"[VISION] Object Detector (YOLOv8): {'✓ Initialized' if self.object_detector.initialized else '✗ Failed'}")
            except Exception as e:
                print(f"[VISION] Warning: Could not initialize Object Detector: {e}")
            
            try:
                self.pose_estimator = PoseEstimator()
                print(f"[VISION] Pose Estimator (MediaPipe): {'✓ Initialized' if self.pose_estimator.initialized else '✗ Failed'}")
            except Exception as e:
                print(f"[VISION] Warning: Could not initialize Pose Estimator: {e}")
        

        if self.azure_key and self.azure_endpoint:
            try:
                if not self.azure_endpoint.endswith('/'):
                    self.azure_endpoint += '/'
                self.azure_vision_endpoint = f"{self.azure_endpoint}openai/deployments/{self.azure_deployment}/chat/completions?api-version={self.azure_api_version}"
                self.azure_client = httpx.AsyncClient(timeout=30.0)
                self.provider = "azure"
                print(f"[VISION] Initialized Azure OpenAI Vision: {self.azure_vision_endpoint}")
            except Exception as e:
                print(f"[VISION] Warning: Could not initialize Azure OpenAI Vision: {e}")
        

        if not self.azure_client and self.anthropic_key:
            try:
                self.claude_client = anthropic.Anthropic(api_key=self.anthropic_key)
                self.provider = "anthropic"
                print(f"[VISION] Initialized Anthropic Claude Vision (fallback)")
            except Exception as e:
                print(f"[VISION] Warning: Could not initialize Anthropic client: {e}")
        
        if not self.azure_client and not self.claude_client:
            print(f"[VISION] No vision AI provider available - will use stub responses")
    
    async def analyze(self, base64_image: str, context: Optional[str] = None) -> str:
        
        return await self.analyze_frame(base64_image, context)
    
    async def analyze_frame(self, base64_image: str, context: Optional[str] = None) -> str:
        

        if self.use_enhanced and (self.object_detector or self.pose_estimator):
            return await self._analyze_enhanced(base64_image, context)
        

        if self.azure_client:
            return await self._analyze_with_azure(base64_image, context)
        
        if self.claude_client:
            return await self._analyze_with_claude(base64_image, context)
        
        return self._generate_stub_commentary()
    
    async def _analyze_enhanced(self, base64_image: str, context: Optional[str] = None) -> str:
        
        try:

            detection_task = None
            pose_task = None
            
            if self.object_detector and self.object_detector.initialized:
                loop = asyncio.get_event_loop()
                detection_task = loop.run_in_executor(
                    None, 
                    self.object_detector.detect_objects, 
                    base64_image
                )
            
            if self.pose_estimator and self.pose_estimator.initialized:
                loop = asyncio.get_event_loop()
                pose_task = loop.run_in_executor(
                    None,
                    self.pose_estimator.estimate_pose,
                    base64_image
                )
            

            detection_result = None
            pose_result = None
            
            if detection_task:
                detection_result = await detection_task
            if pose_task:
                pose_result = await pose_task
            

            enhanced_context = self._build_enhanced_context(
                detection_result, 
                pose_result, 
                context
            )
            

            if self.azure_client:
                return await self._analyze_with_azure(base64_image, enhanced_context)
            elif self.claude_client:
                return await self._analyze_with_claude(base64_image, enhanced_context)
            else:

                return self._generate_commentary_from_detections(detection_result, pose_result)
                
        except Exception as e:
            print(f"[VISION] ✗ Enhanced analysis error: {e}")
            import traceback
            traceback.print_exc()

            if self.azure_client:
                return await self._analyze_with_azure(base64_image, context)
            elif self.claude_client:
                return await self._analyze_with_claude(base64_image, context)
            return self._generate_stub_commentary()
    
    def _build_enhanced_context(self, detection_result: Optional[Dict], pose_result: Optional[Dict], original_context: Optional[str]) -> str:
        
        context_parts = []
        
        if original_context:
            context_parts.append(f"VIDEO CONTEXT: {original_context}")
        
        if detection_result:
            context_parts.append("\n=== OBJECT DETECTION (YOLOv8) ===")
            context_parts.append(f"Detected: {detection_result.get('summary', 'No objects')}")
            
            players = detection_result.get('players', [])
            if players:
                context_parts.append(f"\nPlayers detected: {len(players)}")
                for i, player in enumerate(players[:5]):
                    bbox = player.get('bbox', {})
                    conf = player.get('confidence', 0)
                    context_parts.append(f"  Player {i+1}: center=({bbox.get('center_x', 0):.0f}, {bbox.get('center_y', 0):.0f}), confidence={conf:.2f}")
            
            ball = detection_result.get('ball')
            if ball:
                bbox = ball.get('bbox', {})
                conf = ball.get('confidence', 0)
                context_parts.append(f"\nBall detected: center=({bbox.get('center_x', 0):.0f}, {bbox.get('center_y', 0):.0f}), confidence={conf:.2f}")
                

                possession = self.object_detector.find_ball_possession(detection_result)
                if possession:
                    context_parts.append(f"Ball possession: Player {possession['player_id']+1} (distance: {possession['distance']:.0f}px)")
        
        if pose_result:
            context_parts.append("\n=== POSE ESTIMATION (MediaPipe) ===")
            poses = pose_result.get('poses', [])
            actions = pose_result.get('actions', [])
            if poses:
                context_parts.append(f"Poses detected: {len(poses)}")
                for i, pose in enumerate(poses):
                    action = pose.get('action', 'unknown')
                    context_parts.append(f"  Person {i+1}: action={action}")
            if actions:
                context_parts.append(f"Actions detected: {', '.join(actions)}")
        
        context_parts.append("\n=== INSTRUCTIONS ===")
        context_parts.append("You have EXACT object detection and pose estimation data above.")
        context_parts.append("Use this data to give a PRECISE, ACCURATE description of what's happening.")
        context_parts.append("Be specific about player positions, ball location, and actions.")
        context_parts.append("If object detection found a ball and players, describe their exact positions.")
        context_parts.append("If pose estimation detected actions (kicking, jumping, running), describe them.")
        
        return "\n".join(context_parts)
    
    def _generate_commentary_from_detections(self, detection_result: Optional[Dict], pose_result: Optional[Dict]) -> str:
        
        parts = []
        
        if detection_result:
            summary = detection_result.get('summary', '')
            if summary:
                parts.append(f"Object detection: {summary}")
        
        if pose_result:
            summary = pose_result.get('summary', '')
            if summary:
                parts.append(f"Pose analysis: {summary}")
        
        if parts:
            return ". ".join(parts) + "."
        
        return self._generate_stub_commentary()
    
    async def _analyze_with_azure(self, base64_image: str, context: Optional[str] = None) -> str:
        
        try:


            compressed = compress_image(base64_image, max_size=1024, quality=85)
            
            prompt = "Analyze this soccer frame. Describe the key action happening: player positions, ball location, and what's occurring. Be concise, under 20 words."
            
            if context:
                prompt = f"CONTEXT: {context}\n\n{prompt}"
            

            max_retries = 2
            retry_delay = 3.0
            
            for attempt in range(max_retries):
                try:
                    response = await self.azure_client.post(
                        self.azure_vision_endpoint,
                        headers={
                            "api-key": self.azure_key,
                            "Content-Type": "application/json"
                        },
                        json={
                            "messages": [
                                {
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": prompt
                                        },
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/jpeg;base64,{compressed}"
                                            }
                                        }
                                    ]
                                }
                            ],
                            "temperature": 0.7,
                            "max_tokens": 300
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        commentary = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                        print(f"[VISION] ✓ Azure Vision analysis: {commentary[:60]}...")
                        return commentary
                    elif response.status_code == 429:

                        if attempt < max_retries - 1:
                            error_data = response.json() if response.text else {}
                            retry_after = error_data.get('error', {}).get('message', '')
                            

                            import re
                            retry_match = re.search(r'retry after (\d+) seconds?', retry_after.lower())
                            if retry_match:

                                retry_delay = float(retry_match.group(1)) + 3
                            else:

                                retry_delay = retry_delay * 5
                            
                            print(f"[VISION] Rate limit (429) - waiting {retry_delay:.1f}s before retry (attempt {attempt + 1}/{max_retries})...")
                            await asyncio.sleep(retry_delay)
                            continue
                        else:
                            print(f"[VISION] ✗ Azure Vision API rate limit - max retries reached")
                            return self._generate_stub_commentary()
                    else:
                        print(f"[VISION] ✗ Azure Vision API error: {response.status_code} - {response.text}")
                        return self._generate_stub_commentary()
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"[VISION] Request error (attempt {attempt + 1}/{max_retries}): {e}")
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        raise
            
        except Exception as e:
            print(f"[VISION] ✗ Azure Vision analysis error: {e}")
            import traceback
            traceback.print_exc()
            return self._generate_stub_commentary()
    
    async def _analyze_with_claude(self, base64_image: str, context: Optional[str] = None) -> str:
        
        try:
            compressed = compress_image(base64_image, max_size=384, quality=50)
            
            prompt = "Analyze this soccer frame. Describe the key action happening: player positions, ball location, and what's occurring. Be concise, under 20 words."
            
            if context:
                prompt = f"CONTEXT: {context}\n\n{prompt}"
            
            message = self.claude_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": compressed
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }]
            )
            
            commentary = message.content[0].text.strip()
            print(f"[VISION] ✓ Claude Vision analysis: {commentary[:60]}...")
            return commentary
            
        except Exception as e:
            print(f"[VISION] ✗ Claude Vision analysis error: {e}")
            return self._generate_stub_commentary()
    
    async def extract_positions(self, base64_image: str) -> Dict[str, Any]:
        


        return {
            "attackers": [[0.7, 0.5], [0.6, 0.3], [0.65, 0.4]],
            "defenders": [[0.3, 0.5], [0.2, 0.7], [0.25, 0.6]],
            "ball": [0.65, 0.45],
            "diagramType": "defensive"
        }
    
    def _generate_stub_commentary(self) -> str:
        
        import random
        stubs = [
            "Players are moving into position, creating space for a potential attack.",
            "The team is building up play from the back, looking for passing options.",
            "A counter-attack is developing with players sprinting forward.",
            "Defensive shape is compact, denying space in the central areas.",
            "The ball is in the final third, with attackers looking for an opening."
        ]
        return random.choice(stubs)
