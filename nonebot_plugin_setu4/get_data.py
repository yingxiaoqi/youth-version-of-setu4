from httpx import AsyncClient
from nonebot.log import logger
import random
import asyncio
import nonebot
import sqlite3
import os
from pathlib import Path
from PIL import Image
from io import BytesIO
error = "Error:"


# save_path,可在env设置, 默认False, 类型bool或str
try:
    save_path = nonebot.get_driver().config.setu_save
    all_file_name = os.listdir(save_path)
except:
    save_path = False
    all_file_name = []


# 本地setu路径,默认在插件目录下的resource/img
# img_path = str(Path(os.path.join(os.path.dirname(__file__), "resource/img")))
# 读取file_name里面的全部文件名
# all_file_name = os.listdir(img_path)


# 返回列表,内容为setu消息(列表套娃)
async def get_setu(keyword="", r18=False, num=1, quality=75) -> list:
    data = []
    # 连接数据库
    # 数据库每个字段分别是 pid, p, title, author, r18, width, height, tags, ext, uploadDate, urls
    conn = sqlite3.connect(
        Path(os.path.join(os.path.dirname(__file__), "resource")) / "lolicon.db")
    cur = conn.cursor()
    # sql操作,根据keyword和r18进行查询拿到数据
    cursor = cur.execute(
        f"SELECT pid,p,title,author,r18,tags,urls from main where (tags like \'%{keyword}%\' or title like \'%{keyword}%\' or author like \'%{keyword}%\') and r18=\'{r18}\' order by random() limit {num}")
    db_data = cursor.fetchall()
    # 断开数据库连接
    conn.close()
    # 如果没有返回结果
    if db_data == []:
        data.append([error, f"图库中没有搜到关于{keyword}的图。", False])
        return data

    async with AsyncClient() as client:
        tasks = []
        for setu in db_data:
            tasks.append(pic(setu, quality, client))
        data = await asyncio.gather(*tasks)

    return data


# 返回setu消息列表,内容 [图片, 信息, True/False, url]
async def pic(setu, quality, client):
    setu_pid = setu[0]                   # pid
    setu_p = setu[1]                     # p
    setu_title = setu[2]                 # 标题
    setu_author = setu[3]                # 作者
    setu_r18 = setu[4]                   # r18
    setu_tags = setu[5]                  # 标签
    setu_url = setu[6].replace('i.pixiv.cat', 'i.pixiv.re')     # 图片url
    
    data = (
        "标题:"
        + setu_title
        + "\npid:"
        + str(setu_pid)
        + "\n画师:"
        + setu_author
    )

    logger.info("\n"+data+"\ntags:" +
                setu_tags+"\nR18:"+setu_r18)

    # 本地图片如果是用well404的脚本爬的话,就把下面的replace代码解除注释
    file_name = setu_url.split("/")[-1]  # .replace('p', "",1)

    # 判断文件是否本地存在
    if file_name in all_file_name:
        logger.info("图片本地存在")
        image = Image.open(save_path + "/" + file_name)
    # 如果没有就下载
    else:
        logger.info("图片本地不存在,正在去i.pixiv.re下载")

        """
            2022-10-14:
            这天下午通过i.pixiv.re反向代理下访问图片是空白内容, 然后根据pixiv.re的说明:
            連結: https://pixiv.cat/Pixiv作品數字ID.jpg|png|gif
            例如: https://pixiv.cat/82775556.jpg
            連結: https://pixiv.cat/Pixiv作品數字ID-第幾張圖.jpg|png|gif
            例如: https://pixiv.cat/78286152-2.png
            可以访问到图片, 故对url进行了修改
            圖片為動態產生，網址結尾副檔名部分無實際用途，準確檔案類型會以 Content-Type header 發送。
            所以这里url统一用jpg, 后面可以用image.format获取图片格式
        """


        if setu_p ==0:
            # 如果setu_p为0, 他可能是多图模式也可能是单图模式
            # 如果是多图模式的话, download_url = f"https://pixiv.re/{setu_pid}-{int(setu_p)+1}.jpg"
            # 如果是单图模式的话, download_url = f"https://pixiv.re/{setu_pid}.jpg"
            # 这里我们无法判断到底是多图还是单图, 所以我们都请求一次, 直到返回状态码为200
            # 根据downloadpic的返回值, 如果是int类型, 说明是状态码可能是404,408, 也就是下载失败
            download_url = f"https://pixiv.re/{setu_pid}.jpg"
            content = await down_pic(setu_url, client, download_url)
            if type(content) == int:
                download_url = f"https://pixiv.re/{setu_pid}-{int(setu_p)+1}.jpg"
                content = await down_pic(setu_url, client, download_url)
        else:
            # 如果setu_p不为0的话, 那么说明铁定是多图模式, 又因为pixiv的p是从0开始计算的, 所以这里+1
            download_url = f"https://pixiv.re/{setu_pid}-{int(setu_p)+1}.jpg"
            content = await down_pic(setu_url, client, download_url)
        
        #  此次fix结束
        
        if type(content) == int:
            logger.error(f"图片下载失败, 状态码: {content}")
            return [error, f"图片下载失败, 状态码{content}", False, setu_url]
        image = Image.open(BytesIO(content))

    pic = await change_pixel(image, quality)
    return [pic, data, True, setu_url]


# 图片左右镜像
async def change_pixel(image, quality):
    image = image.transpose(Image.FLIP_LEFT_RIGHT)
    image = image.convert("RGB")
    byte_data = BytesIO()
    image.save(byte_data, format="JPEG", quality=quality)
    # pic是的图片的bytes
    pic = byte_data.getvalue()
    return pic


# 下载图片并且返回content,或者status_code
async def down_pic(url, client,download_url):
    headers = {
        "Referer": "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
    }
    try:
        re = await client.get(url=download_url, headers=headers, timeout=60)
        if re.status_code == 200:
            logger.success("成功获取图片")
            if save_path:
                file_name = url.split("/")[-1]
                try:
                    with open(f"{save_path}/{file_name}", "wb") as f:
                        f.write(re.content)
                    all_file_name.append(file_name)
                except Exception as e:
                    logger.error(f'图片存储失败: {e}')
            return re.content
        else:
            return re.status_code
    except:
        return 408
