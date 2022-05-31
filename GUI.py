from tkinter import *
import tkinter.font

class GUI:
    def __init__(self, board_size, black_info, white_info):
        def get_step_tuple(step_size):
            left_pix = self.board_wh % step_size

            step_list = list()
            temp = step_size
            while temp < self.board_wh:
                if left_pix > 0:
                    temp += 1

                step_list.append(temp)

                temp += step_size
                left_pix -= 1
            return tuple(step_list)

        def init_window(root):
            root.title('board window')
            root.geometry(f"{self.wd['width']}x{self.wd['height']}+100+100")
            root.resizable(False, False)

        def init_board(canvas, step_tuple):
            canvas.create_rectangle(
                self.bd['x'], self.bd['y'],
                self.bd['x']+self.board_wh, self.bd['y']+self.board_wh
            )

            #draw row, col=============
            for step in step_tuple:
                canvas.create_line(    #row
                    self.bd['x'], self.bd['y']+step,
                    self.bd['x']+self.board_wh, self.bd['y']+step
                )
                canvas.create_line(    #col
                    self.bd['x']+step, self.bd['y'],
                    self.bd['x']+step, self.bd['y']+self.board_wh
                )
            #End=======================

            #draw cross dot============
            for step_y in step_tuple:
                for step_x in step_tuple:
                    canvas.create_oval(
                        self.bd['x'] - 3 + step_x, self.bd['y'] - 3 + step_y,
                        self.bd['x'] + 3 + step_x, self.bd['y'] + 3 + step_y
                    )
            #End=======================

        def init_state(root, black_info, white_info):
            def get_player_text(palyer_code):
                if palyer_code == 1:
                    return 'RANDOM_CHOICE'
                elif palyer_code == 2:
                    return 'α_O'
                return 'USER'

            black_text = '● ' + get_player_text(black_info)
            white_text = get_player_text(white_info) + ' ○'
            
            
            stone_ft = tkinter.font.Font(size=20)

            black_stone_txt = Label(root, text=black_text, font=stone_ft)
            white_stone_txt = Label(root, text=white_text, font=stone_ft, state='disable')

            black_stone_txt.place(x=self.interval, y=15)
            white_stone_txt.place(x=self.wd['width']-self.interval, y=15, anchor='ne')


            predict_ft = tkinter.font.Font(size=15)
            black_vnn_txt = Label(root, text='VNN: ', font=predict_ft)
            white_vnn_txt = Label(root, text='VNN: ', font=predict_ft, state='disable')

            black_vnn_txt.place(x=self.interval+20, y=70)
            white_vnn_txt.place(x=self.wd['width']-self.interval-20, y=70, anchor='ne')

        def wheon_move_mouse(event):   #포석 위치 체크
            def get_is_inner_cross(x, y):
                x_bd_in_TF = x > self.bd['x'] - TOLERANCE and x < self.bd['x'] + self.board_wh + TOLERANCE
                y_bd_in_TF = y > self.bd['y'] - TOLERANCE and y < self.bd['y'] + self.board_wh + TOLERANCE

                if x_bd_in_TF and y_bd_in_TF:
                    x_cr_in_TF = (x - self.bd['x']) % self.board_step_size
                    x_cr_in_TF = x_cr_in_TF > (self.board_step_size - TOLERANCE) or x_cr_in_TF < TOLERANCE

                    y_cr_in_TF = (y - self.bd['y']) % self.board_step_size
                    y_cr_in_TF = y_cr_in_TF > (self.board_step_size - TOLERANCE) or y_cr_in_TF < TOLERANCE

                    return x_cr_in_TF and y_cr_in_TF
                return False

            def get_close_value(value, put_loc_tup):
                for step in put_loc_tup:
                    if abs(step - value) <= TOLERANCE:
                        return step

            def show_visual_stone(x, y):
                if not x:
                    x = self.wd['width']
                    y = 0
                
                self.board.moveto(self.visual_stone, x, y)

            def get_close_value_idx(value, put_loc_tup):
                for idx, step in enumerate(put_loc_tup):
                    if step == value:
                        return idx
                return idx

            TOLERANCE = 20  #포석 인정 허용 범위
            put_loc_tup = tuple([0] + list(self.step_tuple) + [self.step_tuple[-1] + self.board_step_size])
            
            x, y = event.x, event.y


            if get_is_inner_cross(x, y):
                b_x, b_y = x - self.bd['x'], y - self.bd['y']
                loc_x = get_close_value(b_x, put_loc_tup)
                loc_y = get_close_value(b_y, put_loc_tup)
                
                half_st = self.stone_size // 2
                show_visual_stone(loc_x+self.bd['x']-half_st, loc_y+self.bd['y']-half_st)

                loc_x_idx = get_close_value_idx(loc_x, put_loc_tup)
                loc_y_idx = get_close_value_idx(loc_y, put_loc_tup)
                self.board.itemconfig(self.loc_text, text=f'stone location: ({loc_x_idx}, {loc_y_idx})')
            else:
                show_visual_stone(None, None)


        self.board_size = board_size
        self.black_info, self.white_info = black_info, white_info


        self.interval = 30
        self.wd = {'width': 700, 'height': 800} #wd: `window`의 줌말
        
        self.board_step_size = (self.wd['width'] - self.interval * 2) // (self.board_size + 2)  #하나의 셀 크기
        self.stone_size = self.board_step_size // 1.25
        self.board_wh = self.board_step_size * self.board_size  #board size

        self.step_tuple = get_step_tuple(step_size=self.board_step_size)

        self.bd = {'x': 30 + self.board_step_size}   #bd: `board`의 줌말, 시작 x, y 좌표
        self.bd['y'] = self.wd['height'] - self.bd['x'] - self.board_wh


        self.root = Tk()
        init_window(self.root)

        self.board = Canvas(self.root, width=self.wd['width'], height=self.wd['height'])
        init_board(self.board, self.step_tuple)
        self.board.pack()

        init_state(self.root, self.black_info, self.white_info)

        self.visual_stone = self.board.create_oval( #visual stone 초기 위치
            self.wd['width'], 0, self.wd['width']+self.stone_size, self.stone_size, fill='black'
        )

        self.loc_text = self.board.create_text(   #stone location text
            self.bd['x']*2, self.wd['height']-self.interval,
            text='stone location: ',
            font=('', 12)
        )

        self.root.bind("<Motion>", wheon_move_mouse)
        

    def print_canvas(self):
        self.root.update()


if __name__ == '__main__':
    now_board = ((5, 5), (2, 2), (3, 3))

    
    gui = GUI(board_size=3, black_info=2, white_info=0)

    gui.print_canvas()
