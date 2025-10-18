import json
from datetime import datetime, timedelta

class ContentOptimizer:
    def __init__(self):
        self.optimal_times = {
            "weekday_morning": "07:00-09:00",
            "weekday_lunch": "12:00-13:00",
            "weekday_evening": "17:00-19:00",
            "weekend_morning": "09:00-11:00",
            "weekend_afternoon": "14:00-16:00"
        }
    
    def optimize_content(self, story_text, niche, language):
        """Generate optimized content metadata"""
        
        # Generate title
        title = self._generate_title(story_text, niche, language)
        
        # Generate description
        description = self._generate_description(story_text, niche, language)
        
        # Generate hooks
        hooks = self._generate_hooks(story_text, niche, language)
        
        # Generate hashtags
        hashtags = self._generate_hashtags(niche, language)
        
        # Calculate optimal posting times
        posting_times = self._get_optimal_posting_times()
        
        return {
            "title": title,
            "description": description,
            "hooks": hooks,
            "hashtags": hashtags,
            "optimal_posting_times": posting_times
        }
    
    def _generate_title(self, story_text, niche, language):
        """Generate engaging title"""
        first_sentence = story_text.split('.')[0]
        
        if language == 'id':
            return f"🤫 RAHASIA {niche.upper()} YANG TAK PERNAH DICERITAKAN!"
        else:
            return f"🤫 SECRET {niche.upper()} FACTS NOBODY TELLS YOU!"
    
    def _generate_description(self, story_text, niche, language):
        """Generate video description"""
        if language == 'id':
            return f"""🎬 Video {niche} yang wajib kamu tonton!

{story_text[:200]}...

Jangan lupa:
✓ Like jika bermanfaat
✓ Comment pendapatmu
✓ Subscribe untuk konten menarik lainnya"""
        else:
            return f"""🎬 Must-watch {niche} video!

{story_text[:200]}...

Don't forget to:
✓ Like if helpful
✓ Comment your thoughts
✓ Subscribe for more amazing content"""
    
    def _generate_hooks(self, story_text, niche, language):
        """Generate video hooks"""
        if language == 'id':
            return [
                "Tahukah kamu rahasia tersembunyi ini?",
                "Ini akan mengubah cara pandangmu selamanya!",
                "Jangan skip video ini jika kamu ingin tahu kebenarannya!"
            ]
        else:
            return [
                "Did you know this hidden secret?",
                "This will change your perspective forever!",
                "Don't skip this video if you want to know the truth!"
            ]
    
    def _generate_hashtags(self, niche, language):
        """Generate relevant hashtags"""
        if language == 'id':
            return ["viral", "trending", "fyp", niche.lower().replace(' ', ''), "faktamenarik"]
        else:
            return ["viral", "trending", "fyp", niche.lower().replace(' ', ''), "facts"]
    
    def _get_optimal_posting_times(self):
        """Calculate optimal posting times"""
        return [
            {"day": "Senin", "time_slot": "07:00-09:00", "recommendation": "Tinggi"},
            {"day": "Rabu", "time_slot": "17:00-19:00", "recommendation": "Tinggi"},
            {"day": "Sabtu", "time_slot": "09:00-11:00", "recommendation": "Sedang"}
        ]

# Singleton instance
content_optimizer = ContentOptimizer()
