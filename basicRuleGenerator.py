from util import Util

import numpy as np



class Generator:
    def __init__(self, board_size: int):
        self.board_size = board_size

    def return_current_player(self, current_turn, black, white):
        '''
        * 현재 플레이어 순서[current_turn]를 토대로 흑 또는 백 플레이어 반환
        '''
        return white if current_turn else black

    def distribe_player(self, main_color, alpha_player, beta_player):
        '''
        [main_color]가 흑(0)이면, [alpha_player]가 흑을 잡고
        백(1)이면, [alpha_player]가 백을 잡는다
        '''
        black = self.return_current_player(current_turn=main_color, black=alpha_player, white=beta_player)
        white = self.return_current_player(current_turn=not main_color, black=alpha_player, white=beta_player)
        return black, white

    def get_consecutive_yx_list(self, consecutive_num: int, rotate_degree: int, limit_side_num: int):
        '''
        * [rotate_degree]만큼 회전하고 [consecutive_num]개 연결된 좌표 리스트와 side 좌표를 반환
        * [rotate_degree] = 0: oooo

        ※ 흑, 백이 구분된 게임보드를 반환하는 `get_random_consecutive_yx_board`와 혼동 주의
        '''

        #inner function=============
        def get_origin_consecutive_yx_list(consecutive_num: int, rotate_degree: int):
            '''
            *(0, 0)을 기준으로 연속된 좌표 리스트를 반환
            '''
            if rotate_degree in (0, 90):
                seq_yx_list = [[0, x] for x in range(-1, consecutive_num+1)]
            
            if rotate_degree == 90:
                seq_yx_list = Util.rotate_yx_list(
                    yx_list=seq_yx_list, rotate_degree=rotate_degree, origin_yx=(0, 0)
                )

            if rotate_degree == 45:
                seq_yx_list = [[loc, loc] for loc in range(-1, consecutive_num+1)]

            if rotate_degree == 135:
                seq_yx_list = [[consecutive_num-loc-1, loc] for loc in range(-1, consecutive_num+1)]
            
            side_yx_list = list(seq_yx_list.pop(pop_idx) for pop_idx in (0, -1))   #양 끝 yx 추출
            return seq_yx_list, side_yx_list

        def get_limit_loc(seq_yx_list, board_size: int):
                '''
                * 게임 보드에서 sequance YX 필터가 이동 가능한 최대 Y, X 좌표를 반환
                '''
                height, width =  np.max(seq_yx_list, axis=0)
                y_limit = board_size - height - 1  #이동 가능한 최대 x 좌표
                x_limit = board_size - width - 1   #이동 가능한 최대 y 좌표
                return y_limit, x_limit

        def is_out_loc(yx, board_size: int):
                '''
                * [yx] 좌표가 게임 보드 내에 위치 하였는지 boolean 형태로 반환
                * True: 게임 보드 외부에 위치
                * False: 게임 보드 내부에 위치
                '''
                for loc in yx:
                    if loc < 0: return True;
                    if loc >= board_size: return True;
                return False
        #End========================

        side_yx_list = list()
        while len(side_yx_list) < limit_side_num:
            seq_yx_list, side_yx_list = get_origin_consecutive_yx_list(
                consecutive_num=consecutive_num, rotate_degree=rotate_degree
            )

            y_limit, x_limit = get_limit_loc(   #이동 가능한 최대 yx 좌표
                seq_yx_list=seq_yx_list, board_size=self.board_size
            )
        
            move_yx = (np.random.randint(0, y_limit + 1), np.random.randint(0, x_limit + 1))  #이동 좌표 무작위 선택

            #seq 필터 및 사이드 yx 좌표 이동하기
            seq_yx_list = np.add(seq_yx_list, move_yx).tolist()
            side_yx_list = np.add(side_yx_list, move_yx).tolist()
            
            #유효 좌표 필터링 및 yx 좌표 튜플 변환
            seq_yx_list = list(tuple(yx) for yx in seq_yx_list)
            side_yx_list = list(    #보드에 위치한 yx만 추출
                tuple(yx) for yx in side_yx_list if not is_out_loc(yx, board_size=self.board_size)
            )
        return seq_yx_list, side_yx_list

    def get_random_consecutive_yx_board(
            self,
            consecutive_yx_list,
            side_yx_list,
            main_color,
            noise_rate,
            main_is_last,
            noise_sequence_limit
        ):
            '''
            * [rotate_degree]만큼 회전한 [main_color]의 돌이 [sequence_num]개 연결된 yx 좌표 집합
            * [main_is_last] 여부에 따라 [main_color]가 마지막 착수가 된다.
            * 최소 [limit_side_num]개 만큼 연속된 돌의 양 쪽에 빈 공간을 확보한다.
            * [noise_sequence_limit]개의 연속된 돌이 되는 위치는 착수하지 않는다
            '''

            #inner function=============
            def get_able_move_yx_list(board_size, disable_yx_list=[], shuffle=False):
                '''
                * 보드에서 불가능한 좌표인 [disable_yx_list]의 좌표들을 제외한 가능한 yx 좌표 리스트를 반환
                '''
                able_move_yx_list = list ()
                for y in range(board_size):
                    for x in range(board_size):
                        yx = (y, x)
                        if not yx in disable_yx_list:
                            able_move_yx_list.append(yx)
                if shuffle:
                    np.random.shuffle(able_move_yx_list)   #착수 가능 좌표 섞기
                return able_move_yx_list
            
            def noise_rate_to_num(noise_rate: float, board_size:int, disable_num: int=0):
                '''
                * [noise_rate]에 해당하는 noise 돌의 수를 반환
                * [disable_num]은 사전에 예약된 수로, 이를 제외하고 noise 돌 수를 계산
                '''
                if noise_rate == 0:
                    return 0

                noise_num = board_size ** 2
                noise_num -= disable_num
                noise_num = round(noise_num * noise_rate)
                noise_num -= noise_num % 2    #노이즈 돌 개수는 반드시 짝수여야함
                return noise_num
            #End========================
            seq_yx_list = consecutive_yx_list.copy()   #pop 과정이 있으므로 원본 유지를 위해 복사

            yx_board = list()

            #착수 가능한 yx 좌표 리스트
            able_yx_list = get_able_move_yx_list(
                disable_yx_list=seq_yx_list + side_yx_list,
                board_size=self.board_size,
                shuffle=True
            )

            #main_color에 따른 흑, 백 플레이어 좌표 리스트 할당하기
            black_yx_list, white_yx_list = self.distribe_player(
                main_color=main_color, alpha_player=seq_yx_list, beta_player=able_yx_list
            )

            #basic rule 착수하기
            while seq_yx_list:  #seq_yx_list의 yx를 소진할때 까지 반복
                current_turn = Util.get_current_color(yx_board)  #현재 플레이어 돌 색 얻기
                current_yx_list = self.return_current_player(  #현재 플레이어 yx_list 반환
                    current_turn=current_turn,
                    black=black_yx_list,
                    white=white_yx_list
                )
                move_yx = current_yx_list.pop() #좌표 yx 추출

                #적의 수가 착수 가능한지 확인 필요   
                if current_turn != main_color:
                    concat_yx_board = yx_board.copy()
                    concat_yx_board.append(move_yx)

                    is_consecutive = Util.check_consecutive_is_N(   #3개 이상 연속될 경우 continue
                        yx_board=concat_yx_board, origin_yx=move_yx, N=noise_sequence_limit
                    )
                    if is_consecutive:
                        continue
                
                yx_board.append(move_yx)

            noise_num = noise_rate_to_num(  #[noise_rate]에 따른 noise 돌 수
                noise_rate=noise_rate,
                disable_num=len(yx_board + side_yx_list),   #사전에 예약된 수(move)
                board_size=self.board_size
            )

            if not main_is_last:    #요구되는 마지막 수가 [main_color]일 경우
                noise_num += 1

            #noise stone 착수하기
            noise_stone_num = 0
            while noise_stone_num < noise_num:
                move_yx = able_yx_list.pop()

                #착수 가능 수인지 확인 필요
                is_consecutive = Util.check_consecutive_is_N(   #[NOISE_SEQ_LIMIT]개 이상 연속될 경우 continue
                    yx_board=concat_yx_board, origin_yx=move_yx, N=noise_sequence_limit
                )
                if not is_consecutive:
                    yx_board.append(move_yx)
                    noise_stone_num += 1
            return yx_board

    def attack_four(self, noise_rate: float, size: int):
        '''
        현재 플레이어 돌이 막히지 않고 4개 연속 이어져있음, 
        5개가 되는 위치에 각각 0.5 할당, 
        z = 1
        '''

        if noise_rate < 0 or 0.8 < noise_rate:  #[noise_rate] 제한 0 ~ 0.8
            raise Exception(f'[noise_rate] must be 0 ~ 0.8')

        SEQUENCE_NUM = 4
        LIMIT_SIDE_NUM = 1  #최소 side space
        NOISE_SEQ_LIMIT = 3 #노이즈 수의 연속 개수 제한
        MAIN_IS_LAST = False  #마지막 착수 플레이어 돌의 색이 [main_color]과 동일한지 여부
        
        main_color = np.random.randint(0, 2) #흑: 0, 백: 1
        rot_degree = np.random.choice((0, 45, 90, 135))

        consecutive_yx_list, side_yx_list = self.get_consecutive_yx_list(
            consecutive_num=SEQUENCE_NUM,
            rotate_degree=rot_degree,
            limit_side_num=LIMIT_SIDE_NUM
        )

        args = {
            'consecutive_yx_list': consecutive_yx_list,
            'side_yx_list': side_yx_list,
            'main_color': main_color,
            'noise_rate': noise_rate,
            'main_is_last': MAIN_IS_LAST,
            'noise_sequence_limit': NOISE_SEQ_LIMIT
        }
        
        yx_board = self.get_random_consecutive_yx_board(**args)
        state = Util.yx_board_to_state(yx_board=yx_board, main_color=main_color, board_size=self.board_size)

        policy_per_move = 1. / len(side_yx_list)
        

        import matplotlib.pyplot as plt
        print(yx_board)
        print(consecutive_yx_list)
        print(side_yx_list)
        plt.imshow(state)
        plt.show()
        


    def defend_four(self, noise_rate, size):
        pass

    def attack_three(self, noise_rate, size):
        pass

    def defend_three(self, noise_rate, size):
        pass

    def attack_space_three(self, noise_rate, size):
        pass

    def defend_space_three(self, noise_rate, size):
        pass
    



if __name__ == '__main__':
    gen = Generator(board_size=15)
    gen.attack_four(noise_rate=0.5, size=10)

    #현재 플레이어 돌이 막히지 않고 4개 연속 이어져있음. 5개가 되는 위치에 각각 0.5 할당. 승률 1
    # print(gen.generate_live_4_attack(1).get_sample(1.))
    

    #적 플레이어 돌이 막히지 않고 4개 연속 이어져있음. 5개가 되는 위치에 각각 0.5 할당. 승률 -1
    # obs, color, last_move, pi, z = gen.generate_live_4_defend(1).get_sample(1.)
    # print(obs, color, last_move, np.array(pi).reshape(15, 15), z)


    #현재 플레이어 돌이 막히지 않고 3개 연속 이어져있음. 4개가 되는 위치에 각각 0.5 할당. 승률 1
    # obs, color, last_move, pi, z = gen.generate_live_3_ooo_attack(1).get_sample(1.)
    # print(obs, end='\n\n')
    # print(np.array(pi).reshape(15, 15), end='\n\n')
    # print(color, end='\n\n')
    # print(last_move, end='\n\n')
    # print(z, end='\n\n')


    #적 플레이어 돌이 막히지 않고 3개 연속 이어져있음. 4개가 되는 위치에 각각 0.5 할당. 승률 0
    # obs, color, last_move, pi, z = gen.generate_live_3_ooo_defend(1).get_sample(1.)
    # print(obs, end='\n\n')
    # print(np.array(pi).reshape(15, 15), end='\n\n')
    # print(color, end='\n\n')
    # print(last_move, end='\n\n')
    # print(z, end='\n\n')
   
    #현재 플레이어 돌이 00_0 형태로 되어있음. 4개가 되는 위치에 각각 1 할당. 승률 1
    # obs, color, last_move, pi, z = gen.generate_live_3_oo_o_attack(1).get_sample(1.)
    # print(obs, end='\n\n')
    # print(np.array(pi).reshape(15, 15), end='\n\n')
    # print(color, end='\n\n')
    # print(last_move, end='\n\n')
    # print(z, end='\n\n')

    #적 플레이어 돌이 00_0 형태로 되어있음. 비어있는 중앙 0.5, 양쪽 0.25 할당. 승률 0
    # obs, color, last_move, pi, z = gen.generate_live_3_oo_o_defend(1).get_sample(1.)
    # print(obs, end='\n\n')
    # print(np.array(pi).reshape(15, 15), end='\n\n')
    # print(color, end='\n\n')
    # print(last_move, end='\n\n')
    # print(z, end='\n\n')