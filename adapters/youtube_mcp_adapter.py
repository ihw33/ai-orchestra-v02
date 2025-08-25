"""
YouTube MCP Adapter for OrchestrEX
영상 자막을 추출하여 AI 오케스트라 시스템과 통합
"""

import json
import subprocess
from typing import Dict, Any, Optional
# from adapters.base import BaseAdapter  # BaseAdapter 상속 제거
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

class YouTubeMCPAdapter:
    """YouTube MCP 서버와 통신하는 어댑터"""
    
    def __init__(self, session_name: str = "youtube_mcp"):
        self.session_name = session_name
        self.mcp_server = "youtube"
        
    def extract_video_id(self, url: str) -> str:
        """YouTube URL에서 video ID 추출"""
        parsed = urlparse(url)
        if parsed.hostname in ('youtu.be', 'www.youtu.be'):
            return parsed.path[1:]
        if parsed.hostname in ('youtube.com', 'www.youtube.com'):
            if parsed.path == '/watch':
                return parse_qs(parsed.query)['v'][0]
            elif parsed.path.startswith('/v/'):
                return parsed.path[3:]
            elif parsed.path.startswith('/shorts/'):
                return parsed.path[8:]
        raise ValueError(f"Could not extract video ID from URL: {url}")
    
    def get_transcript(self, video_url: str, with_timestamps: bool = True, language: str = "en") -> Dict[str, Any]:
        """
        YouTube 영상의 자막을 가져옴
        
        Args:
            video_url: YouTube 영상 URL
            with_timestamps: 타임스탬프 포함 여부
            language: 자막 언어 (기본: en)
            
        Returns:
            자막 데이터와 메타정보
        """
        try:
            video_id = self.extract_video_id(video_url)
            
            # YouTube Transcript API 직접 사용
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # 언어별 자막 시도
            transcript = None
            try:
                transcript = transcript_list.find_transcript([language])
            except:
                # 요청한 언어가 없으면 첫 번째 가능한 자막 사용
                for t in transcript_list:
                    transcript = t
                    break
            
            if not transcript:
                return {
                    "error": f"No transcript found for video {video_id}",
                    "video_id": video_id
                }
            
            # 자막 데이터 가져오기
            transcript_data = transcript.fetch()
            
            # 포맷팅
            if with_timestamps:
                formatted_text = self._format_with_timestamps(transcript_data)
            else:
                formatted_text = "\n".join([entry['text'] for entry in transcript_data])
            
            return {
                "video_id": video_id,
                "video_url": video_url,
                "language": transcript.language,
                "transcript": formatted_text,
                "raw_data": transcript_data,
                "metadata": {
                    "total_segments": len(transcript_data),
                    "duration": transcript_data[-1]['start'] + transcript_data[-1]['duration'] if transcript_data else 0
                }
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "video_url": video_url
            }
    
    def _format_with_timestamps(self, transcript_data: list) -> str:
        """타임스탬프와 함께 자막 포맷팅"""
        def format_timestamp(seconds: float) -> str:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            if hours > 0:
                return f"[{hours}:{minutes:02d}:{secs:02d}]"
            return f"[{minutes}:{secs:02d}]"
        
        return "\n".join(
            f"{format_timestamp(entry['start'])} {entry['text']}" 
            for entry in transcript_data
        )
    
    def process_for_ai(self, transcript_data: Dict[str, Any], task: str = "summarize") -> str:
        """
        자막 데이터를 AI 작업에 맞게 전처리
        
        Args:
            transcript_data: get_transcript의 반환값
            task: 작업 유형 (summarize, analyze, extract_topics 등)
            
        Returns:
            AI에게 전달할 프롬프트
        """
        if "error" in transcript_data:
            return f"Error: {transcript_data['error']}"
        
        transcript = transcript_data.get("transcript", "")
        
        prompts = {
            "summarize": f"""다음 YouTube 영상 자막을 요약해주세요:
            
{transcript}

주요 포인트를 bullet points로 정리해주세요.""",
            
            "analyze": f"""다음 YouTube 영상 자막을 분석해주세요:
            
{transcript}

1. 주제와 핵심 메시지
2. 주요 논점들
3. 실용적인 인사이트""",
            
            "extract_topics": f"""다음 YouTube 영상 자막에서 주요 토픽들을 추출해주세요:
            
{transcript}

각 토픽과 관련 타임스탬프를 함께 제공해주세요.""",

            "create_lesson": f"""다음 YouTube 영상 자막을 기반으로 학습 콘텐츠를 만들어주세요:

{transcript}

다음 형식으로 작성:
1. 학습 목표
2. 핵심 개념 (3-5개)
3. 실습 과제
4. 퀴즈 문제 (3개)"""
        }
        
        return prompts.get(task, transcript)
    
    def send_to_ai(self, ai_session: str, prompt: str) -> bool:
        """
        처리된 데이터를 특정 AI 세션으로 전송
        
        Args:
            ai_session: AI 세션 이름 (예: "gemini", "claude", "chatgpt")
            prompt: 전송할 프롬프트
            
        Returns:
            전송 성공 여부
        """
        try:
            # OrchestrEX의 기존 통신 시스템 활용
            from controllers.tmux_controller import TmuxController
            
            controller = TmuxController()
            
            # 세션에 메시지 전송
            success = controller.send_to_pane(ai_session, prompt)
            
            return success
            
        except Exception as e:
            print(f"Error sending to {ai_session}: {e}")
            return False