import numpy as np

#常量使用全大写;类名首字母大写;函数名_变量名_全小写_下划线
N_ROWS = 1200
BOARD_SIZE = 6

##########################################################################################
#   MyBoard   
##########################################################################################

class MyBoard:
    
    def __init__(self, board, n_rows,turn=1):
        ''' 初始化 MyBorad 的一个 instance
        '''
        #变量:
        #   board:主棋盘 (array[6,6]) ;
        #   n_rows:下一个要落下的棋子在BOARD中的位置 (array[6])
        self.board=board.copy()
        self.n_rows = n_rows.copy()
        self.turn = turn
        
        self.add_score=0
        
        self.greedy=0
        self.best=None
        
    def copy(self):
        newboard = MyBoard(board = self.board, n_rows=self.n_rows, turn=self.turn)
        return newboard

    def switch(self,loc1,loc2):
        self.board[loc1],self.board[loc2]=self.board[loc2],self.board[loc1]

    @classmethod
    def first_turn(cls,board,is_first):
        mainboard=board[...,0:6]
        nan=np.array(['nan']*BOARD_SIZE**2).reshape(BOARD_SIZE,BOARD_SIZE)#6*6的'nan'列表

        if is_first:
            MyBoard.MAX_N_ROWS=np.array([N_ROWS]*6)
        else:
            MAX_N_ROWS=np.zeros(BOARD_SIZE,dtype=int)
            for i in range(BOARD_SIZE):
                j=N_ROWS
                while True:
                    j-=1
                    if board[i][j]!='nan':
                        MAX_N_ROWS[i]=j
                        break
            MyBoard.MAX_N_ROWS=MAX_N_ROWS

        MyBoard.BOARD=np.concatenate([board,nan],axis=1)
        return MyBoard(mainboard, np.array([BOARD_SIZE]*6))
    

    def erz(self,to_visit=None):
        '''单次擦除并下落,并返回一个score
        '''
        #first_erz询问是否是第一次擦除.由于第一次擦除前的图一定是无法擦除的,所以只需跑交换的2点,节约大量时间。
        #当first_erz 不为Flase时,传入的数据为to_visit
        
        #变量:
        #     棋盘:a 将要擦除:to_erz  得分:score
        a = self.board
        to_erz = np.zeros((BOARD_SIZE,BOARD_SIZE), dtype=int)
        
        if to_visit is None:

            def visit():#generator
                ''' 给定一个方格,判断其是否是三连的中心
                '''
                for i in range(BOARD_SIZE):
                    for j in range(BOARD_SIZE):
                        
                        if a[i,j]=='nan':
                            break
                        if to_erz[ i,j ] == 1:
                            continue
                        if ((0<j< BOARD_SIZE-1 and a[i,j-1]==a[i,j]==a[i,j+1]) or
                            (0<i< BOARD_SIZE-1 and a[i-1,j]==a[i,j]==a[i+1,j])):
                            yield (i,j)
            to_visit=visit()
        
        else:#to_visit
            if to_visit==[]:
                return 0

        #遍历坐标:coord (tuple) 颜色:color (str)
        add_score=0
        for coord in to_visit:
            color = a[coord]
            #用队列实现广度优先搜索
            #       指针:head (int); 连接的棋块:connected (List[Tuple]) ; 正在广搜的点 current (tuple) ;方向 d ;邻点(x,y)
            head = 0
            connected = [coord]
            to_erz[coord] = 1
            while head < len(connected):
                current = connected[head] 
                for d in ( (1,0),(-1,0),(0,1),(0,-1) ):
                    x,y = current[0]+d[0],current[1]+d[1]
                    if x<0 or y<0 or x>=BOARD_SIZE or y>=BOARD_SIZE:
                        continue
                    if a[x,y] == color and to_erz[x,y] == 0:
                        to_erz[x,y] = 1
                        connected.append( (x,y) )
                head += 1
            add_score += (len(connected)-2)**2
        #沉降方块
        col_erz = np.sum(to_erz, axis=1)
        for i in range(BOARD_SIZE):
            if col_erz[i] == 0:
                continue
            #分割点 u,v
            u,v,w = BOARD_SIZE-col_erz[i] , BOARD_SIZE , self.n_rows[i]
            a[i][0:u] = a[i][0:v][to_erz[i] == 0]
            a[i][u:v] = MyBoard.BOARD[i][w:w+v-u]
        self.n_rows += col_erz
        #当触底时
        return add_score


    #循环执行erz
    def eliminate(self,to_visit):
        add_score = self.erz(to_visit)
        self.add_score += add_score
        while add_score!=0:
            add_score = self.erz()
            self.add_score+=add_score

        self.turn = -self.turn
    def calculate(self):
        if self.greedy<1:
            self.row=[[0 for j in range(BOARD_SIZE)]for i in range(BOARD_SIZE-1)]
            self.col=[[0 for j in range(BOARD_SIZE-1)]for i in range(BOARD_SIZE)]
            value=0

            for j in range(BOARD_SIZE):
                for i in range(BOARD_SIZE-1):
                    
                    if self.board[i,j]==self.board[i+1,j]:
                        self.row[i][j] = self
                    
                    else:
                        to_visit=[]
                        newboard=self.copy()                        
                        newboard.switch((i,j),(i+1,j))
                        a=newboard.board
                            
                        if (i>1 and a[i-2,j]==a[i-1,j]==a[i,j] or
                            j>1 and a[i,j-2]==a[i,j-1]==a[i,j] or
                            0<j<BOARD_SIZE-1 and a[i,j-1]==a[i,j]==a[i,j+1] or
                            j<BOARD_SIZE-2   and a[i,j]==a[i,j+1]==a[i,j+2]):

                            to_visit.append((i,j))
                            
                        if (i<BOARD_SIZE-3   and a[i+1,j]==a[i+2,j]==a[i+3,j] or
                            j>1              and a[i+1,j-2]==a[i+1,j-1]==a[i+1,j] or
                            0<j<BOARD_SIZE-1 and a[i+1,j-1]==a[i+1,j]==a[i+1,j+1] or
                            j<BOARD_SIZE-2   and a[i+1,j]==a[i+1,j+1]==a[i+1,j+2]):
                            
                            to_visit.append((i+1,j))

                        newboard.eliminate(to_visit)
                        self.row[i][j]=newboard
                        score = newboard.add_score
                        if score > value:
                            value=score
                            self.best=((i,j),(i+1,j))

            for i in range(BOARD_SIZE):
                for j in range(BOARD_SIZE-1):
                    
                    if self.board[i,j]==self.board[i,j+1]:
                        self.col[i][j]=self
                        
                    else:
                        to_visit=[]
                        newboard=self.copy()
                        newboard.switch((i,j),(i,j+1))
                        a=newboard.board
                        
                        if (j>1 and a[i,j-2]==a[i,j-1]==a[i,j] or
                            i>1 and a[i-2,j]==a[i-1,j]==a[i,j] or
                            0<i<BOARD_SIZE-1 and a[i-1,j]==a[i,j]==a[i+1,j] or
                            i<BOARD_SIZE-2   and a[i,j]==a[i+1,j]==a[i+2,j]):
                            
                            to_visit.append((i,j))

                        if (j<BOARD_SIZE-3   and a[i,j+1]==a[i,j+2]==a[i,j+3] or
                            i>1              and a[i-2,j+1]==a[i-1,j+1]==a[i,j+1] or
                            0<i<BOARD_SIZE-1 and a[i-1,j+1]==a[i,j+1]==a[i+1,j+1] or
                            i<BOARD_SIZE-2   and a[i,j+1]==a[i+1,j+1]==a[i+2,j+1]):
                            
                            to_visit.append((i,j+1))

                        newboard.eliminate(to_visit)
                        self.col[i][j]=newboard
                        score = newboard.add_score
                        if score > value:
                            value=score
                            self.best=((i,j),(i,j+1))
            self.greedy=1
            
    def calculate_2(self,gap):
        self.calculate()
        if self.greedy<2:
            self.best2=None
            value=-65536
            for j in range(BOARD_SIZE):
                for i in range(BOARD_SIZE-1):
                    newboard=self.row[i][j]
                    newboard.calculate()
                    if newboard.best is None:
                        if newboard.add_score>gap:
                            self.best2=(i,j),(i+1,j)
                            self.greedy=2
                            return
                    else:
                        loc1,loc2=newboard.best
                        score=newboard.add_score - change(newboard,loc1,loc2).add_score
                        if score>value:
                            value=score
                            self.best2=(i,j),(i+1,j)

            for i in range(BOARD_SIZE):
                for j in range(BOARD_SIZE-1):
                    newboard=self.col[i][j]
                    newboard.calculate()
                    if newboard.best is None:
                        if newboard.add_score>gap:
                            self.best2=(i,j),(i,j+1)
                            self.greedy=2
                        return
                    else:
                        loc1,loc2=newboard.best
                        score=newboard.add_score - change(newboard,loc1,loc2).add_score
                        if score>value:
                            value=score
                            self.best2=(i,j),(i,j+1)
        self.greedy=2
            
##########################################################################################
# Plaser
##########################################################################################
def change(myboard,loc1,loc2):
    x1,y1=loc1
    x2,y2=loc2
    if y1==y2:
        return myboard.row[min(x1,x2)][y1]
    else:
        return myboard.col[x1][min(y1,y2)]
        
class Plaser:
    def __init__(self,is_First):
        self.is_first=is_First
        self.move_history=[]
        self.tmp_score=[]
        #self.used_time[0],self.used_time[1]分别代表我和对方所剩的时间
        #self.move_history可以查阅到操作序列

    def move(self,board,operations,scores,turn_number):
        self.tmp_score.append(scores[1]-scores[0])
        #初始化棋盘
        if turn_number==1:
            self.myboard=MyBoard.first_turn(board,self.is_first)
            self.myboard.calculate_2(self.tmp_score[-1])
        #跟上比赛的节奏
        if turn_number != 1:
            self.myboard=change(self.myboard,*self.move_history[-2])
            self.myboard.calculate()
            self.myboard=change(self.myboard,*self.move_history[-1])
            self.myboard.calculate_2(self.tmp_score[-1])
            if change(self.myboard,*self.move_history[-1]) is change(self.myboard,*self.move_history[-2]) and self.tmp_score[-1]>4:
                return self.myboard.best
        if turn_number == 100:
            return self.myboard.best
        else:
            return self.myboard.best2

