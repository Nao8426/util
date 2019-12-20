# ファイルを走査してパスをcsvに書き出すプログラム
import csv
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class Organize():
    # mode=0 : パスをそのままcsv出力する．
    # mode=1 : ディレクトリ，ファイルの階層ごとに分けてcsv出力を行う．
    def listup(self, dirname, mode=0):
        filelist = []
        for root, dirs, files in os.walk(dirname):
            for f in files:
                if mode == 0:
                    filelist.append([os.path.join(root, f)])
                elif mode == 1:
                    filelist.append(os.path.join(root, f).split('\\'))

        return filelist


    def save(self, filelist, out_path):
        if os.path.exists(out_path):
            while 1:
                check = input('同じ名前のファイルが存在しますが上書きしますか？(y/n) : ')
                if check == 'y':
                    break
                elif check == 'n':
                    exit()
                else:
                    print('不正な入力です．もう一度入力して下さい．')

        with open(out_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(filelist)
            print('\"{}\" を作成しました．'.format(out_path))


if __name__ == '__main__':
    organize = Organize()
    filelist = organize.listup('dir', 0)
    organize.save(filelist, 'filelist.csv')
