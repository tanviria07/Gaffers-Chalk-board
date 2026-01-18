
import os
import httpx
import re
import asyncio
from typing import Optional, Dict, Any


class ChatService:
    
    
    def __init__(self):
        self.api_key = os.getenv("AZURE_OPENAI_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-07-01-preview")
        

        if self.endpoint and not self.endpoint.endswith('/'):
            self.endpoint += '/'
        self.chat_endpoint = f"{self.endpoint}openai/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"
        
        self.client = None
        if self.api_key and self.endpoint:
            self.client = httpx.AsyncClient(timeout=30.0)
            print(f"[CHAT] Azure OpenAI initialized: endpoint={self.endpoint}, deployment={self.deployment}")
        else:
            print(f"[CHAT] Azure OpenAI NOT initialized - missing credentials")
            print(f"[CHAT] Debug: api_key={'SET' if self.api_key else 'NOT SET'}, endpoint={'SET' if self.endpoint else 'NOT SET'}")
    
    def _is_available(self) -> bool:
        
        return self.client is not None and self.api_key is not None and self.endpoint is not None
    
    def _parse_timestamp_from_message(self, message: str) -> Optional[float]:
        
        import re
        message_lower = message.lower()
        

        time_pattern = r'(\d{1,2}):(\d{2})(?::(\d{2}))?'
        match = re.search(time_pattern, message)
        if match:
            hours = 0
            minutes = int(match.group(1))
            seconds = int(match.group(2))

            if match.group(3) is not None:
                hours = minutes
                minutes = seconds
                seconds = int(match.group(3))
            timestamp = hours * 3600 + minutes * 60 + seconds
            print(f"[CHAT] Parsed timestamp from MM:SS format: {minutes}:{seconds:02d} = {timestamp}s")
            return timestamp
        

        decimal_pattern = r'(\d{1,2})\.(\d{2})\b'
        match = re.search(decimal_pattern, message)
        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            if seconds < 60:
                timestamp = minutes * 60 + seconds
                print(f"[CHAT] Parsed timestamp from MM.SS format: {minutes}.{seconds:02d} = {timestamp}s")
                return timestamp
        


        minute_second_patterns = [
            r'(\d+)\s*(?:minute|min)\s+(?:and\s+)?(\d+)\s*(?:second|sec|s)',
            r'(\d+)\s*(?:minute|min)\s+(\d+)',
        ]
        for pattern in minute_second_patterns:
            match = re.search(pattern, message_lower)
            if match:
                minutes = int(match.group(1))
                seconds = int(match.group(2))
                if seconds < 60:
                    timestamp = minutes * 60 + seconds
                    print(f"[CHAT] Parsed timestamp from 'minute second' format: {minutes} minute {seconds} second = {timestamp}s")
                    return timestamp
        



        if 'minute' not in message_lower and 'min' not in message_lower:
            sec_patterns = [

                r'explain\s+(\d+)\s*(?:second|sec|s)\b',

                r'(?:at|in|what\s+happened\s+in|what\s+happened\s+at|what\s+happens?\s+in|what\s+happens?\s+at|what|whats|what\'s)\s+(\d+)\s*(?:second|sec|s)\b',

                r'(\d+)\s*(?:second|sec|s)\b',
            ]
            
            for pattern in sec_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    timestamp = float(match.group(1))
                    print(f"[CHAT] Parsed timestamp from seconds format: {timestamp}s (pattern matched: {pattern[:30]}...)")
                    return timestamp
        


        if len(message.split()) <= 5:
            num_pattern = r'^(\d+)(?:\s|$)'
            match = re.search(num_pattern, message)
            if match:
                num = int(match.group(1))


                if num < 600 and ':' not in message and '.' not in message:
                    print(f"[CHAT] Parsed timestamp from number: {num}s")
                    return float(num)
        
        print(f"[CHAT] Could not parse timestamp from message: '{message}'")
        return None
    
    async def chat(
        self,
        user_message: str,
        video_id: str,
        current_time: float,
        context: Optional[Dict[str, Any]] = None,
        video_metadata: Optional[Dict[str, Any]] = None,
        caption_extractor=None,
        frame_extractor=None,
        vision_analyzer=None
    ) -> str:
        
        if not self._is_available():
            print(f"[CHAT] Azure OpenAI not available - using stub response")
            print(f"[CHAT] Debug: api_key={'SET' if self.api_key else 'NOT SET'}, endpoint={'SET' if self.endpoint else 'NOT SET'}, client={'SET' if self.client else 'NOT SET'}")
            return self._generate_stub_response(user_message, current_time, context)
        
        print(f"[CHAT] Calling Azure OpenAI at {self.chat_endpoint}")
        
        system_prompt = "You are a knowledgeable soccer analyst helping users understand soccer tactics and plays in videos. Provide clear, concise explanations using soccer terminology. If asked about NFL analogies, use American football comparisons. Be helpful and specific about what's happening in the video."

        video_title = video_metadata.get('title', '') if video_metadata else ''
        video_description = video_metadata.get('description', '') if video_metadata else ''
        
        minutes = int(current_time // 60)
        seconds = int(current_time % 60)
        timestamp_str = f"{minutes}:{seconds:02d}"
        
        user_prompt = f"USER QUESTION: {user_message}\n\nCURRENT VIDEO TIME: {timestamp_str}\n\n"
        

        if video_metadata:
            user_prompt += f"VIDEO INFORMATION:\n"
            user_prompt += f"Title: {video_title}\n"
            if video_description:
                user_prompt += f"Description: {video_description[:300]}...\n"
            user_prompt += f"\n"
        

        is_generic_context = False
        if context:
            commentary = context.get('commentary', '')
            nfl_analogy = context.get('nflAnalogy', '')
            

            generic_phrases = [
                'soccer action at',
                'well-designed offensive scheme',
                'every player has a role',
                'players are moving into position',
                'the team is building up play',
                'counter-attack is developing',
                'defensive shape is compact',
                'ball is in the final third'
            ]
            
            is_generic_context = any(phrase.lower() in commentary.lower() or phrase.lower() in nfl_analogy.lower() 
                                    for phrase in generic_phrases)
            
            if context.get('commentary'):
                if is_generic_context:
                    user_prompt += f"NOTE: The analysis below is generic/placeholder. The video shows a soccer match at {timestamp_str}. "
                    user_prompt += f"Use your knowledge of soccer to answer specifically about what's happening. "
                    user_prompt += f"Generic analysis (ignore if too vague): {context['commentary']}\n\n"
                else:
                    user_prompt += f"CURRENT PLAY ANALYSIS: {context['commentary']}\n\n"
            
            if context.get('nflAnalogy') and not is_generic_context:
                user_prompt += f"NFL ANALOGY: {context['nflAnalogy']}\n\n"
        

        asked_timestamp = self._parse_timestamp_from_message(user_message)
        is_asking_about_now = any(phrase in user_message.lower() for phrase in [
            'now', 'current', 'happening now', 'what\'s happening', 'whats happening',
            'what happened now', 'whats happening now', 'what is happening now', 'what happens now'
        ])
        




        if asked_timestamp is not None:

            target_timestamp = asked_timestamp
            print(f"[CHAT] User specified timestamp: {target_timestamp}s")
        elif is_asking_about_now:

            if current_time > 0:

                target_timestamp = current_time
                print(f"[CHAT] User asked 'now' - video is playing at {target_timestamp}s")
            else:

                return "Please play the video first, then ask 'what's happening now' or 'what happened now' while the video is playing."
        else:

            if current_time > 0:
                target_timestamp = current_time
                print(f"[CHAT] No timestamp specified, using current playback time: {target_timestamp}s")
            else:

                return "Please specify a timestamp (e.g., 'what happened at 23 seconds' or 'explain 1:27') or play the video and ask 'what's happening now'."
        

        minutes = int(target_timestamp // 60)
        seconds = int(target_timestamp % 60)
        timestamp_str = f"{minutes}:{seconds:02d}"
        


        window_start = max(0, target_timestamp - 5)
        window_end = target_timestamp + 5
        print(f"[CHAT] CAPTIONS-ONLY MODE: Using fast window {window_start}s - {window_end}s (skipping vision and audio for speed)")
        
        captions_in_window = []
        

        if caption_extractor:
            try:
                captions_in_window = await caption_extractor.get_captions_in_range(video_id, window_start, window_end)
                if captions_in_window:
                    print(f"[CHAT] ✓ Found {len(captions_in_window)} captions in {window_end - window_start}s window")
                else:
                    print(f"[CHAT] No captions available - will answer based on video metadata and context")
            except Exception as e:
                print(f"[CHAT] Could not fetch captions in range: {e} - will answer based on video metadata and context")
        



        visual_analysis = None
        audio_transcript = None
        


        if False and frame_extractor and vision_analyzer:
            try:
                target_min = int(target_timestamp // 60)
                target_sec = int(target_timestamp % 60)
                target_str = f"{target_min}:{target_sec:02d}"
                
                start_min = int(window_start // 60)
                start_sec = int(window_start % 60)
                end_min = int(window_end // 60)
                end_sec = int(window_end % 60)
                window_str = f"{start_min}:{start_sec:02d} - {end_min}:{end_sec:02d}"
                
                print(f"[CHAT] Analyzing optimized window around {target_str} ({window_str})...")
                



                frame_times = [
                    max(0, target_timestamp - 2),
                    max(0, target_timestamp - 1),
                    target_timestamp,
                    target_timestamp + 1,
                    target_timestamp + 2,
                    target_timestamp + 3,
                    target_timestamp + 4,
                    target_timestamp + 5,
                    target_timestamp + 6,
                    target_timestamp + 7
                ]
                

                async def extract_single_frame(t):
                    try:
                        frame = await asyncio.wait_for(
                            frame_extractor.extract_frame(video_id, t),
                            timeout=8.0
                        )
                        return (t, frame) if frame else (t, None)
                    except asyncio.TimeoutError:
                        print(f"[CHAT] ✗ Frame extraction timeout at {t}s")
                        return (t, None)
                    except Exception as e:
                        print(f"[CHAT] ✗ Frame extraction error at {t}s: {e}")
                        return (t, None)
                
                frame_results = await asyncio.gather(*[extract_single_frame(t) for t in frame_times])
                frames = [(t, f) for t, f in frame_results if f]
                frames.sort(key=lambda x: x[0])
                print(f"[CHAT] ✓ Extracted {len(frames)}/10 frames (GOAL-DETECTION MODE: 2s before + 7s after, 2 frames before + target + 7 frames after - focusing on AFTER frames)")
                
                if frames:
                    print(f"[CHAT] ✓ Extracted {len(frames)} frames, analyzing with Vision AI in parallel...")
                    

                    async def analyze_single_frame(frame_time: float, frame_base64: str) -> Optional[str]:
                        frame_min = int(frame_time // 60)
                        frame_sec = int(frame_time % 60)
                        frame_str = f"{frame_min}:{frame_sec:02d}"
                        vision_context = f"Video title: {video_title}. Analyzing frame at {frame_str} (part of sequence from {window_str})."
                        try:
                            print(f"[CHAT] Analyzing frame at {frame_str}...")

                            analysis = await asyncio.wait_for(
                                vision_analyzer.analyze_frame(frame_base64, context=vision_context),
                                timeout=10.0
                            )
                            if analysis and analysis.strip():
                                print(f"[CHAT] ✓ Frame {frame_str} analyzed: {analysis[:60]}...")
                                return f"At {frame_str}: {analysis}"
                            else:
                                print(f"[CHAT] ✗ Frame {frame_str} returned empty analysis")
                        except asyncio.TimeoutError:
                            print(f"[CHAT] ✗ Frame {frame_str} analysis timeout (10s)")
                            return None
                        except Exception as e:
                            print(f"[CHAT] ✗ Error analyzing frame at {frame_str}: {e}")
                            import traceback
                            traceback.print_exc()
                        return None
                    


                    analysis_results = []
                    
                    print(f"[CHAT] Starting SEQUENTIAL analysis of {len(frames)} frames (1 at a time with 10s delays to avoid rate limits)...")
                    for idx, (frame_time, frame_base64) in enumerate(frames):
                        result = await analyze_single_frame(frame_time, frame_base64)
                        analysis_results.append(result)
                        



                        if idx < len(frames) - 1:
                            await asyncio.sleep(10.0)
                    

                    analyses = [
                        result for result in analysis_results
                        if result and not isinstance(result, Exception)
                    ]
                    
                    if analyses:
                        visual_analysis = "\n".join(analyses)
                        print(f"[CHAT] ✓ Vision AI successfully analyzed {len(analyses)}/{len(frames)} frames")
                    else:
                        print(f"[CHAT] ✗ WARNING: No frames were successfully analyzed! All {len(frames)} frames failed.")
                        visual_analysis = None
            except Exception as e:
                print(f"[CHAT] Could not extract/analyze frames: {e}")
                import traceback
                traceback.print_exc()
        


        target_min = int(target_timestamp // 60)
        target_sec = int(target_timestamp % 60)
        target_str = f"{target_min}:{target_sec:02d}"
        

        window_start_min = int(window_start // 60)
        window_start_sec = int(window_start % 60)
        window_end_min = int(window_end // 60)
        window_end_sec = int(window_end % 60)
        window_str = f"{window_start_min}:{window_start_sec:02d} - {window_end_min}:{window_end_sec:02d}"
        
        if captions_in_window:
            caption_texts = []
            for cap in captions_in_window:
                cap_start = float(cap.get('start', 0))
                cap_min = int(cap_start // 60)
                cap_sec = int(cap_start % 60)
                cap_text = cap.get('text', '').strip()
                if cap_text:
                    caption_texts.append(f"At {cap_min}:{cap_sec:02d}: {cap_text}")
            
            if caption_texts:
                user_prompt += f"USER IS ASKING ABOUT TIMESTAMP {target_str} (analyzing captions from {window_str} - 5 seconds before and 5 seconds after):\n\n"
                user_prompt += "=== VIDEO CAPTIONS/COMMENTARY (PRIMARY SOURCE) ===\n"
                user_prompt += "\n".join(caption_texts) + "\n\n"
                user_prompt += f"This is what the commentators said during the time period around {target_str} (from {window_str}). Use this as your PRIMARY source to answer the question.\n"
                user_prompt += "Be specific - mention goals, shots, saves, player actions, and key moments mentioned in the captions.\n"
                user_prompt += "If captions mention 'GOAL', 'scored', 'celebrates', or similar, state it clearly!\n"
                user_prompt += f"Focus on what happened at or around {target_str} based on these captions.\n\n"
                print(f"[CHAT] Using captions-only mode for {target_str} (window: {window_str}): {len(caption_texts)} captions found")
            else:
                user_prompt += f"USER IS ASKING ABOUT TIMESTAMP {target_str}:\n\n"
                user_prompt += "No captions available for this timestamp. Answer based on video metadata and context provided.\n\n"
        else:
            user_prompt += f"USER IS ASKING ABOUT TIMESTAMP {target_str}:\n\n"
            user_prompt += "No captions available for this timestamp. Answer based on video metadata and context provided.\n\n"
        


        if False and not visual_analysis and captions_in_window:
            try:
                target_min = int(target_timestamp // 60)
                target_sec = int(target_timestamp % 60)
                target_str = f"{target_min}:{target_sec:02d}"
                
                caption_texts = []
                for cap in captions_in_window:
                    cap_start = float(cap.get('start', 0))
                    cap_min = int(cap_start // 60)
                    cap_sec = int(cap_start % 60)
                    cap_text = cap.get('text', '').strip()
                    if cap_text:
                        caption_texts.append(f"At {cap_min}:{cap_sec:02d}: {cap_text}")
                
                if caption_texts:
                    user_prompt += f"USER IS ASKING ABOUT TIMESTAMP {target_str} (analyzing window: 2s before + 7s after = {window_str}, focusing on AFTER frames for goal detection):\n"
                    user_prompt += f"VIDEO CAPTIONS/COMMENTARY:\n" + "\n".join(caption_texts) + "\n"
                    user_prompt += "This is what the commentators said during this time period. Use this to answer the question.\n\n"
                    print(f"[CHAT] Using captions for {target_str}: {len(caption_texts)} captions found")
            except Exception as e:
                print(f"[CHAT] Could not format captions: {e}")
        

        if context and context.get('caption'):
            user_prompt += f"CURRENT VIDEO CAPTION/COMMENTARY AT {timestamp_str}: {context['caption']}\n"
            user_prompt += "This is the actual commentary from the video at the current playback time.\n\n"
        
        if not context or (not context.get('commentary') and not context.get('nflAnalogy') and not context.get('caption') and not captions_in_window and not visual_analysis):
            user_prompt += f"NOTE: Limited context available. The user is watching a soccer video at {timestamp_str}. "
            if video_title:
                user_prompt += f"The video is titled: '{video_title}'. "
            user_prompt += "Use your knowledge of soccer to answer specifically about what typically happens at this moment.\n\n"
        
        user_prompt += f"USER QUESTION: {user_message}\n\n"
        

        if asked_timestamp is not None or is_asking_about_now:
            target_min = int(target_timestamp // 60)
            target_sec = int(target_timestamp % 60)
            start_min = int(window_start // 60)
            start_sec = int(window_start % 60)
            end_min = int(window_end // 60)
            end_sec = int(window_end % 60)
            user_prompt += f"INSTRUCTIONS: The user is asking about what happened at timestamp {target_min}:{target_sec:02d} (analyzing window: 2 seconds before + 7 seconds after = {start_min}:{start_sec:02d} to {end_min}:{end_sec:02d}). "
            user_prompt += f"CRITICAL: Pay special attention to frames AFTER {target_min}:{target_sec:02d} (1-7 seconds after) - goals often happen AFTER shots/passes, not at the exact moment! "
            if audio_transcript or visual_analysis or captions_in_window:
                sources = []
                if audio_transcript:
                    sources.append("Audio Transcription")

                if captions_in_window:
                    user_prompt += "Use the VIDEO CAPTIONS provided above as your PRIMARY source. "
                    user_prompt += "The captions contain the commentator's real-time description. "
                    if video_title:
                        user_prompt += f"The video is titled '{video_title}' - use this for team names and context. "
                    user_prompt += "Be SPECIFIC - mention goals, shots, saves, player actions, and key moments mentioned in the captions. "
                    user_prompt += "If captions mention 'GOAL', 'scored', 'celebrates', or similar, state it clearly!"
                else:
                    user_prompt += "Answer based on the video metadata and context provided. "
                    if video_title:
                        user_prompt += f"The video is titled '{video_title}' - use this for context. "
                    user_prompt += "Be SPECIFIC about what happened during this time period."
        elif is_generic_context:
            user_prompt += "INSTRUCTIONS: The analysis above is generic/placeholder. "
            if video_title:
                user_prompt += f"However, the video is titled '{video_title}' - use this to understand what's happening. "
            if context and context.get('caption'):
                user_prompt += "The CURRENT VIDEO CAPTION above shows what the commentators said - use that as the primary source. "
            user_prompt += f"Answer based on the video title, caption (if provided), and your knowledge of soccer. "
            user_prompt += f"Be SPECIFIC - mention what type of play, tactics, or situation is happening at {timestamp_str}. "
            user_prompt += "If this is a famous moment (like Roberto Carlos free kick), describe that specific moment."
        else:
            user_prompt += "INSTRUCTIONS: Answer the question SPECIFICALLY about this moment. "
            if context and context.get('caption'):
                user_prompt += "The CURRENT VIDEO CAPTION shows what actually happened - prioritize that information. "
            user_prompt += "Reference the analysis and caption provided above. "
            user_prompt += "If the question is about the video itself, be specific about what's happening at this timestamp. Don't give generic responses - be detailed and specific."
        

        

        max_retries = 3
        retry_delay = 2.0
        
        for attempt in range(max_retries):
            try:
                print(f"[CHAT] Sending request to Azure OpenAI... (attempt {attempt + 1}/{max_retries})")
                response = await self.client.post(
                    self.chat_endpoint,
                    headers={
                        "api-key": self.api_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 200
                    }
                )
                
                print(f"[CHAT] Azure OpenAI response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    ai_response = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                    print(f"[CHAT] ✓ Got AI response: {ai_response[:100]}...")
                    return ai_response
                elif response.status_code == 429:

                    error_data = response.json() if response.text else {}
                    retry_after = error_data.get('error', {}).get('message', '')
                    
                    if attempt < max_retries - 1:

                        import re
                        retry_match = re.search(r'retry after (\d+) seconds?', retry_after.lower())
                        if retry_match:
                            retry_delay = float(retry_match.group(1)) + 1
                        else:
                            retry_delay = retry_delay * 2
                        
                        print(f"[CHAT] Rate limit (429) - waiting {retry_delay:.1f}s before retry...")
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        print(f"[CHAT] ✗ Azure OpenAI rate limit - max retries reached")
                        return self._generate_stub_response(user_message, current_time, context)
                else:
                    print(f"[CHAT] ✗ Azure OpenAI API error: {response.status_code} - {response.text}")
                    return self._generate_stub_response(user_message, current_time, context)
            except Exception as e:
                print(f"[CHAT] ✗ Chat service error: {e}")
                import traceback
                traceback.print_exc()

                if attempt == max_retries - 1:
                    return self._generate_stub_response(user_message, current_time, context)

                await asyncio.sleep(retry_delay)
                continue
        

        return self._generate_stub_response(user_message, current_time, context)
    
    def _generate_stub_response(self, user_message: str, current_time: float, context: Optional[Dict[str, Any]] = None) -> str:
        
        print(f"[CHAT] Generating stub response (Azure OpenAI not available)")
        minutes = int(current_time // 60)
        seconds = int(current_time % 60)
        timestamp_str = f"{minutes}:{seconds:02d}"
        
        user_lower = user_message.lower()
        

        if any(word in user_lower for word in ['what', 'happening', 'going on']):
            if context and context.get('commentary'):
                return f"At {timestamp_str}, {context['commentary']} This is a placeholder response - Azure OpenAI integration coming soon!"
            return f"At {timestamp_str}, players are engaged in active play. This is a placeholder response - configure Azure OpenAI to get real answers!"
        
        if any(word in user_lower for word in ['why', 'reason', 'explain']):
            if context and context.get('nflAnalogy'):
                return f"At {timestamp_str}, {context['nflAnalogy']} This is a placeholder response - configure Azure OpenAI for detailed explanations!"
            return f"At {timestamp_str}, this play demonstrates tactical movement. This is a placeholder response - configure Azure OpenAI to get real explanations!"
        
        if any(word in user_lower for word in ['tactic', 'strategy', 'formation']):
            return f"At {timestamp_str}, the teams are executing their tactical plans. This is a placeholder response - configure Azure OpenAI for tactical analysis!"
        

        return f"At {timestamp_str}, I understand you're asking: '{user_message}'. This is a placeholder response - configure Azure OpenAI to get intelligent answers about the play!"
