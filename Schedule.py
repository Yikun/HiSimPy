# -*- coding: utf-8 -*-
class Schedule:
    def __init__(self, hm_num):
        self.hm_real_ofdms = [[0 for hm_id in range(hm_num)], [0 for hm_id in range(hm_num)]]
        
    def schedule_handle(self, hm_num, ofdms_need_schedule, hm_data_queue_ofdm):
        return self.schedule_average(hm_num, ofdms_need_schedule, hm_data_queue_ofdm)
        
    def schedule_average(self, hm_num, ofdms_need_schedule, hm_data_queue_ofdm):
        # 1.最简单的平均分配调度
        #   1.1 带宽资源充足时
        #       - 直接分配
        #   1.2 带宽资源不足时
        #       - 不同HM的分配策略：根据grant_band_ofdm按比例分配
        #       - 同HM上、下行分配策略：1：1分配
        #
        ofdm_sum = sum(hm_data_queue_ofdm[0]) + sum(hm_data_queue_ofdm[1])

        if ofdms_need_schedule >= ofdm_sum :
            # 带宽资源充足时，可分配的ofdm数大于当前的队列，则可以直接分配
            print "Resource is more"
            for hm_id in range(hm_num):
                self.hm_real_ofdms[0][hm_id] = hm_data_queue_ofdm[0][hm_id]
                self.hm_real_ofdms[1][hm_id] = hm_data_queue_ofdm[1][hm_id]
        else :
            # 带宽资源不充足时，可分配的ofdm数小于当前的队列，平均分配
            print "Resource is not more"
            for hm_id in range(hm_num):
                self.hm_real_ofdms[0][hm_id] = (float) (ofdms_need_schedule * hm_data_queue_ofdm[0][hm_id] / ofdm_sum)
                self.hm_real_ofdms[1][hm_id] = (float) (ofdms_need_schedule * hm_data_queue_ofdm[1][hm_id] / ofdm_sum)
            #print "hm_real_ofdms[0|1]|[hm_id]: %s" % self.hm_real_ofdms
        print "Up count: %d, Down count: %d, All count: %d / %d" \
        % (sum(self.hm_real_ofdms[0]), sum(self.hm_real_ofdms[1]), sum(self.hm_real_ofdms[0])+sum(self.hm_real_ofdms[1]), ofdms_need_schedule)
        
        return self.hm_real_ofdms