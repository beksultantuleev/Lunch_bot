from core_bot.core_bot import *
from bot_commands.main_command import *
from bot_commands.c_order_handlers import *
from bot_commands.c_garnish_handlers import *
from bot_commands.c_basket_handlers import *
from bot_commands.c_review_handlers import *
from bot_commands.a_menu_handlers import *
from db_tables.db_tables import *


logging.basicConfig(level=logging.INFO, stream=sys.stdout)
asyncio.run(main())