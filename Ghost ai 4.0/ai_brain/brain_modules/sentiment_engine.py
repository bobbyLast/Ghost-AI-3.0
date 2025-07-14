"""
Sentiment Engine: Tracks pick sentiment/tags for future ML.
"""
import logging

class SentimentEngine:
    def __init__(self, history, logger=None):
        self.history = history
        self.logger = logger or logging.getLogger("SentimentEngine")

    def tag_sentiment(self, props):
        """
        Tags each pick with sentiment (easy read, trap bait, reverse fade, etc.).
        """
        for prop in props:
            # Example: Tag based on odds, public %, and context
            if prop.get('public_bet_pct', 0) > 0.7:
                prop['sentiment'] = 'public_trap_bait'
            elif prop.get('reverse_line_move', False):
                prop['sentiment'] = 'reverse_fade'
            elif prop.get('confidence', 0.5) > 0.8:
                prop['sentiment'] = 'easy_read'
            else:
                prop['sentiment'] = 'neutral'
        self.logger.info("[SentimentEngine] Tagged pick sentiment.")
        return props 