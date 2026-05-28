import os
import tomllib
from typing import Dict, Any

import nonebot
from nonebot.adapters.onebot.v11 import Adapter

from message_source.mc import start_sync
from lib import logger, database
from lib.backup.auto import start_auto_backup
from lib.database import config, cache
from lib.database.config import set_toml_config
from lib.mcsmanager import set_api_key, set_base_url
from lib.mcsmanager.instance import rebuild_instance_nickname_cache
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
        toml_config: Dict[str, Dict[str, Any]] = tomllib.load(f)

    # 设置MCSM api key / base url
    mcsm_ready = True

    if 'mcsm' in toml_config.keys() and 'key' in toml_config['mcsm'].keys():
        set_api_key(toml_config['mcsm']['key'])
    else:
        logger.warn('MCSManager API KEY **未设置**! 无法使用Minecraft服务器管理功能')
        mcsm_ready = False

    if 'mcsm' in toml_config.keys() and 'base_url' in toml_config['mcsm'].keys():
        set_base_url(toml_config['mcsm']['base_url'])
    else:
        logger.warn('MCSManager BASE URL **未设置**! 无法使用Minecraft服务器管理功能')
        mcsm_ready = False

    cache.connect_database(toml_config['database']['mongo_connection_string'])
    database.connect_database(toml_config['database']['mongo_connection_string'])
    config.connect_database(toml_config['database']['mongo_connection_string'])

    logger.debug('数据库已连接')

    # 重建缓存
    if mcsm_ready: rebuild_instance_nickname_cache()

    # 按情况接管nb2的日志
    if toml_config['logging']['inject_nonebot']:
        logger.inject_nonebot_logger()

    logger.set_log_level(toml_config['logging']['level'])

    logger.debug('配置文件已解析成功')

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
    scan_and_register('rules')
    logger.info(f'已配置 `{len(get_registry())}` 条事件处理规则')

    # nb2, 启动!
    nonebot.init()
    driver = nonebot.get_driver()

    # 启动聊天转发
    if mcsm_ready: driver.on_startup(start_sync)
    if mcsm_ready: driver.on_startup(start_auto_backup)

    driver.register_adapter(Adapter)
    nonebot.load_builtin_plugins('echo')  # 内置插件
    nonebot.load_plugin('message_source.qq')  # 本地插件

    logger.info('nonebot已启动')

    nonebot.run()
