"""
Live News Regrader: Regrades open props/tickets if news drops before lock.
"""
import logging

class LiveNewsRegrader:
    def __init__(self, history, logger=None):
        self.history = history
        self.logger = logger or logging.getLogger("LiveNewsRegrader")

    def regrade_on_news(self, open_tickets, news):
        """
        Regrades/flags open tickets/props if news drops before lock.
        """
        for ticket in open_tickets:
            for leg in ticket.get('legs', []):
                if news and leg.get('player_name') in news.get('affected_players', []):
                    leg['regraded'] = True
                    leg['news_flag'] = news.get('headline', 'news_event')
        self.logger.info(f"[LiveNewsRegrader] Regraded tickets on news: {news.get('headline', '') if news else 'No news'}.")
        return open_tickets 