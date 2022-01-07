import socket
import struct
import json
import os

download_dir = r'F:\PycharmProjects\06_名片管理\文件上传下载\client\download'


def get(phone, cmds):
    # 以写的方式打开一个新文件，接受服务端发来的文件的内容，写入客户的新文件
    # 先拿到报头的长度
    header = phone.recv(4)
    print('1')
    header_size = struct.unpack('i', header)[0]
    # 再收报头
    header_bytes = phone.recv(header_size)
    # 从报头中解析出对真实数据的描述信息
    header_json = header_bytes.decode('utf-8')
    header_dic = json.loads(header_json)
    total_size = header_dic['file_size']
    filename = header_dic['filename']
    # 接受真实的数据
    with open('%s/%s' % (download_dir, filename), 'wb') as f:
        recv_size = 0

        while recv_size < total_size:
            line = phone.recv(1024)
            f.write(line)
            recv_size += len(line)
            print('总大小：%s   已下载:%.2f%%' % (total_size, recv_size / total_size * 100))


def put(phone, cmds):
    filename = cmds[1]
    header_dic = {
        'filename': filename,
        'md5': 'xxdxxx',
        'file_size': os.path.getsize(r'%s/%s' % (download_dir, filename))
    }
    header_json = json.dumps(header_dic)
    header_bytes = header_json.encode('utf-8')
    # 发送报头的长度
    phone.send(struct.pack('i', len(header_bytes)))
    # 发送报头
    phone.send(header_bytes)
    # 再发送真实的数据
    with open('%s/%s' % (download_dir, filename), 'rb') as f:
        # conn.send(f.read())
        for line in f:
            phone.send(line)


def run():
    # 基于网络通信，TCP协议
    phone = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 发起链接,一种套接字
    phone.connect(('127.0.0.1', 8080))
    # 收发消息,strip删除开头和结尾的字符
    # 通信循环
    while True:
        # 发命令
        inp = input('>> ').strip()
        if not inp:
            continue
        phone.send(inp.encode('utf-8'))

        cmds = inp.split()
        if cmds[0] == 'get':
            get(phone, cmds)
        elif cmds[0] == 'put':
            put(phone, cmds)
    # 关闭
    phone.close()


if __name__ == '__main__':
    run()

