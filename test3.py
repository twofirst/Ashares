# encoding=utf-8

from jieba import posseg

print([(w,p) for w,p in posseg.cut('室内外装饰装修；房屋建筑；钢结构工程安装；管道和设备安装；电气安装；广告设计制作；标牌制作；门窗制作安装；办公用品、文具用品、五金电料、水性涂料（不含油漆）、采暖炉、太阳能销售**（依法须经批准的项目，经相关部门批准后方可开展经营活动）')])