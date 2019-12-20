import csv
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class Organize():
    def __init__(self, dirname):
        self.dirname = dirname


    def listup(self):
        filelist = []
        for root, dirs, files in os.walk(self.dirname):
            for f in files:
                filelist.append(os.path.join(root, f).split('\\')[1:])

        return filelist


    def main(self, out_path):
        filelist = self.listup()
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
    organize = Organize('./dir')
    organize.main('./filelist.csv')
