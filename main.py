from threading import Thread
import pfcbot, talkbot, nbabot

if __name__ == '__main__':
    Thread(target=talkbot.main).start()
    # Thread(target=pfcbot.main).start()
    Thread(target=nbabot.main).start()
else:
    print(__name__)