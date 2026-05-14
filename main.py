import os
import tomllib

import nonebot
from nonebot.adapters.onebot.v11 import Adapter

from lib import logger, database
from lib.database import config
from lib.database.config import set_toml_config
from lib.rule_registry import scan_and_register, get_registry

banner = r'''
   __________  ________________  ________          __ 
  / ____/ __ \/ ____/ ____/ __ \/ ____/ /_  ____  / /_
 / /   / /_/ / __/ / __/ / /_/ / __/ / __ \/ __ \/ __/
/ /___/ _, _/ /___/ /___/ ____/ /___/ /_/ / /_/ / /___
\____/_/ |_/_____/_____/_/  _/_____/_.___/\____/\__/ /
         / __/ -_|_-</ _ \/ _ `/ |/|/ / _ \/ -_) _  / 
        /_/  \__/___/ .__/\_,_/|__,__/_//_/\__/\_,_/  
孩子们我回来了        /_/            2024.7.18-2026.5.12 
'''

# -------------------------
#    CREEPEBOT_RESPAWNED
#        孩子们我回来了
# -------------------------

if __name__ == '__main__':

    print(banner)

    # 解析配置并连接数据库
    with open('config.toml', 'rb') as f:
        toml_config = tomllib.load(f)

    # 按情况接管nb2的日志
    if toml_config['logging']['inject_nonebot']:
        logger.inject_nonebot_logger()

    logger.set_log_level(toml_config['logging']['level'])

    logger.debug('配置文件已解析成功')

    database.connect_database(toml_config['database']['mongo_connection_string'])
    config.connect_database(toml_config['database']['mongo_connection_string'])

    logger.debug('数据库已连接')

    # 将toml配置复制到nb .env
    if os.path.exists('.env'):
        os.remove('.env')

    with open('.env', 'w') as f:
        for key, value in toml_config['nonebot'].items():
            f.write(str(key).upper() + '=' + str(value).replace("'", '"') + '\n')

    logger.debug('nonebot配置转发完成')

    # 存储配置
    set_toml_config(toml_config)

    logger.info('CREEPEbot respawned **堂堂复活**! 孩子们我回来了')

    # 注册事件处理规则
    scan_and_register('./nb_plugins/creepebot_respawned')
    logger.info(f'已配置 `{len(get_registry())}` 条事件处理规则')

    # nb2, 启动!
    nonebot.init()
    driver = nonebot.get_driver()
    driver.register_adapter(Adapter)

    nonebot.load_builtin_plugins('echo')  # 内置插件
    nonebot.load_plugins('nb_plugins')  # 本地插件

    logger.info('nonebot已启动')

    nonebot.run()
