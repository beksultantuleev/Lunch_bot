from core_bot.core_bot import *
from bot_commands.main_command import *



logging.basicConfig(level=logging.INFO, stream=sys.stdout)
asyncio.run(main())