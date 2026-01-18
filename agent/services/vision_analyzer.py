
import google.generativeai as genai
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
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        self.model = None
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
        

        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest")
                self.model = genai.GenerativeModel(model_name)
                self.provider = "gemini"
                print(f"[VISION] Initialized Gemini Vision")
            except Exception as e:
                print(f"[VISION] Warning: Could not initialize Gemini: {e}")
                self.model = None
        
        if not self.model:
            print(f"[VISION] No vision AI provider available - will use stub responses")
    
    async def analyze(self, base64_image: str, context: Optional[str] = None) -> str:
        
        return await self.analyze_frame(base64_image, context)
    
    async def analyze_frame(self, base64_image: str, context: Optional[str] = None) -> str:
        

        if self.use_enhanced and (self.object_detector or self.pose_estimator):
            return await self._analyze_enhanced(base64_image, context)
        
        if self.model:
            return await self._analyze_with_gemini(base64_image, context)
        
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
            

            if self.model:
                return await self._analyze_with_gemini(base64_image, enhanced_context)
            else:

                return self._generate_commentary_from_detections(detection_result, pose_result)
                
        except Exception as e:
            print(f"[VISION] ✗ Enhanced analysis error: {e}")
            import traceback
            traceback.print_exc()

            if self.model:
                return await self._analyze_with_gemini(base64_image, context)
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
    
    async def _analyze_with_gemini(self, base64_image: str, context: Optional[str] = None) -> str:
        
        try:
            compressed = compress_image(base64_image, max_size=384, quality=50)
            
            prompt = "Analyze this soccer frame. Describe the key action happening: player positions, ball location, and what's occurring. Be concise, under 20 words."
            
            if context:
                prompt = f"CONTEXT: {context}\n\n{prompt}"
            
            from PIL import Image
            import io
            
            image_data = base64.b64decode(compressed)
            image = Image.open(io.BytesIO(image_data))
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content([prompt, image])
            )
            
            commentary = response.text.strip()
            print(f"[VISION] ✓ Gemini Vision analysis: {commentary[:60]}...")
            return commentary
            
        except Exception as e:
            print(f"[VISION] ✗ Gemini Vision analysis error: {e}")
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
