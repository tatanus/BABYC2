class BackgroundSession(Exception):
    """Custom exception to exit command loop"""
    pass

class KillAgent(Exception):
    """Custom exception to flag a Killed Agent"""
    pass