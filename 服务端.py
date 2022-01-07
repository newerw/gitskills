import socket
import struct
import json
import os

share_dir = r'F:\PycharmProjects\06_名片管理\文件上传下载\server\share'


def get(conn, cmds):
    filename = cmds[1]
    # 以读的方式打开文件，读取文件内容发送给客户端
    # 制作固定长度的报头
    header_dic = {
        'filename': filename,
        'md5': 'xxdxxx',
        'file_size': os.path.getsize(r'%s/%s' % (share_dir, filename))
    }
    header_json = json.dumps(header_dic)
    header_bytes = header_json.encode('utf-8')
    # 发送报头的长度
    conn.send(struct.pack('i', len(header_bytes)))
    # 发送报头
    conn.send(header_bytes)
    # 再发送真实的数据
    with open('%s/%s' % (share_dir, filename), 'rb') as f:
        # conn.send(f.read())
        for line in f:
            conn.send(line)


def input(conn, cmds):
    header = conn.recv(4)
    print('1')
    header_size = struct.unpack('i', header)[0]
    # 再收报头
    header_bytes = conn.recv(header_size)
    # 从报头中解析出对真实数据的描述信息
    header_json = header_bytes.decode('utf-8')
    header_dic = json.loads(header_json)
    total_size = header_dic['file_size']
    filename = header_dic['filename']
    # 接受真实的数据
    with open('%s/%s' % (share_dir, filename), 'wb') as f:
        recv_size = 0

        while recv_size < total_size:
            line = conn.recv(1024)
            f.write(line)
            recv_size += len(line)
            print('总大小：%s   已下载:%.2f%%' % (total_size, recv_size / total_size * 100))


def run():
    # 基于网络通信，TCP协议
    phone = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 解决端口占用
    phone.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 绑定 端口0-65535，0-1024给操作系统使用
    phone.bind(('127.0.0.1', 8080))

    # 最大挂起的链接数
    phone.listen(5)
    # 等待链接
    # res = phone.accept(),两种套接字，phone，conn
    print('starting.....')
    # 链接循环
    while True:
        conn, client_addr = phone.accept()
        print(client_addr)
        # 收发消息，接受数据的最大数 单位：bytes
        while True:
            try:
                # 收命令
                res = conn.recv(1024)
                # 使用Linux系统
                if not res:
                    break
                print('客户端的数据', res)
                # 解析命令，提取相应命令参数，解析成['get', 'a.txt']格式
                cmds = res.decode('utf-8').split()
                if cmds[0] == 'get':
                    get(conn, cmds)
                elif cmds[0] == 'put':
                    input(conn, cmds)
            except ConnectionResetError:
                break
            # 挂断
            # conn.close()
    # 关机
    phone.close()


if __name__ == '__main__':
    run()
