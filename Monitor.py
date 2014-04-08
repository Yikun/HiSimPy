# -*- coding: utf-8 -*-
class Monitor:

    def __init__(self):
        # 每次调度后，各HM中队列BUFFER, 用于监测每次调度后HM的队列情况
        # m_hm_datat_queue[scheduletimes][0|1][hm_id]
        self.m_hm_data_queue = []#[ [[0 for hm_id in range(self.HM_NUM)], [0 for hm_id in range(self.HM_NUM)]] ]
        # 每次调度后，各HM分配到的ofdm资源, 用于监测每次调度后HM的资源利用情况
        # m_hm_real_ofdm[scheduletimes][0|1][hm_id]
        self.m_hm_real_ofdm  = []#[ [[0 for hm_id in range(self.HM_NUM)], [0 for hm_id in range(self.HM_NUM)]] ]
        # 每次调度后，各HM实际传输的bit数
        self.m_hm_real_bit   = []
        # 每次调度，各HM实际的QAM情况
        self.m_hm_qam        = []
