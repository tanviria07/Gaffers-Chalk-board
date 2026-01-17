
import cv2
import numpy as np
import base64
from typing import List, Dict, Any, Optional
import logging
from ultralytics import YOLO

logger = logging.getLogger(__name__)


class ObjectDetector:
    
    
    def __init__(self):
        self.model = None
        self.initialized = False
        self._initialize_model()
    
    def _initialize_model(self):
        
        try:


            self.model = YOLO('yolov8n.pt')

            self.initialized = True
            logger.info("[OBJECT_DETECTOR] YOLOv8 initialized successfully")
        except Exception as e:
            logger.error(f"[OBJECT_DETECTOR] Failed to initialize YOLOv8: {e}")
            self.initialized = False
    
    def detect_objects(self, base64_image: str, confidence_threshold: float = 0.25) -> Dict[str, Any]:
        
        if not self.initialized:
            return self._empty_detection()
        
        try:

            image_bytes = base64.b64decode(base64_image)
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                logger.error("[OBJECT_DETECTOR] Failed to decode image")
                return self._empty_detection()
            

            try:
                results = self.model(image, conf=confidence_threshold, verbose=False)
            except AttributeError as e:
                if "'Conv' object has no attribute 'bn'" in str(e):

                    logger.warning(f"[OBJECT_DETECTOR] Model compatibility error (YOLOv8 will be skipped): {e}")
                    return self._empty_detection()
                else:
                    logger.error(f"[OBJECT_DETECTOR] Detection error: {e}")
                    return self._empty_detection()
            except Exception as e:
                logger.error(f"[OBJECT_DETECTOR] Detection error: {e}")
                return self._empty_detection()
            

            detections = {
                'players': [],
                'ball': None,
                'goals': [],
                'other_objects': [],
                'summary': ''
            }
            
            if len(results) > 0 and results[0].boxes is not None:
                boxes = results[0].boxes
                
                for box in boxes:

                    class_id = int(box.cls[0])
                    class_name = self.model.names[class_id]
                    confidence = float(box.conf[0])
                    

                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    center_x = (x1 + x2) / 2
                    center_y = (y1 + y2) / 2
                    width = x2 - x1
                    height = y2 - y1
                    
                    detection = {
                        'class': class_name,
                        'confidence': confidence,
                        'bbox': {
                            'x1': float(x1),
                            'y1': float(y1),
                            'x2': float(x2),
                            'y2': float(y2),
                            'center_x': float(center_x),
                            'center_y': float(center_y),
                            'width': float(width),
                            'height': float(height)
                        }
                    }
                    

                    if class_name == 'person':
                        detections['players'].append(detection)
                    elif class_name == 'sports ball':

                        if detections['ball'] is None or confidence > detections['ball']['confidence']:
                            detections['ball'] = detection
                    elif class_name in ['sports ball', 'ball']:
                        if detections['ball'] is None or confidence > detections['ball']['confidence']:
                            detections['ball'] = detection
                    else:
                        detections['other_objects'].append(detection)
            

            summary_parts = []
            if detections['players']:
                summary_parts.append(f"{len(detections['players'])} player(s)")
            if detections['ball']:
                ball_conf = detections['ball']['confidence']
                ball_x = detections['ball']['bbox']['center_x']
                ball_y = detections['ball']['bbox']['center_y']
                summary_parts.append(f"ball at ({ball_x:.0f}, {ball_y:.0f}) [conf: {ball_conf:.2f}]")
            if detections['other_objects']:
                summary_parts.append(f"{len(detections['other_objects'])} other object(s)")
            
            detections['summary'] = ", ".join(summary_parts) if summary_parts else "No objects detected"
            
            logger.info(f"[OBJECT_DETECTOR] Detected: {detections['summary']}")
            return detections
            
        except Exception as e:
            logger.error(f"[OBJECT_DETECTOR] Detection error: {e}")
            import traceback
            traceback.print_exc()
            return self._empty_detection()
    
    def detect_objects_batch(self, base64_images: List[str], confidence_threshold: float = 0.25) -> List[Dict[str, Any]]:
        
        if not self.initialized:
            return [self._empty_detection() for _ in base64_images]
        
        results = []
        for base64_image in base64_images:
            detection = self.detect_objects(base64_image, confidence_threshold)
            results.append(detection)
        
        return results
    
    def find_ball_possession(self, detections: Dict[str, Any], max_distance: float = 100.0) -> Optional[Dict[str, Any]]:
        
        if not detections['ball'] or not detections['players']:
            return None
        
        ball_center = (
            detections['ball']['bbox']['center_x'],
            detections['ball']['bbox']['center_y']
        )
        
        closest_player = None
        min_distance = float('inf')
        
        for i, player in enumerate(detections['players']):
            player_center = (
                player['bbox']['center_x'],
                player['bbox']['center_y']
            )
            

            distance = np.sqrt(
                (ball_center[0] - player_center[0]) ** 2 +
                (ball_center[1] - player_center[1]) ** 2
            )
            
            if distance < min_distance:
                min_distance = distance
                closest_player = {
                    'player_id': i,
                    'distance': distance,
                    'player_bbox': player['bbox']
                }
        
        if closest_player and closest_player['distance'] <= max_distance:
            return closest_player
        
        return None
    
    def _empty_detection(self) -> Dict[str, Any]:
        
        return {
            'players': [],
            'ball': None,
            'goals': [],
            'other_objects': [],
            'summary': 'No objects detected'
        }
