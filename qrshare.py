#! /usr/bin/env python
# -*- coding: utf-8 -*-

from optparse import OptionParser
import Tkinter
import ImageTk
import threading
import BaseHTTPServer
import SimpleHTTPServer
import socket
import fcntl
import struct

import qrcode


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,
        struct.pack('256s', ifname[:15])
    )[20:24])


if __name__ == "__main__":

    p = OptionParser(description="QrShare",
                     prog="qrshare",
                     version="0.1",
                     usage="%prog [options] [file]")

    p.add_option("-p", "--port", dest="port",
                 help="Port to Share the File", default=8000)

    opts, args = p.parse_args()

    if len(args) == 1:

        f = args[0]
        url = ''
        try:
            url = 'http://' + get_ip_address('wlan0') + ':' + str(opts.port) + '/'
        except:
            print "Error : need wifi up"
            exit()

        def handler_quit():
            httpd.shutdown()
            root.quit()

        print "Get the file on " + url + f
        print "to finish close the QRCode or Ctrl+C"

        try:
            httpd = BaseHTTPServer.HTTPServer(("", opts.port), SimpleHTTPServer.SimpleHTTPRequestHandler)
            thread_httpd = threading.Thread(target=httpd.serve_forever)
            thread_httpd.setdaemon = True
            thread_httpd.start()
        except:
            handler_quit()

        root = Tkinter.Tk()
        root.protocol("WM_DELETE_WINDOW", handler_quit)
        root.resizable(0, 0)
        root.geometry('+%d+%d' % (100, 100))

        image = qrcode.make(url + f)

        root.title('QRShare')
        root.geometry('%dx%d' % (image.size[0], image.size[1]))

        tkpi = ImageTk.PhotoImage(image)
        label_image = Tkinter.Label(root, image=tkpi, text="Hello, world!")
        label_image.place(x=0, y=0, width=image.size[0], height=image.size[1])

        try:
            root.mainloop()
        except KeyboardInterrupt:
            httpd.shutdown()
            root.quit()

    else:
        p.print_help()