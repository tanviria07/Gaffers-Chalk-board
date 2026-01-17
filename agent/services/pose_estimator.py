
import cv2
import numpy as np
import base64
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    logger.warning("[POSE_ESTIMATOR] MediaPipe not installed - install with: pip install mediapipe>=0.10.0")


class PoseEstimator:
    
    
    def __init__(self):
        self.mp_pose = None
        self.pose = None
        self.mp_drawing = None
        self.initialized = False
        self._initialize_model()
    
    def _initialize_model(self):
        
        if not MEDIAPIPE_AVAILABLE:
            logger.warning("[POSE_ESTIMATOR] MediaPipe not available - install with: pip install mediapipe>=0.10.0")
            self.initialized = False
            return
        
        try:

            if hasattr(mp, 'solutions'):
                self.mp_pose = mp.solutions.pose
                self.mp_drawing = mp.solutions.drawing_utils
            else:
                logger.error("[POSE_ESTIMATOR] MediaPipe solutions not available - may need to reinstall: pip install --upgrade mediapipe")
                self.initialized = False
                return
            

            self.pose = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=2,
                enable_segmentation=False,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.initialized = True
            logger.info("[POSE_ESTIMATOR] MediaPipe Pose initialized successfully")
        except Exception as e:
            logger.error(f"[POSE_ESTIMATOR] Failed to initialize MediaPipe: {e}")
            logger.error("[POSE_ESTIMATOR] Try: pip install --upgrade mediapipe")
            import traceback
            traceback.print_exc()
            self.initialized = False
    
    def estimate_pose(self, base64_image: str) -> Dict[str, Any]:
        
        if not self.initialized:
            return self._empty_pose()
        
        try:

            image_bytes = base64.b64decode(base64_image)
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                logger.error("[POSE_ESTIMATOR] Failed to decode image")
                return self._empty_pose()
            

            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            

            try:
                results = self.pose.process(image_rgb)
            except ValueError as e:
                if "Packet timestamp mismatch" in str(e) or "CalculatorGraph" in str(e):

                    logger.warning(f"[POSE_ESTIMATOR] Timestamp error (non-fatal, parallel processing): {e}")
                    return self._empty_pose()
                else:
                    raise
            
            poses_data = {
                'poses': [],
                'actions': [],
                'summary': ''
            }
            
            if results.pose_landmarks:


                pose_landmarks = results.pose_landmarks
                

                keypoints = {}
                for idx, landmark in enumerate(pose_landmarks.landmark):
                    keypoint_name = self.mp_pose.PoseLandmark(idx).name
                    keypoints[keypoint_name] = {
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z,
                        'visibility': landmark.visibility
                    }
                

                action = self._detect_action(keypoints)
                
                pose_data = {
                    'keypoints': keypoints,
                    'action': action,
                    'confidence': 1.0
                }
                
                poses_data['poses'].append(pose_data)
                if action:
                    poses_data['actions'].append(action)
            

            if poses_data['poses']:
                actions_str = ", ".join(poses_data['actions']) if poses_data['actions'] else "standing"
                poses_data['summary'] = f"{len(poses_data['poses'])} person(s) detected, actions: {actions_str}"
            else:
                poses_data['summary'] = "No poses detected"
            
            logger.info(f"[POSE_ESTIMATOR] {poses_data['summary']}")
            return poses_data
            
        except Exception as e:
            logger.error(f"[POSE_ESTIMATOR] Pose estimation error: {e}")
            import traceback
            traceback.print_exc()
            return self._empty_pose()
    
    def _detect_action(self, keypoints: Dict[str, Dict[str, float]]) -> Optional[str]:
        
        try:

            left_foot = keypoints.get('LEFT_ANKLE', {})
            right_foot = keypoints.get('RIGHT_ANKLE', {})
            left_knee = keypoints.get('LEFT_KNEE', {})
            right_knee = keypoints.get('RIGHT_KNEE', {})
            left_hip = keypoints.get('LEFT_HIP', {})
            right_hip = keypoints.get('RIGHT_HIP', {})
            

            if not all(kp.get('visibility', 0) > 0.5 for kp in [left_foot, right_foot, left_knee, right_knee]):
                return None
            

            left_leg_extended = abs(left_foot['y'] - left_knee['y']) > 0.15
            right_leg_extended = abs(right_foot['y'] - right_knee['y']) > 0.15
            

            if left_leg_extended and left_foot['y'] < left_knee['y']:
                return "kicking_left"
            if right_leg_extended and right_foot['y'] < right_knee['y']:
                return "kicking_right"
            

            avg_foot_y = (left_foot['y'] + right_foot['y']) / 2
            avg_hip_y = (left_hip['y'] + right_hip['y']) / 2
            if avg_foot_y < avg_hip_y - 0.1:
                return "jumping"
            

            if abs(left_foot['y'] - right_foot['y']) > 0.05:
                return "running"
            

            return "standing"
            
        except Exception as e:
            logger.error(f"[POSE_ESTIMATOR] Action detection error: {e}")
            return None
    
    def estimate_pose_batch(self, base64_images: List[str]) -> List[Dict[str, Any]]:
        
        if not self.initialized:
            return [self._empty_pose() for _ in base64_images]
        
        results = []
        for base64_image in base64_images:
            pose = self.estimate_pose(base64_image)
            results.append(pose)
        
        return results
    
    def _empty_pose(self) -> Dict[str, Any]:
        
        return {
            'poses': [],
            'actions': [],
            'summary': 'No poses detected'
        }
