from subprocess import check_call
import sys
from lolviz import *
from PIL import Image
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QMessageBox
from cv2 import imread

from segmentation import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('gui.ui', self)
        self.setWindowIcon(QIcon('ninja.ico'))
        self.setWindowTitle('分段管理系统')
        self.add_job_btn.clicked.connect(self.add_job)
        self.job_combo.currentIndexChanged.connect(self.change_job)
        self.job_combo_2.currentIndexChanged.connect(self.draw_job)
        self.req_seg_btn.clicked.connect(self.apply_seg)
        self.chg_set_btn.clicked.connect(self.chg_set)
        self.rel_seg_btn.clicked.connect(self.rel_seg)
        self.view_address_btn.clicked.connect(self.view_address)
        self.rel_job_btn.clicked.connect(self.rel_job)
        self.rel_job_all_btn.clicked.connect(self.rel_job_all)
        self.draw_memory()
        self.show()

    def rel_job(self):
        QMessageBox.information(self,
                                "信息",
                                rel_job(self.job_combo.currentIndex()),
                                QMessageBox.Yes | QMessageBox.No)

    def rel_job_all(self):
        QMessageBox.information(self,
                                "信息",
                                rel_job(),
                                QMessageBox.Yes | QMessageBox.No)

    def rel_seg(self):
        if not len(job_list):
            return
        QMessageBox.information(self,
                                "信息",
                                job_list[self.job_combo.currentIndex()].release_segment(
                                    self.seg_combo.currentIndex()),
                                QMessageBox.Yes | QMessageBox.No)
        self.job_combo_2.setCurrentIndex(self.job_combo.currentIndex())
        self.draw_memory()
        self.draw_job()

    def chg_set(self):
        set_conf(int(self.memory_size_line.text())
                 , int(self.seg_size_line.text())
                 , int(self.seginx_line.text())
                 , int(self.segsize_line.text()))
        self.draw_memory()

    def view_address(self):
        if not len(job_list):
            QMessageBox.information(self,
                                    "信息",
                                    "请先装入进程",
                                    QMessageBox.Yes | QMessageBox.No)
            return
        try:
            QMessageBox.information(self,
                                    "信息",
                                    job_list[self.job_combo.currentIndex()].apply_segment(
                                        int(self.s_line.text()), int(self.d_line.text())
                                    ),
                                    QMessageBox.Yes)
        except:
            QMessageBox.information(self,  # 使用infomation信息框
                                    "信息",
                                    "输入错误",
                                    QMessageBox.Yes | QMessageBox.No)

    def apply_seg(self):
        if not len(job_list):
            return
        print(int(self.eliminate.isChecked()))
        QMessageBox.information(self,
                                "信息",
                                job_list[self.job_combo.currentIndex()].apply_memory(
                                    self.seg_combo.currentIndex(), int(self.eliminate.isChecked())),
                                QMessageBox.Yes | QMessageBox.No)

        self.job_combo_2.setCurrentIndex(self.job_combo.currentIndex())
        self.draw_memory()
        self.draw_job()

    def change_job(self):
        self.seg_combo.clear()
        job = job_list[self.job_combo.currentIndex()]
        for i in range(len(job.段表)):
            self.seg_combo.addItem(self.tr(str(job.段表[i].段号)))

    def draw_job(self):
        if not len(job_list):
            return
        objviz(job_list[self.job_combo_2.currentIndex()]).save('job.dot')
        check_call(['dot', '-Tpng', 'job.dot', '-o', 'job.png'])
        pixmap = Image.fromarray(imread('job.png')).toqpixmap()
        scene = QGraphicsScene(0, 0, pixmap.width(), pixmap.height())
        scene.addPixmap(pixmap)
        self.job_view.setScene(scene)

    def add_job(self):

        job_list.append(JCB(self.job_name.text(), int(self.job_seg_num.text())))
        self.job_combo.addItem(self.tr(job_list[len(job_list) - 1].名称))
        self.job_combo_2.addItem(self.tr(job_list[len(job_list) - 1].名称))
        self.job_combo.setCurrentIndex(len(job_list) - 1)
        self.job_combo_2.setCurrentIndex(len(job_list) - 1)
        self.job_name.setText(self.tr("进程" + str(len(job_list) + 1)))

    def draw_memory(self):
        objviz(memory_display()).save('memory.dot')
        check_call(['dot', '-Tpng', 'memory.dot', '-o', 'memory.png'])
        pixmap = Image.fromarray(imread('memory.png')).toqpixmap()
        scene = QGraphicsScene(0, 0, pixmap.width(), pixmap.height())
        scene.addPixmap(pixmap)
        self.memory_view.setScene(scene)


if __name__ == '__main__':
    os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin'
    app = QApplication(sys.argv)
    a = MainWindow()
    sys.exit(app.exec())
