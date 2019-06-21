#encoding:utf-8
import pygame, sys
import random
import os

pygame.init()#pygame的开始

#定义各自的宽度，行列方向
GRID_WIDTH = 20
GRID_NUM_WIDTH = 15
GRID_NUM_HEIGHT = 25
#根据各自数量计算可视框的宽度和高度
WIDTH, HEIGHT = GRID_WIDTH * GRID_NUM_WIDTH, GRID_WIDTH * GRID_NUM_HEIGHT
SIDE_WIDTH = 300
SCREEN_WIDTH = WIDTH + SIDE_WIDTH
#定义常用颜色
WHITE = (0xff, 0xff, 0xff)
BLACK = (0, 0, 0)
LINE_COLOR = (0x33, 0x33, 0x33)
CUBE_COLORS = [
    (0xcc, 0x99, 0x99), (0xff, 0xff, 0x99), (0x66, 0x66, 0x99),
    (0x99, 0x00, 0x66), (0xff, 0xcc, 0x00), (0xcc, 0x00, 0x33),
    (0xff, 0x00, 0x33), (0x00, 0x66, 0x99), (0xff, 0xff, 0x33),
    (0x99, 0x00, 0x33), (0xcc, 0xff, 0x66), (0xff, 0x99, 0x00)
]

# 颜色矩阵，底板矩阵
screen_color_matrix = [[None] * GRID_NUM_WIDTH for i in range(GRID_NUM_HEIGHT)]
# 分数和等级
score = 0
level = 1

# 设置游戏的根目录为当前文件夹
base_folder = os.path.dirname(__file__)
# 设置屏幕宽高
screen = pygame.display.set_mode((SCREEN_WIDTH, HEIGHT))#创建了一个窗口，set_mode会返回一个Surface对象，代表了在桌面上出现的那个窗口，三个参数第一个为元祖，代表分 辨率（必须）；第二个是一个标志位，如果不用什么特性，就指定0；第三个为色深。当我们把第二个参数设置为FULLSCREEN时，就能得到一个全屏窗口了
# 设置程序名字
pygame.display.set_caption("俄罗斯方块")

#设置速度
clock = pygame.time.Clock()
FPS = 3
running = True
gameover = True
counter = 0
live_cube = None#当前方块
new_cube = None#下一个方块
pause = False
#是否成功
success = False
# 暂停时的计数，用于展示闪动的屏幕
pause_count = 0
heightScore = None#最高分
colorBool = True
dead = False

#整体界面的设计
class Wall():
    global GRID_NUM_WIDTH
    global LINE_COLOR
    global HEIGHT
    global HEIGHT

    def __init__(self):
        pass

    # 绘制背景方格
    def draw_grids(self):
        for i in range(GRID_NUM_WIDTH):
            pygame.draw.line(screen, LINE_COLOR,
                             (i * GRID_WIDTH, 0), (i * GRID_WIDTH, HEIGHT))#一列一列画线条
                            #(x, y)直角坐标系
        for i in range(GRID_NUM_HEIGHT):
            pygame.draw.line(screen, LINE_COLOR,
                             (0, i * GRID_WIDTH), (WIDTH, i * GRID_WIDTH))#一行一行画线条

        pygame.draw.line(screen, WHITE,
                         (GRID_WIDTH * GRID_NUM_WIDTH, 0),
                         (GRID_WIDTH * GRID_NUM_WIDTH, GRID_WIDTH * GRID_NUM_HEIGHT))

    #根据颜色矩阵绘制图像，更新屏幕，画方块
    def draw_matrix(self):
        for i, row in zip(range(GRID_NUM_HEIGHT), screen_color_matrix):
            for j, color in zip(range(GRID_NUM_WIDTH), row):
                if color is not None:
                    pygame.draw.rect(screen, color,#填充
                                     (j * GRID_WIDTH, i * GRID_WIDTH,
                                      GRID_WIDTH, GRID_WIDTH))
                    pygame.draw.rect(screen, WHITE,#划线
                                     (j * GRID_WIDTH, i * GRID_WIDTH,
                                      GRID_WIDTH, GRID_WIDTH), 2)

    #满行消除和记分
    def remove_full_line(self):
        global screen_color_matrix
        global score
        global level
        new_matrix = [[None] * GRID_NUM_WIDTH for i in range(GRID_NUM_HEIGHT)]#初始为None
        index = GRID_NUM_HEIGHT - 1
        n_full_line = 0
        for i in range(GRID_NUM_HEIGHT - 1, -1, -1):#倒着取，相当于每次-1
            is_full = True
            for j in range(GRID_NUM_WIDTH):
                if screen_color_matrix[i][j] is None:#这一行没满，不能消
                    is_full = False
                    continue
            if not is_full:#不消
                new_matrix[index] = screen_color_matrix[i]
                index -= 1
            else:#否则消除，不赋值则为None
                n_full_line += 1

        if n_full_line != 0:#记数规则
            score += n_full_line*(n_full_line-1)+1  # 1 3 7 13

        #计算等级
        level = score // 20 + 1
        #消除一行之后的新的矩阵赋值给矩阵
        screen_color_matrix = new_matrix


    #欢迎界面
    def show_welcome(self):
        self.show_text( u'俄罗斯方块', 30, WIDTH / 2, HEIGHT / 2)
        self.show_text( u'按任意键开始游戏', 20, WIDTH / 2, HEIGHT / 2 + 50)
        self.show_text( u'按A进入/退出AI模式', 18, WIDTH / 2, HEIGHT / 2 + 90)

    #显示文字
    def show_text(self, text, size, x, y, color=(0xff, 0xff, 0xff),bgColor = None):

        fontObj = pygame.font.Font('font/font.ttc', size)
        textSurfaceObj = fontObj.render(text, True, color,bgColor)
        textRectObj = textSurfaceObj.get_rect()
        textRectObj.center = (x, y)
        screen.blit(textSurfaceObj, textRectObj)

    def draw_score(self):
        global heightScore#最高分
        self.show_text( u'目前得分 : {}'.format(score), 18, WIDTH + SIDE_WIDTH // 2, 180)

        if heightScore is None:
            self.getHeightScore()

        if score>heightScore:
            heightScore = score

        self.show_text( u'Level : {}'.format(level), 15, WIDTH + SIDE_WIDTH // 2, 205)
        self.show_text(u'目标分数: {}'.format(heightScore), 18, WIDTH + SIDE_WIDTH // 2, 230)

    # 暂停界面的显示
    def showPause(self):
        GREEN = ( 0, 255, 0)
        BLUE = ( 0, 0, 128)
        self.show_text(u'暂停中...', 50, 250, 200, BLUE , GREEN)
        pygame.display.update() #刷新一下画面，画完以后一定记得用update更新一下，否则画面一片漆黑

    # 因为文字描述（最高分，当前分，基本操作提示以及等级）多了，封装一个函数全部显示这些东西
    def drawAll(self):
        # 更新屏幕

        screen.fill(BLACK)
        self.draw_grids()
        self.draw_matrix()
        self.draw_score()
        self.drawNextBrick()


        self.show_text( u'AI模式：A',13, WIDTH+100,HEIGHT-100 , WHITE )
        self.show_text( u'再来一次：R',13, WIDTH+100,HEIGHT-80 , WHITE )
        self.show_text( u'暂停键：P',13, WIDTH+100,HEIGHT-60 , WHITE )
        self.show_text( u'基本操作：↑↓← →',13, WIDTH+100,HEIGHT-40 , WHITE )
        self.show_text( u'学生：宋金铎',13, SCREEN_WIDTH-100,HEIGHT-10 , WHITE )

        if pause :
            self.showAD(u'暂停中', u'恢复请按P')
        else:
            self.showAD()
        if success :
            self.showAD(u'恭喜你',u'成功到达目标状态')
        else:
            self.showAD()
        if live_cube is not None:#当前方块若放好，则画下一个
            live_cube.draw()

        if gameover:
            self.show_welcome()

    # 绘制下一个方块
    def drawNextBrick(self):
        global new_cube#下一个方块
        if new_cube is not None:
            return new_cube.drawNext()

    # 读取文件，获取最高分
    def getHeightScore(self):
        global heightScore
        f = open('score.txt', 'r')
        heightScore = int( f.read() )

    # 把最高分写入文件
    def writeHeightScore(self):
        global heightScore
        f = open('score.txt', 'w')
        f.write( str(heightScore) )
        f.close()

    # 显示广告板
    def showAD(self,text1 = None , text2 = None):
        global CUBE_COLORS
        global colorBool

        line1 = ['哇塞萌新', '运气好而已', '回去吧', '是不是快挂了', '年轻人不简单', '哇塞！！', '围观大佬']
        line2 = ['你会玩吗', '狗屎运而已', '后面太难了', '哈哈哈', '看走眼了', '这样都行？', '大佬请喝茶']
        if level > len(line1):
            num = len(line1)
        else:
            num = level
        if text1 is None and text2 is None:
            if gameover:
                text1 = u'准备好了吗'
                text2 = u'坐好起飞'
            else:
                #text1 = line1[num - 1].decode('utf-8')
                #text2 = line2[num - 1].decode('utf-8')
                text1 = line1[num - 1]
                text2 = line2[num - 1]

        GREEN = (0, 255, 0)
        # 广告底板和边框
        pygame.draw.rect(screen, BLACK,#画广告位
                         (WIDTH + 20, 240,
                          160, 80))
        pygame.draw.rect(screen, GREEN,
                         (WIDTH + 20, 240,
                          160, 80), 1)

        # 这里有一个彩蛋，当你正常运行程序时，按c键，广告板的文字会闪动
        if colorBool :
            color = CUBE_COLORS[num]
        else :
            color =  CUBE_COLORS[random.randint(0, len(CUBE_COLORS) - 1)]
        # 广告的文字信息
        self.show_text( text1,18, WIDTH+100,265 , color )
        self.show_text( text2,18, WIDTH+100,295 , color )

#方块的类
class Brick():
    #各种类型的方块
    SHAPES = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']
    I = [[(0, -1), (0, 0), (0, 1), (0, 2)],
         [(-1, 0), (0, 0), (1, 0), (2, 0)]]
    J = [[(-2, 0), (-1, 0), (0, 0), (0, -1)],
         [(-1, 0), (0, 0), (0, 1), (0, 2)],
         [(0, 1), (0, 0), (1, 0), (2, 0)],
         [(0, -2), (0, -1), (0, 0), (1, 0)]]
    L = [[(-2, 0), (-1, 0), (0, 0), (0, 1)],
         [(1, 0), (0, 0), (0, 1), (0, 2)],
         [(0, -1), (0, 0), (1, 0), (2, 0)],
         [(0, -2), (0, -1), (0, 0), (-1, 0)]]
    O = [[(0, 0), (0, 1), (1, 0), (1, 1)]]
    S = [[(-1, 0), (0, 0), (0, 1), (1, 1)],
         [(1, -1), (1, 0), (0, 0), (0, 1)]]
    T = [[(0, -1), (0, 0), (0, 1), (-1, 0)],
         [(-1, 0), (0, 0), (1, 0), (0, 1)],
         [(0, -1), (0, 0), (0, 1), (1, 0)],
         [(-1, 0), (0, 0), (1, 0), (0, -1)]]
    Z = [[(0, -1), (0, 0), (1, 0), (1, 1)],
         [(-1, 0), (0, 0), (0, -1), (1, -1)]]
    SHAPES_WITH_DIR = {
        'I': I, 'J': J, 'L': L, 'O': O, 'S': S, 'T': T, 'Z': Z
    }

    #初始化函数，设置shape,center,dir(形态，也即方块方向）,color为类的自身属性
    def __init__(self):
        self.shape = self.SHAPES[random.randint(0, len(self.SHAPES) - 1)]
        # 骨牌所在的行列
        self.center = (2, GRID_NUM_WIDTH // 2)
        self.dir = random.randint(0, len(self.SHAPES_WITH_DIR[self.shape]) - 1)#初始方向随机
        self.color = CUBE_COLORS[random.randint(0, len(CUBE_COLORS) - 1)]#颜色随机变化

    #根据中心点坐标获取其他位置的点的坐标
    def get_all_gridpos(self, center=None):
        curr_shape = self.SHAPES_WITH_DIR[self.shape][self.dir]#获得一个列表
        if center is None:
            center = [self.center[0], self.center[1]]

        return [(cube[0] + center[0], cube[1] + center[1])
                for cube in curr_shape]#返回一个根据中心点更新过的列表，表示方块

    #根据中心点找到其他点的位置，看看其他点是否合法（是否超出边界， 是否已有元素）
    def conflict(self, center):
        for cube in self.get_all_gridpos(center):#检验方块的各部分是否超出边界
            # 超出屏幕之外，说明不合法
            if cube[0] < 0 or cube[1] < 0 or cube[1] >= GRID_NUM_HEIGHT or  cube[0] >= GRID_NUM_WIDTH:
                return True

            # 不为None，说明之前已经有小方块存在了，也不合法
            if screen_color_matrix[cube[0]][cube[1]] is not None:
                return True

        return False

    #旋转，要存储旧的形态（dir）是因为不知道新的形态是否合法，不合法则倒退
    def rotate(self):
        new_dir = self.dir + 1
        new_dir %= len(self.SHAPES_WITH_DIR[self.shape])
        old_dir = self.dir
        self.dir = new_dir
        if self.conflict(self.center):
            self.dir = old_dir
            return False

    #下落，中心点x轴坐标+1
    def down(self):
        # import pdb; pdb.set_trace()
        center = (self.center[0] + 1, self.center[1])
        if self.conflict(center):
            return False

        self.center = center
        return True

    #左移
    def left(self):
        center = (self.center[0], self.center[1] - 1)
        if self.conflict(center):
            return False

        self.center = center
        return True

    #右移
    def right(self):
        center = (self.center[0], self.center[1] + 1)
        if self.conflict(center):
            return False

        self.center = center
        return True

    #绘制一个方块
    def draw(self):
        for cube in self.get_all_gridpos():#一个方块一个方块地画，cube[1]里存的是横坐标，cube[0]里存的是纵坐标
            pygame.draw.rect(screen, self.color,
                             (cube[1] * GRID_WIDTH, cube[0] * GRID_WIDTH,
                              GRID_WIDTH, GRID_WIDTH))
            pygame.draw.rect(screen, WHITE,
                             (cube[1] * GRID_WIDTH, cube[0] * GRID_WIDTH,
                              GRID_WIDTH, GRID_WIDTH),
                             1)

    # 在特定的位置绘制下一方块
    def drawNext(self):
        Cube = self.get_all_gridpos((0,0))
        for cube in Cube:
            #print(cube[0], 'cube')
            pygame.draw.rect(screen, self.color,
                             (cube[1] * GRID_WIDTH+WIDTH+100, cube[0] * GRID_WIDTH+70,
                              GRID_WIDTH, GRID_WIDTH))
            pygame.draw.rect(screen, WHITE,
                             (cube[1] * GRID_WIDTH+WIDTH+100, cube[0] * GRID_WIDTH+70,
                              GRID_WIDTH, GRID_WIDTH),1)

        return self.shape

# 这些是全局参数，参数指结束动画的初始位置和xy方向的速度
# 显示框弹动速度
x, y = 10., 10.
speed_x, speed_y = 133., 170.
# ai对象
rw = None
# 是否ai模式(贪心）
ai = False
#是否ai深搜+减枝
d_ai = False
#第一层临时占用的位置
Dep1 = []
#路径
path = []
# 玩家操作
class HouseWorker():

    # 开始游戏
    def start(self):#初始化
        global gameover
        global live_cube
        global new_cube
        global score
        global screen_color_matrix
        gameover = False
        live_cube = Brick()
        new_cube = Brick()
        score = 0
        screen_color_matrix = [[None] * GRID_NUM_WIDTH for i in range(GRID_NUM_HEIGHT)]


    # 暂停操作
    def pause(self):
        global pause
        if pause:
            pause = False
        else :
            pause = True

    def sucessAD(self):
        global success
        if success:
            success = False
        else:
            success = True

    # 当暂停时，暂停就是改变pause的值
    def whenPause(self):
        # 暂停动画
        global pause_count
        global score
        global live_cube
        global level
        global screen_color_matrix
        global colorBool
        global dead
        global success
        pause_count += 1
        if pause_count % FPS > 10 and pause_count % FPS < 20:
            w.drawAll()
        else:
            w.showPause()

        pygame.display.update()
        for event in pygame.event.get():#对键盘响应
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:#停止暂停
                    hw.pause()
                elif event.key == pygame.K_ESCAPE:#退出游戏
                    hw.pause()
                    w.writeHeightScore()
                    # 退出pygame
                    pygame.quit()
                    # 退出系统
                    sys.exit()
                #   重新开始
                elif event.key == pygame.K_r:#重新开始
                    w.writeHeightScore()
                    hw.pause()
                    score = 0
                    live_cube = Brick()
                    level = 1
                    dead = False
                    screen_color_matrix = [[None] * GRID_NUM_WIDTH for i in range(GRID_NUM_HEIGHT)]
                elif event.key == pygame.K_s:
                    if success == True:
                        success = False
                elif event.key == pygame.K_c: # ad广告板闪动的彩蛋
                    if colorBool :
                        colorBool = False
                    else:
                        colorBool = True
                else:
                    pass

    # 当正常时
    def whenNormal(self):
        global score
        global live_cube
        global level
        global screen_color_matrix
        global gameover
        global running
        global counter
        global new_cube
        global colorBool
        global dead
        global ai
        global d_ai
        global FPS
        # 正常运行时
        for event in pygame.event.get():#按键操作
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and pause == False:
                if gameover:
                    hw.start()
                    break
                if event.key == pygame.K_LEFT:
                    live_cube.left()
                elif event.key == pygame.K_RIGHT:
                    live_cube.right()
                elif event.key == pygame.K_DOWN:
                    live_cube.down()
                elif event.key == pygame.K_UP:
                    live_cube.rotate()
                elif event.key == pygame.K_SPACE:# 按空格则是快速下落，一直执行while循环直到不能再下落
                    while live_cube.down() == True:
                        pass
                elif event.key == pygame.K_ESCAPE:
                    w.writeHeightScore()
                    # 退出pygame
                    pygame.quit()
                    # 退出系统
                    sys.exit()
                #   重新开始
                elif event.key == pygame.K_r:
                    w.writeHeightScore()
                    score = 0
                    live_cube = Brick()
                    new_cube = Brick()
                    colorBool = True
                    dead = False
                    level = 1
                    screen_color_matrix = [[None] * GRID_NUM_WIDTH for i in range(GRID_NUM_HEIGHT)]
                elif event.key == pygame.K_c:
                    if colorBool :
                        colorBool = False
                    else:
                        colorBool = True
                elif event.key == pygame.K_p:
                    hw.pause()
                elif event.key == pygame.K_a:
                    if ai:
                        ai = False
                    else:
                        ai = True
                    if d_ai:
                        d_ai = False
                elif event.key == pygame.K_d:
                    if d_ai:
                        d_ai = False
                    else:
                        d_ai = True
                    if ai:
                        ai = False
        #贪心
        if live_cube and ai == True:
            rw = RobotWorker([2, 7], live_cube.shape, live_cube.dir, live_cube.color , screen_color_matrix)
            bestPoint, diff =  rw.mainProcess()
            if diff>0:
                live_cube.dir = bestPoint['station']
                live_cube.center = bestPoint['center']
                w.drawAll()
                pygame.display.update()


        #深搜两步
        if live_cube and d_ai == True:
            rw = RobotWorker2([2, 7], live_cube.shape, live_cube.dir, live_cube.color, screen_color_matrix)
            bestPoint = rw.mainProcess()
            live_cube.dir = bestPoint['station']
            live_cube.center = bestPoint['center']
            w.drawAll()
            pygame.display.update()


            # level 是为了方便游戏的难度，level 越高 FPS // level 的值越小
            # 这样屏幕刷新的就越快，难度就越大
        if ai is not True and d_ai is not True:
            flag = counter % (FPS // level) == 0
            FPS = 30
        else :
            flag = True
            FPS = 3000

        # 判断是否结束函数和执行down动作
        if gameover is False and flag :
            if live_cube.down() == False:
                for cube in live_cube.get_all_gridpos():
                    screen_color_matrix[cube[0]][cube[1]] = live_cube.color
                live_cube = new_cube
                new_cube = Brick()
                # 这里游戏结束
                if live_cube.conflict(live_cube.center):
                    w.writeHeightScore()
                    dead = True
                    gameover = True
                    colorBool = False

            # 消除满行
            w.remove_full_line()

        # 计时作用
        counter += 1

        if not dead:
            w.drawAll()
            pygame.display.update()

    def whenSucess(self):
        global success
        global score
        global live_cube
        global new_cube
        global level
        global screen_color_matrix
        global colorBool
        global dead
        global speed_x
        global speed_y
        global SCREEN_WIDTH
        global x
        global y

        w.drawAll()
        w.showAD(u'恭喜你', u'成功了')

        #pygame.display.update()
        for event in pygame.event.get():  # 对键盘响应
            if event.type == pygame.KEYDOWN:
                if success:
                    success = False
                    hw.start()
                    break
            elif event.type == pygame.K_r:
                w.writeHeightScore()
                score = 0
                live_cube = Brick()
                new_cube = Brick()
                colorBool = True
                dead = False
                level = 1
                screen_color_matrix = [[None] * GRID_NUM_WIDTH for i in range(GRID_NUM_HEIGHT)]
            elif event.type == pygame.K_ESCAPE:
                # 退出pygame
                pygame.quit()
                # 退出系统
                sys.exit()
            else:
                pass
    # 当gameover时
    def whenGameOver(self):
        global score
        global live_cube
        global new_cube
        global level
        global screen_color_matrix
        global colorBool
        global dead
        global speed_x
        global speed_y
        global SCREEN_WIDTH
        global x
        global y

        w.drawAll()
        w.showAD(u'游戏结束', u'你失败了')


        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if gameover and dead:
                    dead = False
                    colorBool = True
                    hw.start()
                    break
                if event.key == pygame.K_ESCAPE:
                    # 退出pygame
                    pygame.quit()
                    # 退出系统
                    sys.exit()
                #   重新开始
                elif event.key == pygame.K_r:
                    w.writeHeightScore()
                    score = 0
                    live_cube = Brick()
                    new_cube = Brick()
                    level = 1
                    colorBool = True
                    dead = False
                    screen_color_matrix = [[None] * GRID_NUM_WIDTH for i in range(GRID_NUM_HEIGHT)]
                elif event.key == pygame.K_c:
                    if colorBool:
                        colorBool = False
                    else:
                        colorBool = True
                else:
                    pass

# AI操作
# 基于Pierre Dellacherie算法
class RobotWorker():
    SHAPES = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']
    I = [[(0, -1), (0, 0), (0, 1), (0, 2)],
         [(-1, 0), (0, 0), (1, 0), (2, 0)]]
    J = [[(-2, 0), (-1, 0), (0, 0), (0, -1)],
         [(-1, 0), (0, 0), (0, 1), (0, 2)],
         [(0, 1), (0, 0), (1, 0), (2, 0)],
         [(0, -2), (0, -1), (0, 0), (1, 0)]]
    L = [[(-2, 0), (-1, 0), (0, 0), (0, 1)],
         [(1, 0), (0, 0), (0, 1), (0, 2)],
         [(0, -1), (0, 0), (1, 0), (2, 0)],
         [(0, -2), (0, -1), (0, 0), (-1, 0)]]
    O = [[(0, 0), (0, 1), (1, 0), (1, 1)]]
    S = [[(-1, 0), (0, 0), (0, 1), (1, 1)],
         [(1, -1), (1, 0), (0, 0), (0, 1)]]
    T = [[(0, -1), (0, 0), (0, 1), (-1, 0)],
         [(-1, 0), (0, 0), (1, 0), (0, 1)],
         [(0, -1), (0, 0), (0, 1), (1, 0)],
         [(-1, 0), (0, 0), (1, 0), (0, -1)]]
    Z = [[(0, -1), (0, 0), (1, 0), (1, 1)],
         [(-1, 0), (0, 0), (0, -1), (1, -1)]]

    In = [[[0, 4]], [[-1, 1], [0, 1], [1, 2]]]  # [x, y] x为初始行号，y为该行的数目
    Jn = [[[-2, 1], [-1, 1], [0, 2]], [[-1, 1], [0, 3]], [[0, 2], [1, 1], [2, 1]], [[0, 3], [1, 1]]]
    Ln = [[[-2, 1], [-1, 1], [0, 2]], [[0, 3], [1, 1]], [[0, 2], [1, 1], [2, 1]], [[-1, 1], [0, 3]]]
    On = [[[0, 2], [1, 2]]]
    Sn = [[[-1, 1], [0, 2], [1, 1]], [[0, 2], [1, 2]]]
    Tn = [[[-1, 1], [0, 3]], [[-1, 1], [0, 2], [1, 1]], [[0, 3], [1, 1]], [[-1, 1], [0, 2], [1, 1]]]
    Zn = [[[0, 2], [1, 2]], [[-1, 1], [0, 2], [1, 1]]]

    SHAPES_WITH_DIR = {
        'I': I, 'J': J, 'L': L, 'O': O, 'S': S, 'T': T, 'Z': Z
    }

    SHAPES_WITH_DIRn = {
        'I': In, 'J': Jn, 'L': Ln, 'O': On, 'S': Sn, 'T': Tn, 'Z': Zn
    }

    def __init__(self,center,shape,station,color,matrix):
        self.center = center
        self.shape = shape
        self.station = station
        self.color = color
        self.matrix = matrix

    def get_all_gridpos(self, center,shape,dir):#获取方块的位置
        curr_shape = self.SHAPES_WITH_DIR[shape][dir]

        return [(cube[0] + center[0], cube[1] + center[1])
                for cube in curr_shape]

    def conflict(self, center,matrix,shape,dir):
        for cube in self.get_all_gridpos(center,shape,dir):
            # 超出屏幕之外，说明不合法
            if cube[0] < 0 or cube[1] < 0 or cube[0] >= GRID_NUM_HEIGHT or  cube[1] >= GRID_NUM_WIDTH:
                return True

            screen_color_matrix = self.copyTheMatrix( matrix )
            # 不为None，说明之前已经有小方块存在了，也不合法
            if screen_color_matrix[cube[0]][cube[1]] is not None:
                return True

        return False

    #复制矩阵
    def copyTheMatrix(self,screen_color_matrix):
        newMatrix = [[None] * GRID_NUM_WIDTH for i in range(GRID_NUM_HEIGHT)]
        for i in range( len( screen_color_matrix ) ):
            for j in range( len( screen_color_matrix[i] ) ):
                newMatrix[i][j] = screen_color_matrix[i][j]

        return newMatrix

    #查询指定行气泡的数量
    def checkBubble(self, rown):
        num = 0
        screen_color_matrix = self.copyTheMatrix(self.matrix)
        for i in range(0, GRID_NUM_WIDTH):
            if screen_color_matrix[rown][i] == None:
                num = num + 1
        return num

    #积分函数
    def caculateScores(self, point, shape):
        row0 = point['center'][0]
        dirn = point['station']
        shapen = self.SHAPES_WITH_DIRn[shape]
        '''
        print(shapen, 'shapen')
        print(shape, 'shape')
        print(len(shapen), 'len')
        print(dirn, 'dirn')
        print(shapen[dirn][0][0], 's')
        '''
        line = 0
        for i in range(0, len(shapen[dirn])):
            rown = shapen[dirn][i][0]
            rown = rown + row0

            if self.checkBubble(rown) == shapen[dirn][i][1]:
                line = line + 1
        if line == 0:
            return 0
        else:
            return 1 + line*(line-1)

    #获取当前所有可以放置的位置（遍历出当前位置可以放，但下方的位置不能放）
    def getAllPossiblePos(self,thisShape = 'Z'):
        theMatrix = self.matrix
        theStationNum = len(self.SHAPES_WITH_DIR[thisShape])
        theResult = []#存放所有可以放的中心点和状态
        for k in range(theStationNum):
            for j in range(len(theMatrix[1])):
                for i in range(len(theMatrix) - 1):
                    if self.conflict([i + 1, j], theMatrix, thisShape, k) == True and self.conflict([i, j], theMatrix,
                                                                                                thisShape, k) == False:
                        if {"center": [i, j], "station": k} not in theResult:
                            theResult.append({"center": [i, j], "station": k})

        return theResult

    # 获取方块海拔（1）
    def getLandingHeight(self,center):
        return GRID_NUM_HEIGHT-1-center[0]

    #消除的行数*方块自身被消格数（2）
    def getErodedPieceCellsMetric(self,center,station):
        theNewMatrix = self.getNewMatrix(center,station)
        lines = 0
        usefulBlocks = 0
        theAllPos = self.get_all_gridpos(center,self.shape,station)
        for i in range(len(theNewMatrix)-1,0,-1):
            count = 0
            for j in range(len(theNewMatrix[1])):#遍历当前行
                if theNewMatrix[i][j] is not None:
                    count += 1
                else:
                    break
            # 满一行
            if count == GRID_NUM_WIDTH:
                lines +=1
                for k in range(len(theNewMatrix[1])):#消除行中是否有该方块
                    if [i,k] in theAllPos:
                        usefulBlocks +=1
            # 整行未填充，则跳出循环
            if count == 0:
                break
        return lines*usefulBlocks

    # 把可能的坐标位置放进去颜色矩阵，形成新的颜色矩阵
    def getNewMatrix(self,center,station):
        theNewMatrix = self.copyTheMatrix(self.matrix)
        theAllPos = self.get_all_gridpos(center,self.shape,station)
        for cube in theAllPos:
            theNewMatrix[cube[0]][cube[1]] = self.color
        return theNewMatrix

    # 获取行变换数
    def getBoardRowTransitions(self,theNewmatrix):
        transition = 0
        for i in range( len(theNewmatrix)-1 , 0 , -1 ):
           # count = 0
            for j in range( len(theNewmatrix[1])-1 ):
                '''
                if theNewmatrix[i][j] is not None :
                    count += 1
                '''
                if theNewmatrix[i][j] == None and theNewmatrix[i][j+1] != None:
                    transition += 1
                if theNewmatrix[i][j] != None and theNewmatrix[i][j+1] == None:
                    transition += 1
        return transition

    # 获取列变换数
    def getBoardColTransitions(self,theNewmatrix):
        transition = 0
        for j in range( len(theNewmatrix[1]) ):
            for i in range( len(theNewmatrix)-1,1,-1 ):
                if theNewmatrix[i][j] == None and theNewmatrix[i-1][j] != None:
                    transition += 1
                if theNewmatrix[i][j] != None and theNewmatrix[i-1][j] == None:
                    transition += 1
        return transition

    #获取空洞方格之和
    def getBoardBuriedHoles(self,theNewmatrix):
        holes = 0
        for j in range(len( theNewmatrix[1] )):#按列遍历
            colHoles = None
            for i in range( len( theNewmatrix ) ):
                if colHoles == None and theNewmatrix[i][j] != None:
                    colHoles = 0

                if colHoles != None and theNewmatrix[i][j] == None:
                    colHoles += 1
            if colHoles is not None:
                holes += colHoles
        return holes

    #获取井深分数
    def getBoardWells(self,theNewmatrix):
        sum_n = [0,1,3,6,10,15,21,28,36,45,55]#根据井深计算的分数数组
        wells = 0
        sum = 0

        for j in range( len(theNewmatrix[1]) ):#按列遍历
            for i in range( len(theNewmatrix) ):
                if theNewmatrix[i][j] == None:#遇到气泡，观察气泡两边
                    if (j-1<0 or theNewmatrix[i][j-1] != None) and (j+1 >= 15 or theNewmatrix[i][j+1] != None):
                        wells += 1
                    else:
                        sum += sum_n[wells]
                        wells = 0
        return sum


    def getPrioritySelection(self,point):
        tarStation = point['station']
        nowStation = self.station
        #平移的距离
        colNum = abs(7 - point['center'][1] )
        if tarStation >= nowStation:
            changeTimes = tarStation - nowStation#变换次数
        else :
            changeTimes = len(self.SHAPES_WITH_DIR[self.shape]) - nowStation + tarStation

        result = colNum*100 + changeTimes
        if point['center'][1] <=7 :
            result += 10
        return result


    def evaluateFunction(self,point):
        newMatrix = self.getNewMatrix( point['center'],point['station'] )
        lh = self.getLandingHeight( point['center'] )
        epcm = self.getErodedPieceCellsMetric(point['center'],point['station'])
        brt = self.getBoardRowTransitions(newMatrix)
        bct = self.getBoardColTransitions(newMatrix)
        bbh = self.getBoardBuriedHoles(newMatrix)
        bw = self.getBoardWells(newMatrix)

        # 两个计算分数的式子，前者更优，后者是PD算法的原始设计
        score = -45*lh + 34*epcm - 32*brt - 98*bct - 79* bbh -34*bw
        # score = -1*lh + epcm - brt - bct - 4*bbh - bw
        return score

    def mainProcess(self):
        global path
        pos = self.getAllPossiblePos(self.shape)
        bestScore = -999999
        bestPoint = None
        bestScoren = -999999
        bestScorenn = -99999
        #print(heightScore, 'heightScore')
        #print(score, 'scorenow')
        diff = heightScore - score
        if diff == 0:
            print(path)
            print(len(path))
            hw.sucessAD()

            #hw.whenSucess()
        else:
            if diff > 13:
                for point in pos:
                    theScore = self.evaluateFunction(point)
                    bestScoren = self.caculateScores(point, self.shape)

                    if theScore > bestScore:
                        bestScore = theScore
                        bestPoint = point
                        bestScorenn = bestScoren

                    elif theScore == bestScore:
                        if self.getPrioritySelection(point) < self.getPrioritySelection(bestPoint):
                            bestScore = theScore
                            bestPoint = point
                            bestScorenn = bestScoren
            else:
                for point in pos:
                    theScore = self.evaluateFunction(point)
                    bestScoren = self.caculateScores(point, self.shape)
                    bestScorenn = 0
                    print(bestScoren)
                    print(diff)
                    if bestScoren <= diff:
                        if theScore > bestScore:
                            bestScore = theScore
                            bestPoint = point
                            bestScorenn = bestScoren
                            #bestScoren = self.caculateScores(point, self.shape)

                        elif theScore == bestScore:
                            if self.getPrioritySelection(point) < self.getPrioritySelection(bestPoint):
                                bestScore = theScore
                                bestPoint = point
                                bestScorenn = bestScoren

            #print(bestScorenn, 'bestScorenn')
            path.append([bestPoint, self.shape])
        return bestPoint, diff


'''
class RobotWorker2():

    SHAPES = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']
    I = [[(0, -1), (0, 0), (0, 1), (0, 2)],
         [(-1, 0), (0, 0), (1, 0), (2, 0)]]
    J = [[(-2, 0), (-1, 0), (0, 0), (0, -1)],
         [(-1, 0), (0, 0), (0, 1), (0, 2)],
         [(0, 1), (0, 0), (1, 0), (2, 0)],
         [(0, -2), (0, -1), (0, 0), (1, 0)]]
    L = [[(-2, 0), (-1, 0), (0, 0), (0, 1)],
         [(1, 0), (0, 0), (0, 1), (0, 2)],
         [(0, -1), (0, 0), (1, 0), (2, 0)],
         [(0, -2), (0, -1), (0, 0), (-1, 0)]]
    O = [[(0, 0), (0, 1), (1, 0), (1, 1)]]
    S = [[(-1, 0), (0, 0), (0, 1), (1, 1)],
         [(1, -1), (1, 0), (0, 0), (0, 1)]]
    T = [[(0, -1), (0, 0), (0, 1), (-1, 0)],
         [(-1, 0), (0, 0), (1, 0), (0, 1)],
         [(0, -1), (0, 0), (0, 1), (1, 0)],
         [(-1, 0), (0, 0), (1, 0), (0, -1)]]
    Z = [[(0, -1), (0, 0), (1, 0), (1, 1)],
         [(-1, 0), (0, 0), (0, -1), (1, -1)]]

    SHAPES_WITH_DIR = {
        'I': I, 'J': J, 'L': L, 'O': O, 'S': S, 'T': T, 'Z': Z
    }
    def __init__(self,center,shape,station,color,matrix):
        self.center = center
        self.shape = shape
        self.station = station
        self.color = color
        self.matrix = matrix

    def get_all_gridpos(self, center,shape,dir):#获取方块的位置
        curr_shape = self.SHAPES_WITH_DIR[shape][dir]

        return [(cube[0] + center[0], cube[1] + center[1])
                for cube in curr_shape]

    def conflict(self, center,matrix,shape,dir,dep1):
        for cube in self.get_all_gridpos(center,shape,dir):
            # 超出屏幕之外，说明不合法
            if cube[0] < 0 or cube[1] < 0 or cube[0] >= GRID_NUM_HEIGHT or  cube[1] >= GRID_NUM_WIDTH:
                return True

            screen_color_matrix = self.copyTheMatrix( matrix )
            # 不为None，说明之前已经有小方块存在了，也不合法
            if screen_color_matrix[cube[0]][cube[1]] is not None:
                return True

            if cube in dep1 and dep1!=[]:
                return True
            #print(cube, cube[0])
        return False

    #复制矩阵
    def copyTheMatrix(self,screen_color_matrix):
        newMatrix = [[None] * GRID_NUM_WIDTH for i in range(GRID_NUM_HEIGHT)]
        for i in range( len( screen_color_matrix ) ):
            for j in range( len( screen_color_matrix[i] ) ):
                newMatrix[i][j] = screen_color_matrix[i][j]

        return newMatrix

    #获取当前所有可以放置的位置（遍历出当前位置可以放，但下方的位置不能放）
    def getAllPossiblePos(self,thisShape = 'Z'):
        theMatrix = self.matrix
        theStationNum = len(self.SHAPES_WITH_DIR[thisShape])
        theResult = []#存放所有可以放的中心点和状态
        Dep1 = []#存放占用的位置
        for k in range(theStationNum):
            for j in range(len(theMatrix[1])):
                for i in range(len(theMatrix) - 1):
                    if self.conflict([i + 1, j], theMatrix, thisShape, k, []) == True and self.conflict([i, j], theMatrix,
                                                                                                thisShape, k, []) == False:
                        if {"center": [i, j], "station": k} not in theResult:
                            theResult.append({"center": [i, j], "station": k})
                            Dep1.append(self.get_all_gridpos([i,j],thisShape,k))

        return theResult, Dep1

    def getAllPossiblePos2(self, thisShape='Z', dep1=[]):
        theMatrix = self.matrix
        theStationNum = len(self.SHAPES_WITH_DIR[thisShape])
        theResult = []  # 存放所有可以放的中心点和状态
        Dep1 = []  # 存放占用的位置
        for k in range(theStationNum):
            for j in range(len(theMatrix[1])):
                for i in range(len(theMatrix) - 1):
                    if self.conflict([i + 1, j], theMatrix, thisShape, k, dep1) == True and self.conflict([i, j],
                                                                                                        theMatrix,
                                                                                                        thisShape, k,
                                                                                                        dep1) == False:
                        if {"center": [i, j], "station": k} not in theResult:
                            theResult.append({"center": [i, j], "station": k})

        return theResult

    # 获取方块海拔（1）
    def getLandingHeight(self,center):
        return GRID_NUM_HEIGHT-1-center[0]

    #消除的行数*方块自身被消格数（2）
    def getErodedPieceCellsMetric(self,center,station):
        theNewMatrix = self.getNewMatrix(center,station)
        lines = 0
        usefulBlocks = 0
        theAllPos = self.get_all_gridpos(center,self.shape,station)
        for i in range(len(theNewMatrix)-1,0,-1):
            count = 0
            for j in range(len(theNewMatrix[1])):#遍历当前行
                if theNewMatrix[i][j] is not None:
                    count += 1
                else:
                    break
            # 满一行
            if count == GRID_NUM_WIDTH:
                lines +=1
                for k in range(len(theNewMatrix[1])):#消除行中是否有该方块
                    if [i,k] in theAllPos:
                        usefulBlocks +=1
            # 整行未填充，则跳出循环
            if count == 0:
                break
        return lines*usefulBlocks

    # 把可能的坐标位置放进去颜色矩阵，形成新的颜色矩阵
    def getNewMatrix(self,center,station):
        theNewMatrix = self.copyTheMatrix(self.matrix)
        theAllPos = self.get_all_gridpos(center,self.shape,station)
        for cube in theAllPos:
            theNewMatrix[cube[0]][cube[1]] = self.color
        return theNewMatrix

    # 获取行变换数
    def getBoardRowTransitions(self,theNewmatrix):
        transition = 0
        for i in range( len(theNewmatrix)-1 , 0 , -1 ):
           # count = 0
            for j in range( len(theNewmatrix[1])-1 ):
                
                if theNewmatrix[i][j] is not None :
                    count += 1
                
                if theNewmatrix[i][j] == None and theNewmatrix[i][j+1] != None:
                    transition += 1
                if theNewmatrix[i][j] != None and theNewmatrix[i][j+1] == None:
                    transition += 1
        return transition

    # 获取列变换数
    def getBoardColTransitions(self,theNewmatrix):
        transition = 0
        for j in range( len(theNewmatrix[1]) ):
            for i in range( len(theNewmatrix)-1,1,-1 ):
                if theNewmatrix[i][j] == None and theNewmatrix[i-1][j] != None:
                    transition += 1
                if theNewmatrix[i][j] != None and theNewmatrix[i-1][j] == None:
                    transition += 1
        return transition

    #获取空洞方格之和
    def getBoardBuriedHoles(self,theNewmatrix):
        holes = 0
        for j in range(len( theNewmatrix[1] )):#按列遍历
            colHoles = None
            for i in range( len( theNewmatrix ) ):
                if colHoles == None and theNewmatrix[i][j] != None:
                    colHoles = 0

                if colHoles != None and theNewmatrix[i][j] == None:
                    colHoles += 1
            if colHoles is not None:
                holes += colHoles
        return holes

    #获取井深分数
    def getBoardWells(self,theNewmatrix):
        sum_n = [0,1,3,6,10,15,21,28,36,45,55]#根据井深计算的分数数组
        wells = 0
        sum = 0

        for j in range( len(theNewmatrix[1]) ):#按列遍历
            for i in range( len(theNewmatrix) ):
                if theNewmatrix[i][j] == None:#遇到气泡，观察气泡两边
                    if (j-1<0 or theNewmatrix[i][j-1] != None) and (j+1 >= 15 or theNewmatrix[i][j+1] != None):
                        wells += 1
                    else:
                        sum += sum_n[wells]
                        wells = 0
        return sum


    def getPrioritySelection(self,point):
        tarStation = point['station']
        nowStation = self.station
        #平移的距离
        colNum = abs(7 - point['center'][1] )
        if tarStation >= nowStation:
            changeTimes = tarStation - nowStation#变换次数
        else :
            changeTimes = len(self.SHAPES_WITH_DIR[self.shape]) - nowStation + tarStation

        result = colNum*100 + changeTimes
        if point['center'][1] <=7 :
            result += 10
        return result


    def evaluateFunction(self,point):
        newMatrix = self.getNewMatrix( point['center'],point['station'] )
        lh = self.getLandingHeight( point['center'] )
        epcm = self.getErodedPieceCellsMetric(point['center'],point['station'])
        brt = self.getBoardRowTransitions(newMatrix)
        bct = self.getBoardColTransitions(newMatrix)
        bbh = self.getBoardBuriedHoles(newMatrix)
        bw = self.getBoardWells(newMatrix)

        # 两个计算分数的式子，前者更优，后者是PD算法的原始设计
        score = -45*lh + 34*epcm - 32*brt - 98*bct - 79* bbh -34*bw
        # score = -1*lh + epcm - brt - bct - 4*bbh - bw
        return score

    def mainProcess(self):

        pos, Dep1 = self.getAllPossiblePos(self.shape)
        print(Dep1)

        #print(shape2, pos2)
        bestScore = -999999
        bestPoint = None
        theScore = []
        for point in pos:
            theScore = self.evaluateFunction(point)
            #if(bestScore < )
            shape2 = w.drawNextBrick()
            pos2 = self.getAllPossiblePos2(shape2)
            for point2 in pos2:
                theScored = self.evaluateFunction(point2) + theScore
                if theScored > bestScore:
                    bestScore = theScored
                    bestPoint = point
                elif theScored == bestScore:
                    if self.getPrioritySelection(point) < self.getPrioritySelection(bestPoint):
                        bestScore = theScored
                        bestPoint = point





                
            if theScore > bestScore:
                bestScore = theScore
                bestPoint = point
            elif theScore == bestScore:
                if self.getPrioritySelection(point) < self.getPrioritySelection(bestPoint):
                    bestScore = theScore
                    bestPoint = point
                

        return bestPoint
'''

w =  Wall()
hw = HouseWorker()
a = w.drawNextBrick()
path = []
while running:
    clock.tick(FPS)#一般在电脑上每秒绘制FPS次
    # 暂停时的事件循环

    '''
    b = w.drawNextBrick()
    if b != a:
       # print(b)
        a = b
        '''

    if success == True:
        hw.whenSucess()
        continue
    if pause == True:
        hw.whenPause()
        continue
    if dead:
        hw.whenGameOver()
        continue
    # 正常时的事件循环
    hw.whenNormal()