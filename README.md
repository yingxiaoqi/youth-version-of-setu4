# youth-version-of-setu4

内置数据库的setu插件, 另外尝试降低因为风控发不出图的概率(随机修改左上角一颗像素点) (tx好像改了算法, 作用不明显了)


### 数据库记录66337条

ghs比较纯粹, 只有一般的权限控制, 相比完整版功能简单

安装方式:
    
    pip install youth-version-of-setu4
    
    记得nonebot.load_plugin("youth-version-of-setu4")
    
    有能力尽量从本仓库clone, 因为pypi不一定最新

## env 配置项

>以下配置项均可不填，插件会按照默认值读取

|config             |type            |default|example                          |usage                 |
|-------------------|----------------|-------|---------------------------------|----------------------|
|setu_cd            |int             |20     |setu_cd = 30                     |setu的cd              |
|setu_ban           |tuple[str, int] |None   |setu_ban = ["114514", "1919810"] |禁用名单(群号或QQ号)    |
|setu_withdraw_time |int             |100    |setu_withdraw_time = 30          |setu撤回时间           |
|setu_max_num       |int             |10     |setu_max_num = 20                |setu一次性最大数量     |
|setu_save          |str             |None   |setu_save = './data/setu4/img'   |setu时候保存到本地的路径  可用绝对路径|
|setu_proxy         |str             |i.pixiv.re|setu_proxy = "i.pixiv.re" |下载图片的代理(一般我会把可用的代理设置成默认)|

setu_save保存后下一次调用碰到这个setu就不需要再下载


一般无需科学上网, 确认一下图片代理是否可用:   

    一些也许可用的pixiv代理, 用来填入env的setu_proxy变量: "i.pixiv.re" , "sex.nyan.xyz" , "px2.rainchan.win" 

    Example:

        数据库给的url为: https://i.pixiv.re/img-original/img/2022/07/09/18/51/03/99606781_p0.jpg

        有些代理可能会暂时不可用, 可以用来换成可用的代理, 比如px2.rainchan.win

        即: https://px2.rainchan.win/img-original/img/2022/07/09/18/51/03/99606781_p0.jpg

        能正常访问即可用
    
    

## 插件指令

setu命令:

    命令头: setu|色图|涩图|想色色|来份色色|来份色图|想涩涩|多来点|来点色图|来张setu|来张色图|来点色色|色色|涩涩  (任意一个)
    
    张数: 1 2 3 4 ... 张|个|份  (可不填, 默认1)
    
    r18: 填了就是r18, 不填则不是  (私聊生效, 群聊除非add_r18, 不然视为false)
    
    关键词: 任意 (可不填)
    
    参考:   
    
        setu 10张 r18 白丝
        
        setu 10张 白丝
        
        setu r18 白丝
        
        setu 白丝
        
        setu
        
        (空格可去掉)

添加r18:

    add_r18 xxxxx   (xxxx为qq号码或者群聊号码, 当为qq号码时, 该人在任意有你的bot的群都能在群聊触发r18, 当为群号时, 该群任意人都可以触发r18)

撤销r18:

    del_r18 xxxxx

查看r18列表:

    r18名单
