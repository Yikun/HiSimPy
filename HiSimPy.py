# -*- coding: utf-8 -*-
import random
import copy
import matplotlib.pyplot as plt
# import matplotlib
import Monitor
import SimuArg
import Schedule

class HiSimpy:
    def __init__(self):
        """
        Initialize all arguments
        """
        self.monitor = Monitor.Monitor()
        self.simuarg = SimuArg.SimuArg()
        self.schedule = Schedule.Schedule(self.simuarg.HM_NUM)
        
    def update_data_queue_ofdm(self):
        # 由于QAM及data_queue可能产生变化，所以需要更新ofdm数
        self.simuarg.update_data_queue_ofdm()

    def call_schedule(self):
        self.simuarg.schedule_time += 1
        print "==========================%d times schdule===========================" % self.simuarg.schedule_time
        self.simuarg.hm_real_ofdms = self.schedule.schedule_handle(self.simuarg.HM_NUM, self.simuarg.ofdms_need_schedule_per_times, self.simuarg.hm_data_queue_ofdm)
    
    # TODO:后期将队列管理隔离为一个类
    def simu_transport(self):
        for hm_id in range(self.simuarg.HM_NUM):
            # 用分配的ofdms数*载波数*qam就是实际传输的bits数
            self.simuarg.hm_real_bits[0][hm_id] =  self.simuarg.hm_real_ofdms[0][hm_id] * self.simuarg.hm_current_qam[0][hm_id] * 1920
            self.simuarg.hm_real_bits[1][hm_id] =  self.simuarg.hm_real_ofdms[1][hm_id] * self.simuarg.hm_current_qam[0][hm_id] * 1920
            #TODO: 队列管理有问题
            self.simuarg.hm_data_queue[0][hm_id] -= self.simuarg.hm_real_bits[0][hm_id]
            self.simuarg.hm_data_queue[1][hm_id] -= self.simuarg.hm_real_bits[1][hm_id]
            if self.simuarg.hm_data_queue[0][hm_id] < 0:
                self.simuarg.hm_data_queue[0][hm_id] = 0
            if self.simuarg.hm_data_queue[1][hm_id] < 0:
                self.simuarg.hm_data_queue[1][hm_id] = 0
    
    def simu_CBR_business(self):
    # TODO:后期将业务源隔离为一个类
        for hm_id in range(self.simuarg.HM_NUM):
            self.simuarg.hm_cbr_business[0][hm_id] = 1920*12#random.randrange(1920*2, 1920*12, 1920*2) * random.randint(0, 1)
            self.simuarg.hm_cbr_business[1][hm_id] = 1920*12#random.randrange(1920*2, 1920*12, 1920*2) * random.randint(0, 1)
            self.simuarg.hm_data_queue[0][hm_id] += self.simuarg.hm_cbr_business[0][hm_id]# 10bit / 0.008s = 1250bit/s
            self.simuarg.hm_data_queue[1][hm_id] += self.simuarg.hm_cbr_business[1][hm_id]

    def run(self, schedule_count):
        print "Running..."
        for times in range(schedule_count):
            #产生CBR流，并入队
            self.simu_CBR_business()
            self.monitor.m_hm_business.append(copy.deepcopy(self.simuarg.hm_cbr_business))
            #根据当前的QAM情况，更新实时的队列ofdm数
            self.update_data_queue_ofdm()
            #记录当前队列情况
            self.monitor.m_hm_data_queue.append(copy.deepcopy(self.simuarg.hm_data_queue))
            #分配ofdm
            self.call_schedule()
            #记录当前ofdm分配情况
            self.monitor.m_hm_real_ofdm.append(copy.deepcopy(self.simuarg.hm_real_ofdms))
            #模拟数据出队入队
            self.simu_transport()
            #self.simuatg.print_arg()
            self.monitor.m_hm_real_bit.append(copy.deepcopy(self.simuarg.hm_real_bits))
            self.monitor.m_hm_data_queue_undo.append(copy.deepcopy(self.simuarg.hm_data_queue))

if __name__ == '__main__':
    print "Hinoc Simulation Running:"
    hs = HiSimpy()
    hs.run(20)
    data_queue_plot      = [ hs.monitor.m_hm_data_queue[scheduletime][0][0]      for scheduletime in range(hs.simuarg.schedule_time)]
    real_bit_plot        = [ hs.monitor.m_hm_real_bit[scheduletime][0][0]        for scheduletime in range(hs.simuarg.schedule_time)]
    data_queue_undo_plot = [ hs.monitor.m_hm_data_queue_undo[scheduletime][0][0] for scheduletime in range(hs.simuarg.schedule_time)]
    business_plot        = [ hs.monitor.m_hm_business[scheduletime][0][0]        for scheduletime in range(hs.simuarg.schedule_time)]
    
    plot1=plt.plot(data_queue_plot, '-or', label="<1> Buffer before Schedule")#红色 调度前
    plot2=plt.plot(real_bit_plot, '-og', label="<2> Actual schedule")#绿色 实际分配
    plot3=plt.plot(data_queue_undo_plot, '-ob', label="<3> Buffer after Schedule = ")#蓝色 调度后剩余队列
    plot4=plt.plot(business_plot, '-oy', label="<4> Bussiness ")#黄色 调度前新业务
    #pre<3>+<4>=<1>   <1> = <2> + <3>
    plt.legend(loc="upper right")
    # 红色 - 绿色 = 蓝色
    plt.show()
