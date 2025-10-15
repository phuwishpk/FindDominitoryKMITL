import asyncio
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Debugging

class MyController(Controller):
    def __init__(self, *args, **kwargs):
        # We need to pass the handler to the superclass __init__
        # The 'handler' will be passed when we create an instance of this class.
        super().__init__(*args, **kwargs)

async def main():
    # 1. Instantiate the handler that prints emails to the console.
    handler = Debugging()
    
    # 2. Instantiate our controller, passing the handler to it.
    #    This is the step that was missing and caused the error.
    controller = MyController(handler, hostname='localhost', port=8025)
    
    # Start the controller (it runs in a background thread).
    controller.start()
    
    print("เซิร์ฟเวอร์อีเมลจำลองกำลังทำงานที่ localhost:8025")
    print("กด Ctrl+C เพื่อหยุดการทำงาน...")
    
    try:
        # Keep the main program running until you press Ctrl+C.
        while True:
            await asyncio.sleep(1)
    except (asyncio.CancelledError, KeyboardInterrupt):
        # Stop the controller when the program is interrupted.
        controller.stop()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nหยุดการทำงานของเซิร์ฟเวอร์อีเมลจำลองแล้ว")