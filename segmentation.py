import os
import random
from functools import cmp_to_key

os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin'

SEGMENT_TABLE_SIZE = 16  # 段表寄存器大小
segment_table = []  # 段表寄存器
MAX_SEGMENT_INDEX = 32  # 段号最大长度
MAX_SEGMENT_INNER = 32  # 每个段最大长度
MAX_RAM_SIZE = 128  # 内存大小
memory_table = []
job_list = []


def set_conf(a, b, c, d):
    global MAX_RAM_SIZE, MAX_SEGMENT_INDEX, SEGMENT_TABLE_SIZE, MAX_SEGMENT_INNER
    MAX_RAM_SIZE = a
    SEGMENT_TABLE_SIZE = b
    MAX_SEGMENT_INDEX = c
    MAX_SEGMENT_INNER = d


def func(x, y):
    if x.分区号 > y.分区号:
        return 1
    elif x.分区号 == y.分区号:
        return 0
    else:
        return -1


def func2(x, y):
    if x.分区号 > y.分区号:
        return 1
    elif x.分区号 == y.分区号:
        return 0
    else:
        return -1


class JCB:
    def __init__(self, name, segment_num, segment_size=[], random_segment_size=1):
        self.名称 = name
        self.段表 = []
        is_apply, self.段表编号 = apply_space(1, segment_num)
        if is_apply:  # 如果段表寄存器未满
            for i in range(segment_num):
                if random_segment_size:  # 随机段长度
                    self.段表.append(Segment(index=i, size=random.randint(1, MAX_SEGMENT_INNER),
                                           ex_address=random.randint(100000, 262144)))
                else:
                    self.段表.append(Segment(index=i, size=segment_size[i],
                                           ex_address=random.randint(100000, 262144)))
        # self.apply_memory(0)

    def apply_segment(self, s, w):  # 段号S 段内位移d
        if s >= len(self.段表):
            return "请求段号大于最大段号"
        if w > self.段表[s].大小 * 1000:
            return "请求段内偏移量大于段长"
        if not self.段表[s].是否被装入内存:
            return "请求的地址未放入内存中"
        return "请求的物理地址为:" + str(self.段表[s].内存地址 * 1000 + w)

    def release_segment(self, index):
        if not self.段表[index].是否被装入内存:
            return "请求的程序段未被装入内存"
        for i in range(len(memory_table)):
            if memory_table[i].地址 == self.段表[index].内存地址:
                del memory_table[i]
                self.段表[index].内存地址 = "null"
                self.段表[index].是否被装入内存 = 0
                return "释放程序段成功！"

    def apply(self, index):
        now = 0
        i = 0
        while now < MAX_RAM_SIZE and i < len(memory_table):  # 寻找空闲空间插入程序段
            if now + self.段表[index].大小 < memory_table[i].地址:
                memory_table.append(
                    MemoryTable(now, self.段表[index].大小, self.名称 + ":分段" + str(index)))
                self.段表[index].内存地址 = now
                self.段表[index].是否被装入内存 = 1
                memory_table.sort(key=cmp_to_key(func))
                return "装入成功"
            else:
                now = memory_table[i].地址 + memory_table[i].大小
                i += 1
        if now + self.段表[index].大小 < MAX_RAM_SIZE:
            memory_table.append(
                MemoryTable(now, self.段表[index].大小, self.名称 + ":分段" + str(index)))
            self.段表[index].内存地址 = now
            self.段表[index].是否被装入内存 = 1
            memory_table.sort(key=cmp_to_key(func))
            return "装入成功"
        return 0

    def apply_memory(self, index, remove=0):
        now = 0
        i = 0
        if self.段表[index].是否被装入内存:
            return "请求的内存段已被装入内存"
        if len(memory_table) == 0:
            memory_table.append(
                MemoryTable(now, self.段表[index].大小, self.名称 + ":分段" + str(index)))
            self.段表[index].内存地址 = now
            self.段表[index].是否被装入内存 = 1
            memory_table.sort(key=cmp_to_key(func))

            return "装入成功"
        else:
            a = self.apply(index)
            if a:
                return a
            # 空闲内存已满，移动内存
            now = 0
            for i in range(len(memory_table)):
                is_move = 0
                if now < memory_table[i].地址:
                    for job in job_list:  # 修改JCB中的内存地址
                        if is_move:  # 如果已经被移动过
                            break
                        for ad in job.段表:
                            if ad.内存地址 == memory_table[i].地址:
                                ad.内存地址 = now
                                memory_table[i].地址 = now
                                is_move = 1
                                break
                now = memory_table[i].地址 + memory_table[i].大小
            # 重新执行装入算法
            now = 0
            i = 0
            a = self.apply(index)
            if a:
                return a
            if not remove:
                return "内存空间已满！"

            # 紧凑内存，将最近未使用的段调出
            tmp_memory_table = memory_table
            tmp_memory_table.sort(key=cmp_to_key(func2))
            i = 0
            while len(memory_table) and i < len(tmp_memory_table):
                for j in range(len(memory_table)):
                    if memory_table[j].地址 == tmp_memory_table[i].地址:
                        is_move = 0
                        for job in job_list:  # 修改JCB中的内存地址
                            if is_move == 1:
                                break
                            for ad in job.段表:
                                if ad.内存地址 == memory_table[j].地址:
                                    ad.内存地址 = 0
                                    ad.是否被装入内存 = 0
                                    is_move = 1
                                break
                        del memory_table[j]
                        i += 1
                        break
                a = self.apply(index)
                if a:
                    return a
        return "请求的程序段过大，请重试！"


class Segment:  # 段表
    def __init__(self, index, size, ex_address, is_paged=0, ram_address="null"):
        self.内存地址 = ram_address  # 内存中起始地址
        self.段号 = index  # 段号
        self.大小 = size  # 段长
        self.是否被装入内存 = is_paged  # 是否被装入内存
        self.外存地址 = ex_address  # 外存中起始地址


class SegmentTable:  # 段表寄存器
    def __init__(self, address, size):
        self.地址 = address  # 段表在内存中的始址
        self.大小 = size  # 段表长度


class MemoryTable:  # 内存分区表
    def __init__(self, address, size, name):
        self.地址 = address
        self.大小 = size
        self.名称 = name
        self.分区号 = len(memory_table)


def apply_space(address, size):
    if len(segment_table) == SEGMENT_TABLE_SIZE:
        return 0, -1
    segment_table.append(SegmentTable(address, size))
    return 1, len(segment_table) - 1


def memory_display():
    now = 0
    res = {}
    for i in range(len(memory_table)):
        if now < memory_table[i].地址:
            res[str(now) + "K-" + str(memory_table[i].地址 - 1) + "K"] = "NULL"
        res[str(memory_table[i].地址) + "K-" +
            str(memory_table[i].地址 + memory_table[i].大小 - 1) + "K"] = memory_table[i].名称
        now = memory_table[i].地址 + memory_table[i].大小
    if now < MAX_RAM_SIZE:
        res[str(now) + "K-" + str(MAX_RAM_SIZE) + "K"] = "NULL"
    return res


def rel_job(index=-1):
    global job_list
    if index == -1:
        job_list = []
        return "释放所有进程成功"
    else:
        try:
            del job_list[index]
            "释放进程成功"
        except:
            return "请求释放的进程不在段表寄存器中"