# -*- coding: utf-8 -*-
import random

class SimuArg:
    
    def __init__(self):
        self.HM_NUM= 1
        # 每个HM的保证带宽hm_grant_band[hm_id(0...63)]
        self.hm_grant_band = [ random.choice([1, 2, 4, 10]) for hmid in range(self.HM_NUM) ]
        # 每个HM的当前调制格式hm_current_qam [hm_id(0...63)][0(下行)|1(上行)],
        # 取值为2, 4, 6 ,...,12
        self.hm_current_qam = [ [random.randrange(2, 12, 2) for hm_id in range(self.HM_NUM)], [random.randrange(2, 12, 2) for hm_id in range(self.HM_NUM)] ]
        # 每个ofdm所含子载波数
        self.carrier_per_ofdm = 1920
        # 达到保证带宽所需要的ofdm符号数 grant_band_ofdm[hm_id][0|1]
        self.grant_band_ofdm = [ [0 for hm_id in range(self.HM_NUM)], [0 for hm_id in range(self.HM_NUM)] ]
        for hm_id in range(self.HM_NUM):
        # 利用公式
        # 保证带宽所对应的ofmd数 = (保证带宽(mbps)*1000000) / (当前的调制格式 * 子载波总数)
        # (注：调制格式即为每个子载波能承载的bit数)
            self.grant_band_ofdm[0][hm_id] = \
                (self.hm_grant_band[hm_id] * 1000000) \
                / (self.hm_current_qam[0][hm_id] * self.carrier_per_ofdm)
            self.grant_band_ofdm[1][hm_id] = \
                (self.hm_grant_band[hm_id] * 1000000) \
                / (self.hm_current_qam[1][hm_id] * self.carrier_per_ofdm)
        #存储规划次数
        self.schedule_time = 0
        #每个map周期可分配的ofdm数
        self.ofdms_need_schedule_per_map = 146 - 1 - 1 - 3 - 7
        #一次调度可分配map周期数
        self.ofdms_schedule_map_count = 4
        #一次调度分配的ofdms总数 = 每个map周期可分配的ofdm数 * 一次调度可分配map周期数
        self.ofdms_need_schedule_per_times = self.ofdms_schedule_map_count * self.ofdms_need_schedule_per_map
        self.hm_cbr_business = [[0 for hm_id in range(self.HM_NUM)], [0 for hm_id in range(self.HM_NUM)]]
        #每个hm的数据队列
        self.hm_data_queue = [[0 for hm_id in range(self.HM_NUM)], [0 for hm_id in range(self.HM_NUM)]]
        self.hm_data_queue_ofdm = [ [0 for hm_id in range(self.HM_NUM)], [0 for hm_id in range(self.HM_NUM)]]
        #每次调度，实际分配的ofdm结果
        self.hm_real_ofdms = [[0 for hm_id in range(self.HM_NUM)], [0 for hm_id in range(self.HM_NUM)]]
        self.hm_real_bits   = [[0 for hm_id in range(self.HM_NUM)], [0 for hm_id in range(self.HM_NUM)]]
        
    def print_arg(self):
        #打印所有参数
        print "    carrier_per_ofdm: %s" % self.carrier_per_ofdm
        #print "    hm_grant_band[self.HM_NUM]: %s " % self.hm_grant_band
        print "    调度分配的ofdm情况：hm_real_ofdms[0|1]|[hm_id]:      %s" % self.hm_real_ofdms
        print "    当前的QAM情况：hm_current_qam[0|1][self.HM_NUM]:     %s" % self.hm_current_qam
        print "    达到保证带宽需要的ofdm：grant_band_ofdm[0|1][hm_id]: %s" % self.grant_band_ofdm
        print "    (新)当前各HM的队列情况：hm_data_queue[0|1][hm_id]:   %s" % self.hm_data_queue
        print "    当前新产生的业务情况：hm_cbr_bussiness[0|1][hm_id]   %s" % self.hm_cbr_business
        
    def update_data_queue_ofdm(self):
        """ 由于QAM及data_queue可能产生变化，所以需要更新ofdm数
        """
        for hm_id in range(self.HM_NUM):
            self.hm_data_queue_ofdm[0][hm_id] = self.hm_data_queue[0][hm_id] / (self.hm_current_qam[0][hm_id] * self.carrier_per_ofdm)
            self.hm_data_queue_ofdm[1][hm_id] = self.hm_data_queue[1][hm_id] / (self.hm_current_qam[1][hm_id] * self.carrier_per_ofdm)