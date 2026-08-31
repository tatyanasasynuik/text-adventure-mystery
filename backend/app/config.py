DEV_USERNAME = "dev"  # single stand-in player until real auth exists; shared by
# app/main.py and devtool.py so the two can't drift apart on it.

# Kill switch for the "credits" easter egg (typed command, see main.py's
# CREDITS_PHRASES) that shows the Cellar ASCII art. Still being play-tested —
# flip to False to pull the command without touching the handler itself.
SHOW_CREDITS_COMMAND = True
