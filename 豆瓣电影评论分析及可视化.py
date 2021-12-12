from peewee import SqliteDatabase
from models import Comment,Movie,MovieChinese
import pandas as pd
import jieba
from pyecharts.charts import WordCloud
from pyecharts.globals import ThemeType
import pyecharts.options as opts
from tqdm import tqdm
from cutecharts.charts import Bar


def get_movie_counts():
    # 把数据库内容自动生成模型对应的类
    # python -m pwiz -e sqlite douban_comment_data.db> models.py
    db = SqliteDatabase('douban_comment_data.db')

    comment = Comment.select()
    movieid_list = []
    for c in comment:
        movieid_list.append(c.movieid)
    counts = pd.Series(movieid_list).value_counts()
    print('各个电影的评论数为:{}'.format(counts))
get_movie_counts()

def getMovieInfo(db):
    # 读取'douban_comment_data'数据库
    data = SqliteDatabase(db)
    # 获取'movie'表格中的电影ID,及电影名称 分别添加到movie_id_list , movie_name_list
    movie_id_list = []
    movie_name_list = []
    movie_info = Movie.select()
    # print(movie_info)
    for movie in movie_info:
        movie_id_list.append(movie.id)
        movie_name_list.append(movie.name)
    return movie_name_list,movie_id_list
    # print(movie_name_list)
    # print(movie_id_list)

# 将电影名称和ID做成字典
def getUserChoice(movie_name_list,movie_id_list):
    movie_dict = dict(zip(movie_name_list,movie_id_list))
    # print(movie_dict)

    # 从电影列表中选择一个自己想要看的电影
    your_movie_name = input('输入一个自己想看的电影名称吧>>>')
    while your_movie_name not in movie_name_list:
        print('这部电影暂时没有,换一部试试看吧')
        your_movie_name = input('输入一个自己想看的电影名称吧>>>')
    else:
        your_movie_id = movie_dict[your_movie_name]
    return your_movie_name,your_movie_id


def getComment(your_movie_id):
    # 读取'comment'表格数据，根据电影ID获取每部电影的评论内容
    comments = Comment.select().where(Comment.movieid == your_movie_id,Comment.rating>0)
    if comments:
        comment_list = ''
        for comment in comments:
            # 将每一条评论放在一个字符串,以换行符隔开
            if comment.content:
                # print(comment.content)
                comment_list += comment.content + '\n'
        # print(comment_list)
        # 把评论内容用jieba模块切割成关键词词语
        jieba_list = list(jieba.cut(comment_list))
        # 将关键词列表转化为Serier类型数据,方便处理
        keyword_counts = pd.Series(jieba_list)
        # print(keyword_counts)
        # 将关键词长度小于2的过滤掉 用 data.str.len()方法
        keyword_counts = keyword_counts[keyword_counts.str.len()>=2]
        # 设置一个过滤词列表，过滤掉无用的词语
        FILTER_WORDS = ['知道','影评', '电影', '影片', '这么', '那么', '怎么', '如果', '是','喎',
                        '\n','的', '一部','这部', '这个', '一个', '这种', '时候', '什么', '没有',
                        '还有','这样','...','那样','the','一直','我','你','其实','觉得', '不过',
                        '他们','那个','片子','为了','以为','继续','。','一些','其实','时候','认为']
        #筛选包含过滤词列表中词语的数据 用 data.str.contains(字符串或者正则表达式)方法  '~'表示取反
        keyword_counts = keyword_counts[~keyword_counts.str.contains('|'.join(FILTER_WORDS))]
        # 统计关键词出现的次数 取出前100个高频词语
        keyword_counts = keyword_counts.value_counts()[:99]
    # print(keyword_counts)
        return keyword_counts

def getScore(your_movie_id):
    # 读取'comment'表格数据，根据电影ID获取每部电影的评分rating
    comments = Comment.select().where(Comment.movieid == your_movie_id,Comment.rating>0)
    score1_list = []
    score2_list = []
    score3_list = []
    score4_list = []
    score5_list = []
    score_all_list = []
    for comment in comments:
        # 将电影1分-5分的都存放在列表中
        if comment.rating ==1:
            score1_list.append(comment.rating)
        elif comment.rating == 2:
            score2_list.append(comment.rating)
        elif comment.rating == 3:
            score3_list.append(comment.rating)
        elif comment.rating == 4:
            score4_list.append(comment.rating)
        else :
            score5_list.append(comment.rating)
        # 如果列表不为空,就把每个分数的数量统计一下存放在总列表中,方便做柱状图
    if len(score1_list) > 0:
        score_all_list.append(len(score1_list))
    else:
        score_all_list.append(0)
    if len(score2_list) > 0:
        score_all_list.append(len(score2_list))
    else:
        score_all_list.append(0)
    if len(score3_list) > 0:
        score_all_list.append(len(score3_list))
    else:
        score_all_list.append(0)
    if len(score4_list) > 0:
        score_all_list.append(len(score4_list))
    else:
        score_all_list.append(0)
    if len(score5_list) > 0:
        score_all_list.append(len(score5_list))
    else:
        score_all_list.append(0)
    return score_all_list

def renderWordcloud(your_movie_name,keyword_counts):

    wordcloud = WordCloud(init_opts=opts.InitOpts(theme=ThemeType.ROMANTIC ,                                                  width = '1080px' , height = '719px'))   # 创建数据
    data = tuple(zip(keyword_counts.index,keyword_counts))
    wordcloud.add('',data,word_size_range = [20,100],shape = 'diamond')
    wordcloud.set_global_opts(title_opts = opts.TitleOpts(title = '如果对评论不满意的话,你也去评论一下吧'))
    wordcloud.render('douban_wordcloud/{}影评词云图.html'.format(your_movie_name))


def renderCuteBar(your_movie_name,data):
    bar = Bar('《{}》评分情况'.format(your_movie_name))
    bar.set_options(labels=['1分', '2分', '3分', '4分', '5分'], x_label="I'm xlabel", y_label=" I'm ylabel")
    bar.add_series('才这么点', data)
    for i in tqdm(range(int(10e6)),ncols=88,desc='可爱柱状图生成中...'):
        pass
    bar.render('douban_Bar/{}可爱风柱状图.html'.format(your_movie_name))

# 调用函数获取数据库内容
name_list,id_list = getMovieInfo('douban_comment_data.db')
# 调用函数生成用户输入的电影名称,和对应的ID号
your_movie_name,your_movie_id = getUserChoice(name_list,id_list)
# 根据ID号生成评论
keyword_counts = getComment(your_movie_id)
# print(keyword_counts)
# 生成词云图
wordcloud = renderWordcloud(your_movie_name,keyword_counts)
print('你想看的电影《{}》影评词云图已经产生,快去查看一下吧'.format(your_movie_name))
# 调用函数，通过输入电影ID参数获取电影评分情况
score_list = getScore(your_movie_id)
# 生成可爱风Bar图
bar = renderCuteBar(your_movie_name,score_list)
print('你想看的电影《{}》评分可爱风Bar图已经生成,非常可爱哦'.format(your_movie_name))