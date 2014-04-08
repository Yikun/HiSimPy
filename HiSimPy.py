# -*- coding: utf-8 -*-

import random
import copy
import matplotlib.pyplot as plt
import Monitor

class HiSimpy:
    def __init__(self):
        """
        Initialize all arguments
        """
        self.monitor = Monitor.Monitor()
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
        # 由于QAM及data_queue可能产生变化，所以需要更新ofdm数
        for hm_id in range(self.HM_NUM):
            self.hm_data_queue_ofdm[0][hm_id] = self.hm_data_queue[0][hm_id] / (self.hm_current_qam[0][hm_id] * 1920)
            self.hm_data_queue_ofdm[1][hm_id] = self.hm_data_queue[1][hm_id] / (self.hm_current_qam[1][hm_id] * 1920)

    def schedule_ofdm(self):
        #print "Schedule ofdm..."
        self.schedule_time += 1
        print "==========================%d times schdule===========================" % self.schedule_time
        # 1.最简单的平均分配调度
        #   1.1 带宽资源充足时
        #       - 直接分配
        #   1.2 带宽资源不足时
        #       - 不同HM的分配策略：根据grant_band_ofdm按比例分配
        #       - 同HM上、下行分配策略：1：1分配
        #
        ofdm_sum = sum(self.hm_data_queue_ofdm[0]) + sum(self.hm_data_queue_ofdm[1])

        if self.ofdms_need_schedule_per_times >= ofdm_sum :
            # 带宽资源充足时，可分配的ofdm数大于当前的队列，则可以直接分配
            print "Resource is more"
            for hm_id in range(self.HM_NUM):
                self.hm_real_ofdms[0][hm_id] = self.hm_data_queue_ofdm[0][hm_id]
                self.hm_real_ofdms[1][hm_id] = self.hm_data_queue_ofdm[1][hm_id]
        else :
            # 带宽资源不充足时，可分配的ofdm数小于当前的队列，平均分配
            print "Resource is not more"
            for hm_id in range(self.HM_NUM):
                self.hm_real_ofdms[0][hm_id] = (float) (self.ofdms_need_schedule_per_times * self.hm_data_queue_ofdm[0][hm_id] / ofdm_sum)
                self.hm_real_ofdms[1][hm_id] = (float) (self.ofdms_need_schedule_per_times * self.hm_data_queue_ofdm[1][hm_id] / ofdm_sum)
            #print "hm_real_ofdms[0|1]|[hm_id]: %s" % self.hm_real_ofdms
        print "Up count: %d, Down count: %d, All count: %d / %d" \
        % (sum(self.hm_real_ofdms[0]), sum(self.hm_real_ofdms[1]), sum(self.hm_real_ofdms[0])+sum(self.hm_real_ofdms[1]), self.ofdms_need_schedule_per_times)

    def simu_transport(self):
        for hm_id in range(self.HM_NUM):
            # 用分配的ofdms数*载波数*qam就是实际传输的bits数
            self.hm_real_bits[0][hm_id] =  self.hm_real_ofdms[0][hm_id] * self.hm_current_qam[0][hm_id] * 1920
            self.hm_real_bits[1][hm_id] =  self.hm_real_ofdms[1][hm_id] * self.hm_current_qam[0][hm_id] * 1920
            self.hm_data_queue[0][hm_id] -= self.hm_real_bits[0][hm_id]
            self.hm_data_queue[1][hm_id] -= self.hm_real_bits[1][hm_id]

    def simu_CBR_business(self):
        for hm_id in range(self.HM_NUM):
            self.hm_cbr_business[0][hm_id] = random.randrange(1920*2, 1920*12, 1920*2) * random.randint(0, 1)
            self.hm_cbr_business[1][hm_id] = random.randrange(1920*2, 1920*12, 1920*2) * random.randint(0, 1)
            self.hm_data_queue[0][hm_id] += self.hm_cbr_business[0][hm_id]# 10bit / 0.008s = 1250bit/s
            self.hm_data_queue[1][hm_id] += self.hm_cbr_business[1][hm_id]

    def run(self, schedule_count):
        print "Running..."
        for times in range(schedule_count):
            #产生CBR流，并入队
            self.simu_CBR_business()
            #更新队列ofdm数
            self.update_data_queue_ofdm()
            #记录当前队列情况
            self.monitor.m_hm_data_queue.append(copy.deepcopy(self.hm_data_queue))
            #分配ofdm
            self.schedule_ofdm()
            #记录当前ofdm分配情况
            self.monitor.m_hm_real_ofdm.append(copy.deepcopy(self.hm_real_ofdms))
            #模拟数据出队入队
            self.simu_transport()
            #self.print_arg()
            self.monitor.m_hm_real_bit.append(copy.deepcopy(self.hm_real_bits))

if __name__ == '__main__':
    print "Hinoc Simulation Running:"
    hs = HiSimpy()
    hs.run(100)
    data_queue_plot = [hs.monitor.m_hm_data_queue[scheduletime][0][0] for scheduletime in range(hs.schedule_time)]
    real_bit_plot = [ hs.monitor.m_hm_real_bit[scheduletime][0][0] for scheduletime in range(hs.schedule_time)]

    plot1=plt.plot(data_queue_plot, 'r')#蓝色 数据队列
    plot2=plt.plot(real_bit_plot, 'g')#绿色 实际分配

    #plt.legend([plot1, plot2], ('HM Buffer','ofdm dba'), 'best')
    plt.show()
